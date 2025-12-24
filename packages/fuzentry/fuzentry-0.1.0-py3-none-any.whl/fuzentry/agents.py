"""
Fuzentry Agents Module - AI Orchestration

AI agent invocation, chaining, and streaming responses.
"""

from typing import Dict, Any, List, Optional
from ..core import FuzentryClient


class AgentsClient:
    """
    AI Agents orchestration client
    
    Example:
        agents = AgentsClient(client)
        result = agents.invoke(
            message="Analyze contract",
            folders=[{"id": "folder-123", "name": "Legal"}]
        )
    """
    
    def __init__(self, client: FuzentryClient):
        self.client = client
    
    def invoke(
        self,
        message: str,
        folders: Optional[List[Dict]] = None,
        engine: str = "auto",
        synthesize: bool = True,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Invoke AI agent
        
        Args:
            message: User message/query
            folders: List of folder dicts with 'id' and 'name'
            engine: 'gedde', 'agentcore', or 'auto'
            synthesize: Enable response synthesis
            max_tokens: Max output tokens
            temperature: Sampling temperature (0-1)
            
        Returns:
            Execution result with response, tokens, latency
        """
        response = self.client.post('/agents/invoke', body={
            'message': message,
            'folders': folders or [],
            'options': {
                'engine': engine,
                'synthesize': synthesize,
                'maxTokens': max_tokens,
                'temperature': temperature
            }
        })
        return response['data']
    
    def chain(
        self,
        steps: List[Dict[str, Any]],
        share_context: bool = True
    ) -> Dict[str, Any]:
        """
        Execute multi-step agent chain
        
        Args:
            steps: List of step dicts with 'message', 'folders', 'options'
            share_context: Pass outputs between steps
            
        Returns:
            Chain results with all step outputs
        """
        response = self.client.post('/agents/chain', body={
            'steps': steps,
            'shareContext': share_context
        })
        return response['data']
    
    def get_execution_status(self, execution_id: str) -> Dict[str, Any]:
        """Get async execution status"""
        response = self.client.get(f'/executions/{execution_id}')
        return response['data']
