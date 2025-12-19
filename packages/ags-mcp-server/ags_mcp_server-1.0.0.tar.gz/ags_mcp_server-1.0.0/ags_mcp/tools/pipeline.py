"""Unstructured pipeline tools."""

import urllib.parse
from typing import Dict, Any

from ..client import AnzoAPIClient


def register_pipeline_tools(mcp, client: AnzoAPIClient):
    """Register all pipeline-related MCP tools."""
    
    @mcp.tool()
    def run_pipeline(pipeline_uri: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run an unstructured pipeline.
        
        Args:
            pipeline_uri: URI of the pipeline to run
            payload: Pipeline execution payload
            
        Returns:
            Pipeline execution result
        """
        encoded_uri = urllib.parse.quote(pipeline_uri, safe='')
        return client.post(f"/unstructured/{encoded_uri}/run", json=payload)
    
    @mcp.tool()
    def cancel_pipeline(pipeline_uri: str) -> Dict[str, Any]:
        """
        Cancel a running unstructured pipeline.
        
        Args:
            pipeline_uri: URI of the pipeline to cancel
            
        Returns:
            Cancellation result
        """
        encoded_uri = urllib.parse.quote(pipeline_uri, safe='')
        return client.post(f"/unstructured/{encoded_uri}/cancel")
    
    @mcp.tool()
    def retrieve_pipeline_status(pipeline_uri: str) -> Dict[str, Any]:
        """
        Get the status of an unstructured pipeline.
        
        Args:
            pipeline_uri: URI of the pipeline
            
        Returns:
            Pipeline status information
        """
        encoded_uri = urllib.parse.quote(pipeline_uri, safe='')
        return client.get(f"/unstructured/{encoded_uri}/status")
