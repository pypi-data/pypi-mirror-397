"""Graphmart management tools."""

import urllib.parse
from typing import Dict, Any, Optional
import structlog
import re

from ..client import AnzoAPIClient

logger = structlog.get_logger(__name__)

# URI validation pattern - basic check for valid URI characters
_URI_PATTERN = re.compile(r'^[a-zA-Z][a-zA-Z0-9+.-]*:[^\s]*$')

def _validate_uri(uri: str, param_name: str) -> str:
    """Validate and return URI, raise ValueError if invalid."""
    if not uri or not uri.strip():
        raise ValueError(f"{param_name} cannot be empty")
    uri = uri.strip()
    if not _URI_PATTERN.match(uri):
        raise ValueError(f"{param_name} must be a valid URI (e.g., http://example.com/resource)")
    return uri


def register_graphmart_tools(mcp, client: AnzoAPIClient):
    """Register all graphmart-related MCP tools."""
    
    @mcp.tool()
    def list_graphmarts(expand: Optional[str] = None) -> list:
        """
        List all graphmarts the user has permission to view.
        
        Args:
            expand: Optional expansion parameter (* for full details)
            
        Returns:
            List of graphmarts with their properties
        """
        params = {"expand": expand} if expand else {}
        result = client.get("/api/graphmarts", params=params)
        return result if isinstance(result, list) else [result]
    
    @mcp.tool()
    def get_graphmart_info(graphmart_uri: str, expand: Optional[str] = None) -> Dict[str, Any]:
        """
        Get detailed information about a specific graphmart.
        
        Args:
            graphmart_uri: URI of the graphmart
            expand: Optional expansion parameter
            
        Returns:
            Graphmart details including layers, configuration, etc.
        """
        graphmart_uri = _validate_uri(graphmart_uri, "graphmart_uri")
        encoded_uri = urllib.parse.quote(graphmart_uri, safe='')
        params = {"expand": expand} if expand else {}
        return client.get(f"/api/graphmarts/{encoded_uri}", params=params)
    
    @mcp.tool()
    def create_graphmart(graphmart_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new graphmart.
        
        Args:
            graphmart_config: Configuration for the new graphmart (must include 'title')
            
        Returns:
            Created graphmart details including URI
        """
        return client.post("/api/graphmarts", json=graphmart_config)
    
    @mcp.tool()
    def modify_graphmart(graphmart_uri: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update properties of an existing graphmart.
        
        Args:
            graphmart_uri: URI of the graphmart to modify
            updates: Properties to update
            
        Returns:
            Updated graphmart details
        """
        graphmart_uri = _validate_uri(graphmart_uri, "graphmart_uri")
        encoded_uri = urllib.parse.quote(graphmart_uri, safe='')
        return client.patch(f"/api/graphmarts/{encoded_uri}", json=updates)
    
    @mcp.tool()
    def delete_graphmart(graphmart_uri: str, force: bool = False) -> Dict[str, Any]:
        """
        Delete a graphmart including all layers, steps, and data.
        
        Args:
            graphmart_uri: URI of the graphmart to delete
            force: If true, skip confirmation and force deletion
            
        Returns:
            Deletion status
        """
        graphmart_uri = _validate_uri(graphmart_uri, "graphmart_uri")
        encoded_uri = urllib.parse.quote(graphmart_uri, safe='')
        params = {"force": str(force).lower()}
        return client.delete(f"/api/graphmarts/{encoded_uri}", params=params)
    
    @mcp.tool()
    def retrieve_graphmart_status(graphmart_uri: str, detail: bool = False) -> Dict[str, Any]:
        """
        Get the status of a graphmart (online, offline, activating, etc).
        
        Args:
            graphmart_uri: URI of the graphmart
            detail: If true, return detailed status including layer statuses
            
        Returns:
            Graphmart status information
        """
        graphmart_uri = _validate_uri(graphmart_uri, "graphmart_uri")
        encoded_uri = urllib.parse.quote(graphmart_uri, safe='')
        params = {"detail": str(detail).lower()}
        return client.get(f"/api/graphmarts/{encoded_uri}/status", params=params)
    
    @mcp.tool()
    def activate_graphmart(graphmart_uri: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Activate a graphmart asynchronously.
        
        Args:
            graphmart_uri: URI of the graphmart to activate
            config: Optional activation configuration
            
        Returns:
            Activation result
        """
        graphmart_uri = _validate_uri(graphmart_uri, "graphmart_uri")
        encoded_uri = urllib.parse.quote(graphmart_uri, safe='')
        return client.post(
            f"/api/graphmarts/{encoded_uri}/activate",
            json=config or {}
        )
    
    @mcp.tool()
    def deactivate_graphmart(graphmart_uri: str) -> Dict[str, Any]:
        """
        Deactivate a graphmart asynchronously.
        
        Args:
            graphmart_uri: URI of the graphmart to deactivate
            
        Returns:
            Deactivation result
        """
        graphmart_uri = _validate_uri(graphmart_uri, "graphmart_uri")
        encoded_uri = urllib.parse.quote(graphmart_uri, safe='')
        return client.post(f"/api/graphmarts/{encoded_uri}/deactivate")
    
    @mcp.tool()
    def refresh_graphmart(graphmart_uri: str) -> Dict[str, Any]:
        """
        Refresh a graphmart (reload only changed/dirty layers).
        
        Args:
            graphmart_uri: URI of the graphmart to refresh
            
        Returns:
            Refresh result
        """
        graphmart_uri = _validate_uri(graphmart_uri, "graphmart_uri")
        encoded_uri = urllib.parse.quote(graphmart_uri, safe='')
        return client.post(f"/api/graphmarts/{encoded_uri}/refresh")
    
    @mcp.tool()
    def reload_graphmart(graphmart_uri: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Reload a graphmart (unload and reload all layers).
        
        Args:
            graphmart_uri: URI of the graphmart to reload
            config: Optional reload configuration
            
        Returns:
            Reload result
        """
        graphmart_uri = _validate_uri(graphmart_uri, "graphmart_uri")
        encoded_uri = urllib.parse.quote(graphmart_uri, safe='')
        return client.post(
            f"/api/graphmarts/{encoded_uri}/reload",
            json=config or {}
        )
    
    @mcp.tool()
    def retrieve_graphmart_layers(graphmart_uri: str, expand: Optional[str] = None) -> list:
        """
        List all layers in a graphmart.
        
        Args:
            graphmart_uri: URI of the graphmart
            expand: Optional expansion parameter
            
        Returns:
            List of layers in the graphmart
        """
        graphmart_uri = _validate_uri(graphmart_uri, "graphmart_uri")
        encoded_uri = urllib.parse.quote(graphmart_uri, safe='')
        params = {"expand": expand} if expand else {}
        result = client.get(f"/api/graphmarts/{encoded_uri}/layers", params=params)
        return result if isinstance(result, list) else [result]
    
    @mcp.tool()
    def create_graphmart_layer(graphmart_uri: str, layer_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a new layer to a graphmart.
        
        Args:
            graphmart_uri: URI of the graphmart
            layer_config: Configuration for the new layer
            
        Returns:
            Created layer details
        """
        graphmart_uri = _validate_uri(graphmart_uri, "graphmart_uri")
        encoded_uri = urllib.parse.quote(graphmart_uri, safe='')
        return client.post(
            f"/api/graphmarts/{encoded_uri}/layers",
            json=layer_config
        )
    
    @mcp.tool()
    def delete_graphmart_layer(graphmart_uri: str, layer_uri: str) -> Dict[str, Any]:
        """
        Delete a layer from a graphmart.
        
        Args:
            graphmart_uri: URI of the graphmart
            layer_uri: URI of the layer to delete
            
        Returns:
            Deletion status
        """
        graphmart_uri = _validate_uri(graphmart_uri, "graphmart_uri")
        layer_uri = _validate_uri(layer_uri, "layer_uri")
        encoded_gm = urllib.parse.quote(graphmart_uri, safe='')
        encoded_layer = urllib.parse.quote(layer_uri, safe='')
        return client.delete(
            f"/api/graphmarts/{encoded_gm}/layers/{encoded_layer}"
        )
    
    @mcp.tool()
    def move_graphmart_layer(
        graphmart_uri: str,
        layer_uri: str,
        after: Optional[str] = None,
        before: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Move a layer to a different position in the graphmart.
        
        Args:
            graphmart_uri: URI of the graphmart
            layer_uri: URI of the layer to move
            after: URI of layer to move after (mutually exclusive with before)
            before: URI of layer to move before (mutually exclusive with after)
            
        Returns:
            Move operation result
        """
        graphmart_uri = _validate_uri(graphmart_uri, "graphmart_uri")
        layer_uri = _validate_uri(layer_uri, "layer_uri")
        encoded_gm = urllib.parse.quote(graphmart_uri, safe='')
        encoded_layer = urllib.parse.quote(layer_uri, safe='')
        
        params = {}
        if after:
            params["after"] = after
        if before:
            params["before"] = before
        
        return client.post(
            f"/api/graphmarts/{encoded_gm}/layers/{encoded_layer}/move",
            params=params
        )
