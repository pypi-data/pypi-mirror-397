# -*- coding: utf-8 -*-
"""
Database connection and queries for Motion MCP Server.
Uses asyncpg for PostgreSQL with pgvector support.
"""
import json
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager

import asyncpg
from pgvector.asyncpg import register_vector

from .config import config
from .embedding import embedding_service


class MotionDB:
    """
    Database service for motion retrieval.
    """
    
    def __init__(self):
        self._pool: Optional[asyncpg.Pool] = None
    
    async def get_pool(self) -> asyncpg.Pool:
        """Get or create connection pool."""
        if self._pool is None:
            self._pool = await asyncpg.create_pool(
                host=config.POSTGRES_HOST,
                port=config.POSTGRES_PORT,
                user=config.POSTGRES_USER,
                password=config.POSTGRES_PASSWORD,
                database=config.POSTGRES_DB,
                ssl="require",  # Neon requires SSL
                min_size=1,
                max_size=5,
                init=self._init_connection
            )
        return self._pool
    
    async def _init_connection(self, conn):
        """Initialize connection with vector support."""
        await register_vector(conn)
    
    async def close(self):
        """Close connection pool."""
        if self._pool:
            await self._pool.close()
            self._pool = None
    
    @asynccontextmanager
    async def connection(self):
        """Get a connection from the pool."""
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            yield conn
    
    async def search_motions(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search motions by text similarity using vector search.
        
        Args:
            query: Search query text
            top_k: Number of results to return
            
        Returns:
            List of matching motions with similarity scores
        """
        # Get query embedding
        query_embedding = embedding_service.get_embedding(query)
        if query_embedding is None:
            return []
        
        async with self.connection() as conn:
            # Vector similarity search using cosine distance
            # pgvector: <=> is cosine distance (1 - cosine_similarity)
            rows = await conn.fetch(
                """
                SELECT 
                    id,
                    name,
                    description,
                    total_frames,
                    fps,
                    1 - (name_embedding <=> $1::vector) as similarity
                FROM motions
                WHERE name_embedding IS NOT NULL
                ORDER BY name_embedding <=> $1::vector
                LIMIT $2
                """,
                query_embedding,
                top_k
            )
            
            return [
                {
                    "id": str(row["id"]),
                    "name": row["name"],
                    "description": row["description"] or "",
                    "total_frames": row["total_frames"],
                    "fps": row["fps"],
                    "duration_seconds": row["total_frames"] / row["fps"] if row["fps"] > 0 else 0,
                    "similarity": float(row["similarity"])
                }
                for row in rows
            ]
    
    async def get_motion_by_id(
        self,
        motion_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get motion metadata by ID."""
        async with self.connection() as conn:
            row = await conn.fetchrow(
                """
                SELECT id, name, description, total_frames, fps, source_file
                FROM motions
                WHERE id = $1::uuid
                """,
                motion_id
            )
            
            if row is None:
                return None
            
            return {
                "id": str(row["id"]),
                "name": row["name"],
                "description": row["description"] or "",
                "total_frames": row["total_frames"],
                "fps": row["fps"],
                "source_file": row["source_file"]
            }
    
    async def get_frames(
        self,
        motion_id: str,
        start_frame: Optional[int] = None,
        end_frame: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get bone frames for a motion.
        
        Args:
            motion_id: Motion UUID
            start_frame: Start frame index (inclusive)
            end_frame: End frame index (inclusive)
            
        Returns:
            List of frame data with bone_data JSONB
        """
        async with self.connection() as conn:
            # Build query with optional frame range
            query = """
                SELECT frame_index, bone_data
                FROM bone_frames
                WHERE motion_id = $1::uuid
            """
            params = [motion_id]
            
            if start_frame is not None:
                query += f" AND frame_index >= ${len(params) + 1}"
                params.append(start_frame)
            
            if end_frame is not None:
                query += f" AND frame_index <= ${len(params) + 1}"
                params.append(end_frame)
            
            query += " ORDER BY frame_index"
            
            rows = await conn.fetch(query, *params)
            
            return [
                {
                    "frame_index": row["frame_index"],
                    "bone_data": row["bone_data"]  # Already dict from JSONB
                }
                for row in rows
            ]
    
    def frame_to_vpd(
        self,
        bone_data: Dict[str, Any],
        model_name: str = "Model"
    ) -> str:
        """
        Convert frame bone data to VPD text format.
        
        VPD Format:
        Vocaloid Pose Data file
        <model_name>;
        <bone_count>;
        Bone0{<bone_name>
          <trans_x>,<trans_y>,<trans_z>;
          <quat_x>,<quat_y>,<quat_z>,<quat_w>;
        }
        ...
        """
        lines = [
            "Vocaloid Pose Data file",
            "",
            f"{model_name};",
            f"{len(bone_data)};",
            ""
        ]
        
        for idx, (bone_name, data) in enumerate(bone_data.items()):
            trans = data.get("trans", [0.0, 0.0, 0.0])
            quat = data.get("quat", [0.0, 0.0, 0.0, 1.0])
            
            lines.append(f"Bone{idx}{{{bone_name}")
            lines.append(f"  {trans[0]:.6f},{trans[1]:.6f},{trans[2]:.6f};")
            lines.append(f"  {quat[0]:.6f},{quat[1]:.6f},{quat[2]:.6f},{quat[3]:.6f};")
            lines.append("}")
            lines.append("")
        
        return "\n".join(lines)


# Singleton instance
motion_db = MotionDB()
