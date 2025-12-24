"""
Fuzentry Prompts Module - Prompt Template Management
"""

from typing import Dict, Any, List, Optional
from ..core import FuzentryClient


class PromptsClient:
    """Prompt template management"""
    
    def __init__(self, client: FuzentryClient):
        self.client = client
    
    def save(
        self,
        name: str,
        template: str,
        folder_id: str,
        variables: Optional[Dict] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Save prompt template"""
        response = self.client.post('/prompts', body={
            'name': name,
            'template': template,
            'folderId': folder_id,
            'variables': variables or {},
            'tags': tags or []
        })
        return response['data']
    
    def get(self, prompt_id: str) -> Dict[str, Any]:
        """Get prompt by ID"""
        response = self.client.get(f'/prompts/{prompt_id}')
        return response['data']
    
    def render(self, prompt_id: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Render prompt with variables"""
        response = self.client.post(f'/prompts/{prompt_id}/render', body={'variables': variables})
        return response['data']
    
    def list(self, folder_id: str, tags: Optional[List[str]] = None) -> List[Dict]:
        """List prompts in folder"""
        params = f'?folderId={folder_id}'
        if tags:
            params += f'&tags={",".join(tags)}'
        response = self.client.get(f'/prompts{params}')
        return response['data']
