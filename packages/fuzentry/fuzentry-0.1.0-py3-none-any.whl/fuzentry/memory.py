"""
Fuzentry Memory Module - Vector Search & Semantic Memory

Store, search, and manage vector embeddings for semantic search.
"""

from typing import Dict, Any, List, Optional
from ..core import FuzentryClient


class MemoryClient:
    """
    Vector memory and semantic search client
    
    Example:
        memory = MemoryClient(client)
        memory.store(content="Q4 revenue was $2.5M", folder_id="folder-123")
        results = memory.search("revenue", folder_id="folder-123")
    """
    
    def __init__(self, client: FuzentryClient):
        self.client = client
    
    def store(
        self,
        content: str,
        folder_id: str,
        metadata: Optional[Dict] = None,
        tags: Optional[List[str]] = None,
        ttl_hours: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Store content as vector memory
        
        Args:
            content: Text content to vectorize
            folder_id: Folder ID for scoping
            metadata: Custom metadata dict
            tags: Tags for filtering
            ttl_hours: Auto-delete after N hours
            
        Returns:
            Memory ID and metadata
        """
        response = self.client.post('/memory', body={
            'content': content,
            'folderId': folder_id,
            'metadata': metadata or {},
            'tags': tags or [],
            'ttlHours': ttl_hours
        })
        return response['data']
    
    def search(
        self,
        query: str,
        folder_id: str,
        top_k: int = 10,
        min_score: float = 0.7,
        tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Semantic search across memories
        
        Args:
            query: Search query
            folder_id: Folder to search in
            top_k: Max results to return
            min_score: Min similarity score (0-1)
            tags: Filter by tags
            
        Returns:
            List of matching memories with scores
        """
        response = self.client.post('/memory/search', body={
            'query': query,
            'folderId': folder_id,
            'topK': top_k,
            'minScore': min_score,
            'tags': tags or []
        })
        return response['data']
    
    def get(self, memory_id: str) -> Dict[str, Any]:
        """Get memory by ID"""
        response = self.client.get(f'/memory/{memory_id}')
        return response['data']
    
    def delete(self, memory_id: str) -> Dict[str, Any]:
        """Delete memory by ID"""
        response = self.client.delete(f'/memory/{memory_id}')
        return response['data']
    
    def get_stats(self, folder_id: str) -> Dict[str, Any]:
        """Get folder memory statistics"""
        response = self.client.get(f'/memory/stats?folderId={folder_id}')
        return response['data']
