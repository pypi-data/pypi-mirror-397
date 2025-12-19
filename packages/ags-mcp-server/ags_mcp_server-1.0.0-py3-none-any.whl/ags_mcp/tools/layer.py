"""Layer management tools."""

import urllib.parse
from typing import Dict, Any, Optional

from ..client import AnzoAPIClient


def register_layer_tools(mcp, client: AnzoAPIClient):
    """Register all layer-related MCP tools."""
    
    @mcp.tool()
    def retrieve_layer(layer_uri: str, expand: Optional[str] = None) -> Dict[str, Any]:
        """
        Get detailed information about a specific layer.
        
        Args:
            layer_uri: URI of the layer
            expand: Optional expansion parameter
            
        Returns:
            Layer details including steps, views, and configuration
        """
        encoded_uri = urllib.parse.quote(layer_uri, safe='')
        params = {"expand": expand} if expand else {}
        return client.get(f"/api/layers/{encoded_uri}", params=params)
    
    @mcp.tool()
    def modify_layer(layer_uri: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update properties of an existing layer.
        
        Args:
            layer_uri: URI of the layer to modify
            updates: Properties to update
            
        Returns:
            Updated layer details
        """
        encoded_uri = urllib.parse.quote(layer_uri, safe='')
        return client.patch(f"/api/layers/{encoded_uri}", json=updates)
    
    @mcp.tool()
    def delete_layer(layer_uri: str) -> Dict[str, Any]:
        """
        Delete a layer including all steps and graph data.
        
        Args:
            layer_uri: URI of the layer to delete
            
        Returns:
            Deletion status
        """
        encoded_uri = urllib.parse.quote(layer_uri, safe='')
        return client.delete(f"/api/layers/{encoded_uri}")
    
    @mcp.tool()
    def retrieve_layer_status(layer_uri: str, detail: bool = False) -> Dict[str, Any]:
        """
        Get the status of a layer (loading, loaded, error, etc).
        
        Args:
            layer_uri: URI of the layer
            detail: If true, return detailed status information
            
        Returns:
            Layer status information
        """
        encoded_uri = urllib.parse.quote(layer_uri, safe='')
        params = {"detail": str(detail).lower()}
        return client.get(
            f"/api/layers/{encoded_uri}/status",
            params=params
        )
    
    @mcp.tool()
    def retrieve_layer_views(layer_uri: str, expand: Optional[str] = None) -> Dict[str, Any]:
        """
        List all views in a layer.
        
        Args:
            layer_uri: URI of the layer
            expand: Optional expansion parameter
            
        Returns:
            List of views in the layer
        """
        encoded_uri = urllib.parse.quote(layer_uri, safe='')
        params = {"expand": expand} if expand else {}
        return client.get(
            f"/api/layers/{encoded_uri}/views",
            params=params
        )
    
    @mcp.tool()
    def create_layer_view(layer_uri: str, view_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a new view to a layer.
        
        Args:
            layer_uri: URI of the layer
            view_config: Configuration for the new view
            
        Returns:
            Created view details
        """
        encoded_uri = urllib.parse.quote(layer_uri, safe='')
        return client.post(
            f"/api/layers/{encoded_uri}/views",
            json=view_config
        )
    
    @mcp.tool()
    def refresh_layers(layer_uris: list) -> Dict[str, Any]:
        """
        Refresh specific layers asynchronously.
        
        Args:
            layer_uris: List of layer URIs to refresh
            
        Returns:
            Refresh operation result
        """
        return client.post(
            "/api/layers/refresh",
            params={"layers": layer_uris}
        )
