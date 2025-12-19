"""Ontology/model management tools."""

import urllib.parse
from typing import Dict, Any

from ..client import AnzoAPIClient


def register_ontology_tools(mcp, client: AnzoAPIClient):
    """Register all ontology-related MCP tools."""
    
    @mcp.tool()
    def retrieve_models() -> list:
        """
        List all ontology models in AGS.
        
        Returns:
            List of model URIs
        """
        result = client.get("/api/models")
        return result if isinstance(result, list) else [result]
    
    @mcp.tool()
    def upload_model(model_file_path: str) -> Dict[str, Any]:
        """
        Upload an ontology file to AGS.
        
        Args:
            model_file_path: Path to the ontology file (TTL, RDF, etc.)
            
        Returns:
            Upload result with model URI
        """
        with open(model_file_path, 'rb') as f:
            files = {'modelData': f}
            return client.post("/api/models", files=files)
    
    @mcp.tool()
    def download_model(model_uri: str, format: str = "trig") -> Dict[str, Any]:
        """
        Download an ontology model in specified RDF format.
        
        Args:
            model_uri: URI of the model to download
            format: RDF format (trig, ttl, rdf, nt, etc.)
            
        Returns:
            Model content in specified format
        """
        encoded_uri = urllib.parse.quote(model_uri, safe='')
        params = {"format": format}
        return client.get(
            f"/api/models/{encoded_uri}",
            params=params
        )
    
    @mcp.tool()
    def delete_model(model_uri: str) -> Dict[str, Any]:
        """
        Delete an ontology model from AGS.
        
        Args:
            model_uri: URI of the model to delete
            
        Returns:
            Deletion status
        """
        encoded_uri = urllib.parse.quote(model_uri, safe='')
        return client.delete(f"/api/models/{encoded_uri}")
