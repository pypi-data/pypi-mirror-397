"""
Fuzentry Auth Module - Authentication & Session Management
"""

from typing import Dict, Any
from ..core import FuzentryClient


class AuthClient:
    """Authentication client"""
    
    def __init__(self, client: FuzentryClient):
        self.client = client
    
    def validate_api_key(self) -> Dict[str, Any]:
        """Validate current API key"""
        response = self.client.get('/auth/validate')
        return response['data']
    
    def create_session(self, ttl_hours: int = 1) -> Dict[str, Any]:
        """Create session token from API key"""
        response = self.client.post('/auth/session', body={'ttlHours': ttl_hours})
        return response['data']
    
    def get_tenant_metadata(self) -> Dict[str, Any]:
        """Get tenant metadata"""
        response = self.client.get('/auth/tenant')
        return response['data']
