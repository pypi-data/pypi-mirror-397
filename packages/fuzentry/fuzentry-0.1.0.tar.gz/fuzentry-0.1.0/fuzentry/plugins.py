"""
Fuzentry Plugins Module - MCP Tools & OAuth Integrations
"""

from typing import Dict, Any, List
from ..core import FuzentryClient


class PluginsClient:
    """MCP tools and OAuth integrations"""
    
    def __init__(self, client: FuzentryClient):
        self.client = client
    
    def register(self, tool_definition: Dict[str, Any]) -> Dict[str, Any]:
        """Register MCP tool"""
        response = self.client.post('/plugins', body=tool_definition)
        return response['data']
    
    def invoke(self, tool_id: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke MCP tool"""
        response = self.client.post(f'/plugins/{tool_id}/invoke', body={'arguments': arguments})
        return response['data']
    
    def list(self) -> List[Dict]:
        """List registered tools"""
        response = self.client.get('/plugins')
        return response['data']
    
    # OAuth methods
    def get_oauth_url(self, provider: str, redirect_uri: str, scopes: List[str]) -> str:
        """Get OAuth authorization URL"""
        response = self.client.post('/connectors/oauth/authorize', body={
            'provider': provider,
            'redirectUri': redirect_uri,
            'scopes': scopes
        })
        return response['data']['authUrl']
    
    def handle_oauth_callback(self, provider: str, code: str) -> Dict[str, Any]:
        """Handle OAuth callback"""
        response = self.client.post(f'/connectors/oauth/{provider}/callback', body={'code': code})
        return response['data']
    
    def get_oauth_status(self, provider: str) -> Dict[str, Any]:
        """Get OAuth connection status"""
        response = self.client.get(f'/connectors/oauth/{provider}/status')
        return response['data']
