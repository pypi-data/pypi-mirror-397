"""Dataset management tools."""

import urllib.parse
from typing import Dict, Any, Optional

from ..client import AnzoAPIClient


def register_dataset_tools(mcp, client: AnzoAPIClient):
    """Register all dataset-related MCP tools."""
    
    @mcp.tool()
    def list_datasets(expand: Optional[str] = None) -> list:
        """
        List all datasets the user has permission to view.
        
        Args:
            expand: Optional expansion parameter
            
        Returns:
            List of datasets with their properties
        """
        params = {"expand": expand} if expand else {}
        result = client.get("/api/datasets", params=params)
        return result if isinstance(result, list) else [result]
    
    @mcp.tool()
    def get_dataset_info(dataset_uri: str, expand: Optional[str] = None) -> Dict[str, Any]:
        """
        Get detailed information about a specific dataset.
        
        Args:
            dataset_uri: URI of the dataset
            expand: Optional expansion parameter
            
        Returns:
            Dataset details including editions, components, etc.
        """
        encoded_uri = urllib.parse.quote(dataset_uri, safe='')
        params = {"expand": expand} if expand else {}
        return client.get(f"/api/datasets/{encoded_uri}", params=params)
    
    @mcp.tool()
    def create_empty_dataset(dataset_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an empty dataset at the specified location.
        
        Args:
            dataset_config: Configuration for the new dataset
            
        Returns:
            Created dataset details
        """
        return client.post("/api/datasets/empty", json=dataset_config)
    
    @mcp.tool()
    def modify_dataset(dataset_uri: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update properties of an existing dataset.
        
        Args:
            dataset_uri: URI of the dataset to modify
            updates: Properties to update
            
        Returns:
            Updated dataset details
        """
        encoded_uri = urllib.parse.quote(dataset_uri, safe='')
        return client.patch(f"/api/datasets/{encoded_uri}", json=updates)
    
    @mcp.tool()
    def delete_dataset(dataset_uri: str, force: bool = False) -> Dict[str, Any]:
        """
        Delete a dataset and its associated editions and components.
        
        Args:
            dataset_uri: URI of the dataset to delete
            force: If true, skip confirmation and force deletion
            
        Returns:
            Deletion status
        """
        encoded_uri = urllib.parse.quote(dataset_uri, safe='')
        params = {"force": str(force).lower()}
        return client.delete(f"/api/datasets/{encoded_uri}", params=params)
    
    @mcp.tool()
    def retrieve_acls(object_uri: str) -> Dict[str, Any]:
        """
        Get the ACLs (access control lists) for an object.
        
        Args:
            object_uri: URI of the object
            
        Returns:
            ACL details including inherited and explicit permissions
        """
        encoded_uri = urllib.parse.quote(object_uri, safe='')
        return client.get(f"/api/acls/{encoded_uri}")
    
    @mcp.tool()
    def set_acls(acl_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Set/replace ACLs for an object.
        
        Args:
            acl_config: ACL configuration
            
        Returns:
            ACL update result
        """
        return client.post("/api/acls/set", json=acl_config)
    
    @mcp.tool()
    def modify_acls(acl_modifications: Dict[str, Any]) -> Dict[str, Any]:
        """
        Modify ACLs by adding or removing ACL statements.
        
        Args:
            acl_modifications: ACL modifications to apply
            
        Returns:
            ACL modification result
        """
        return client.post("/api/acls/edit", json=acl_modifications)
