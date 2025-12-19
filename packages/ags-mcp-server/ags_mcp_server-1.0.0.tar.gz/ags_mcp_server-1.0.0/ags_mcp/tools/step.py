"""Step management tools."""

import urllib.parse
from typing import Dict, Any, Optional

from ..client import AnzoAPIClient


def register_step_tools(mcp, client: AnzoAPIClient):
    """Register all step-related MCP tools."""
    
    @mcp.tool()
    def retrieve_layer_steps(layer_uri: str, expand: Optional[str] = None) -> list:
        """
        List all steps in a layer.
        
        Args:
            layer_uri: URI of the layer
            expand: Optional expansion parameter (* for full details)
            
        Returns:
            List of steps with their configurations
        """
        encoded_uri = urllib.parse.quote(layer_uri, safe='')
        params = {"expand": expand} if expand else {}
        result = client.get(
            f"/api/layers/{encoded_uri}/steps",
            params=params
        )
        return result if isinstance(result, list) else [result]
    
    @mcp.tool()
    def retrieve_step(step_uri: str, expand: Optional[str] = None) -> Dict[str, Any]:
        """
        Get detailed information about a specific step.
        
        Args:
            step_uri: URI of the step
            expand: Optional expansion parameter
            
        Returns:
            Step details including query, configuration, etc.
        """
        encoded_uri = urllib.parse.quote(step_uri, safe='')
        params = {"expand": expand} if expand else {}
        return client.get(f"/api/steps/{encoded_uri}", params=params)
    
    @mcp.tool()
    def create_layer_step(layer_uri: str, step_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a new step to a layer.
        
        Args:
            layer_uri: URI of the layer
            step_config: Configuration for the new step (must include 'title' and 'type')
            
        Returns:
            Created step details
        """
        encoded_uri = urllib.parse.quote(layer_uri, safe='')
        return client.post(
            f"/api/layers/{encoded_uri}/steps",
            json=step_config
        )
    
    @mcp.tool()
    def modify_step(step_uri: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update properties of an existing step (e.g., SPARQL query).
        
        Args:
            step_uri: URI of the step to modify
            updates: Properties to update
            
        Returns:
            Updated step details
        """
        encoded_uri = urllib.parse.quote(step_uri, safe='')
        return client.patch(f"/api/steps/{encoded_uri}", json=updates)
    
    @mcp.tool()
    def create_or_replace_layer_step(
        layer_uri: str,
        step_uri: str,
        step_config: Dict[str, Any],
        force: bool = False
    ) -> Dict[str, Any]:
        """
        Create a new step or replace an existing one with the specified URI.
        
        Args:
            layer_uri: URI of the layer
            step_uri: URI for the step
            step_config: Step configuration
            force: If true, replace existing step without confirmation
            
        Returns:
            Created/updated step details
        """
        encoded_layer = urllib.parse.quote(layer_uri, safe='')
        encoded_step = urllib.parse.quote(step_uri, safe='')
        params = {"force": str(force).lower()}
        
        return client.put(
            f"/api/layers/{encoded_layer}/steps/{encoded_step}",
            json=step_config,
            params=params
        )
    
    @mcp.tool()
    def delete_layer_step(layer_uri: str, step_uri: str) -> Dict[str, Any]:
        """
        Delete a step from a layer.
        
        Args:
            layer_uri: URI of the layer
            step_uri: URI of the step to delete
            
        Returns:
            Deletion status
        """
        encoded_layer = urllib.parse.quote(layer_uri, safe='')
        encoded_step = urllib.parse.quote(step_uri, safe='')
        return client.delete(
            f"/api/layers/{encoded_layer}/steps/{encoded_step}"
        )
    
    @mcp.tool()
    def delete_step(step_uri: str) -> Dict[str, Any]:
        """
        Delete a step including all graph data.
        
        Args:
            step_uri: URI of the step to delete
            
        Returns:
            Deletion status
        """
        encoded_uri = urllib.parse.quote(step_uri, safe='')
        return client.delete(f"/api/steps/{encoded_uri}")
    
    @mcp.tool()
    def retrieve_step_status(step_uri: str, detail: bool = False) -> Dict[str, Any]:
        """
        Get the status of a step (valid, invalid, error details).
        
        Args:
            step_uri: URI of the step
            detail: If true, return detailed status information
            
        Returns:
            Step status information including validation errors
        """
        encoded_uri = urllib.parse.quote(step_uri, safe='')
        params = {"detail": str(detail).lower()}
        return client.get(
            f"/api/steps/{encoded_uri}/status",
            params=params
        )
