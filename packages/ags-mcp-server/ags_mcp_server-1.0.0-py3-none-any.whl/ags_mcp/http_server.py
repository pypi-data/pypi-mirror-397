"""Anzo MCP Server - HTTP/SSE transport for Cursor IDE and web-based MCP clients.

This server uses HTTP with Server-Sent Events (SSE) for MCP protocol communication.
Cursor IDE requires this transport instead of stdio.

Usage:
    python anzo_mcp_http.py

Then configure Cursor with:
    "anzo-graphmart": {
      "transport": {
        "type": "sse",
        "url": "http://localhost:8000/sse"
      }
    }
"""

import os
import sys

# Set working directory to script location
_script_dir = os.path.dirname(os.path.abspath(__file__))
if _script_dir not in sys.path:
    sys.path.insert(0, _script_dir)
os.chdir(_script_dir)

import structlog
from mcp.server.fastmcp import FastMCP
from typing import Dict, Any

from ags_mcp.config import get_config
from ags_mcp.client import AnzoAPIClient
from ags_mcp.errors import AnzoAPIError
from ags_mcp.tools import (
    register_graphmart_tools,
    register_layer_tools,
    register_step_tools,
    register_ontology_tools,
    register_dataset_tools,
    register_pipeline_tools
)
from ags_mcp.prompts import register_prompts

# Singleton pyanzo client for connection reuse
_pyanzo_client = None
_pyanzo_lock = __import__('threading').Lock()

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer()
    ]
)

logger = structlog.get_logger(__name__)

# Initialize configuration and client
try:
    config = get_config()
    client = AnzoAPIClient(config)
    logger.info("anzo_client_initialized", base_url=config.http_base)
except Exception as e:
    logger.error("failed_to_initialize", error=str(e))
    sys.exit(1)

# Initialize MCP server with SSE transport
mcp = FastMCP("anzo_mcp_server")

# Register all MCP tools
register_graphmart_tools(mcp, client)
register_layer_tools(mcp, client)
register_step_tools(mcp, client)
register_ontology_tools(mcp, client)
register_dataset_tools(mcp, client)
register_pipeline_tools(mcp, client)
# Register prompts for agent guidance
register_prompts(mcp)


logger.info("mcp_tools_registered")

# Health check resource
@mcp.resource("health://status")
def health_check() -> str:
    """Health check endpoint for monitoring."""
    import json
    pyanzo_status = "available" if _get_pyanzo_client() is not None else "unavailable"
    return json.dumps({
        "status": "healthy",
        "server": "anzo_mcp_http",
        "tools_registered": len(mcp._tool_manager._tools),
        "pyanzo": pyanzo_status,
        "config": {
            "base_url": config.http_base,
            "port": config.port
        }
    })


def _get_pyanzo_client():
    """Get or create singleton pyanzo client (thread-safe)."""
    global _pyanzo_client
    if _pyanzo_client is None:
        with _pyanzo_lock:
            if _pyanzo_client is None:
                try:
                    from pyanzo import AnzoClient
                    # Extract domain properly from URL
                    from urllib.parse import urlparse
                    parsed = urlparse(config.http_base)
                    domain = parsed.hostname or config.http_base.replace("https://", "").replace("http://", "").split(':')[0]
                    port = parsed.port or config.port
                    
                    _pyanzo_client = AnzoClient(
                        domain=domain,
                        port=port,
                        username=config.username,
                        password=config.password
                    )
                    logger.info("pyanzo_client_initialized", domain=domain, port=port)
                except ImportError as e:
                    logger.error("pyanzo_not_available", error=str(e))
                    return None
                except Exception as e:
                    logger.error("pyanzo_init_failed", error=str(e))
                    return None
    return _pyanzo_client


# SPARQL query tool with pyanzo
@mcp.tool()
def execute_sparql_query(query: str, graphmart_uri: str = None) -> Dict[str, Any]:
    """
    Execute a SPARQL query against the Anzo database using pyanzo.
    
    Args:
        query: SPARQL query string (max 1MB)
        graphmart_uri: Optional graphmart URI to query against (defaults to ANZO_GRAPHMART_IRI from env)
        
    Returns:
        Query results as JSON with status, results, and row_count
    """
    # Input validation
    if not query or not query.strip():
        return {
            "status": "error",
            "error": "Query cannot be empty",
            "results": []
        }
    
    if len(query) > 1024 * 1024:  # 1MB limit
        return {
            "status": "error",
            "error": "Query exceeds maximum size of 1MB",
            "results": []
        }
    
    anzo_client = _get_pyanzo_client()
    if anzo_client is None:
        return {
            "status": "error",
            "error": "pyanzo library not installed or failed to initialize. Run: pip install pyanzo",
            "results": []
        }
    
    try:
        # Use provided graphmart or fall back to env config
        target_graphmart = graphmart_uri or config.graphmart_iri
        
        if not target_graphmart:
            return {
                "status": "error",
                "error": "No graphmart specified. Provide graphmart_uri parameter or set ANZO_GRAPHMART_IRI in .env",
                "results": []
            }
        
        # Execute query using singleton client
        results = anzo_client.query_graphmart(target_graphmart, query)
        
        # Convert results to list of dictionaries
        result_list = []
        if results:
            for row in results.as_table_results().as_record_dictionaries():
                result_list.append(row)
        
        logger.info("sparql_query_executed", rows=len(result_list), graphmart=target_graphmart)
        
        return {
            "status": "success",
            "graphmart": target_graphmart,
            "results": result_list,
            "row_count": len(result_list)
        }
        
    except Exception as e:
        logger.error("sparql_query_failed", error=str(e), error_type=type(e).__name__, graphmart=target_graphmart)
        return {
            "status": "error",
            "error": f"SPARQL query failed: {type(e).__name__}: {str(e)}",
            "results": [],
            "error_type": type(e).__name__
        }


def main():
    """Entry point for anzo-mcp-http console script."""
    # Pre-initialize pyanzo client to catch errors early
    _get_pyanzo_client()
    
    # Log startup information
    logger.info("starting_mcp_server", tools_count=45, transport="sse")
    
    # Run server with SSE transport for Cursor IDE
    try:
        mcp.run(transport="sse")
    except KeyboardInterrupt:
        logger.info("mcp_server_stopped", reason="user_interrupt")
        print("\nMCP server stopped by user", file=sys.stderr)
    except Exception as e:
        logger.error("mcp_server_crashed", error=str(e), error_type=type(e).__name__, exc_info=True)
        print(f"FATAL ERROR: MCP server crashed: {type(e).__name__}: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        raise


if __name__ == "__main__":
    main()

    # Run MCP server with SSE transport
    # FastMCP will automatically set up the SSE endpoints
    # Note: Port and host are configured via uvicorn settings, not run() parameters
    logger.info("starting_mcp_server", transport="sse", tools_count=len(mcp._tool_manager._tools))
    
    try:
        # FastMCP.run() with SSE transport starts uvicorn on default port
        mcp.run(transport='sse')
    except KeyboardInterrupt:
        logger.info("server_shutdown", reason="user_interrupt")
    except Exception as e:
        logger.error("server_crashed", error=str(e), error_type=type(e).__name__)
        raise
