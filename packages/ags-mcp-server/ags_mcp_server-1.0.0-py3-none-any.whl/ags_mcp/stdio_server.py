"""Anzo MCP Server - stdio transport ONLY for MCP clients (Cursor/Claude Desktop).

This is the entry point for MCP clients that communicate via stdio.
It does NOT start an HTTP server, uvicorn, or any web endpoints.

For HTTP/SSE support, use anzo_mcp_server_v2.py instead.
"""

import os
import sys

# ============================================================================
# CRITICAL: Set working directory to script location FIRST
# This ensures imports work regardless of where Cursor runs the script from
# ============================================================================
_script_dir = os.path.dirname(os.path.abspath(__file__))
if _script_dir not in sys.path:
    sys.path.insert(0, _script_dir)
os.chdir(_script_dir)

import logging
import structlog
import warnings

# ============================================================================
# CRITICAL: Configure logging BEFORE any imports that might log
# MCP stdio protocol requires clean stdout for JSON-RPC communication
# ALL logs must go to stderr, NEVER stdout
# ============================================================================

# Check if we're in stdio mode
IS_STDIO_MODE = os.getenv("MCP_TRANSPORT", "").lower() == "stdio"

# 1. Configure Python's standard logging to stderr ONLY
stderr_handler = logging.StreamHandler(sys.stderr)
stderr_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# Use INFO level but filter in handler to allow easier debugging
logging.basicConfig(
    level=logging.INFO,
    handlers=[stderr_handler],
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True
)

# 2. Silence chatty loggers to reduce noise
logging.getLogger("mcp.server.lowlevel").setLevel(logging.WARNING)
logging.getLogger("uvicorn").setLevel(logging.ERROR)
logging.getLogger("watchfiles").setLevel(logging.ERROR)

# 3. Ensure root logger uses stderr
root_logger = logging.getLogger()
root_logger.handlers.clear()
root_logger.addHandler(stderr_handler)
root_logger.setLevel(logging.WARNING if IS_STDIO_MODE else logging.INFO)  # WARNING in stdio mode

# 4. Redirect warnings to stderr
warnings.simplefilter('default')
logging.captureWarnings(True)

# 5. Configure structlog to use stdlib logging (which goes to stderr)
#    Do NOT redirect sys.stdout - FastMCP needs it for stdio protocol
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Now it's safe to import anzo modules and FastMCP
from mcp.server.fastmcp import FastMCP
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

logger = structlog.get_logger(__name__)


def run_stdio():
    """
    Run MCP server in stdio mode ONLY.
    No HTTP server, no uvicorn, no SSE endpoints.
    Pure stdio transport for Cursor/Claude Desktop.
    """
    # Initialize configuration and client
    try:
        config = get_config()
        client = AnzoAPIClient(config)
        logger.debug("anzo_client_initialized", base_url=config.http_base)
    except Exception as e:
        logger.error("failed_to_initialize", error=str(e))
        sys.exit(1)

    # Initialize pyanzo client once for SPARQL queries (reused across all queries)
    pyanzo_client = None
    try:
        from pyanzo import AnzoClient
        pyanzo_client = AnzoClient(
            domain=config.http_base.replace("https://", "").replace("http://", ""),
            port=config.port,
            username=config.username,
            password=config.password
        )
        logger.debug("pyanzo_client_initialized")
    except ImportError:
        logger.warning("pyanzo_not_available", message="pyanzo library not installed, SPARQL queries will fail")
    except Exception as e:
        logger.warning("pyanzo_init_failed", error=str(e))

    # Initialize MCP server with stdio transport
    mcp = FastMCP("anzo-graphmart")

    # Register all MCP tools with error handling
    tool_registrations = [
        ("graphmart", register_graphmart_tools),
        ("layer", register_layer_tools),
        ("step", register_step_tools),
        ("ontology", register_ontology_tools),
        ("dataset", register_dataset_tools),
        ("pipeline", register_pipeline_tools),
    ]
    
    registered_count = 0
    for tool_name, register_func in tool_registrations:
        try:
            register_func(mcp, client)
            registered_count += 1
            logger.debug(f"registered_{tool_name}_tools")
            print(f"Registered {tool_name} tools", file=sys.stderr)
        except Exception as e:
            logger.error(f"failed_to_register_{tool_name}_tools", error=str(e), error_type=type(e).__name__, exc_info=True)
            print(f"ERROR: Failed to register {tool_name} tools: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            # Continue registering other tools even if one fails
            # This ensures partial functionality if some tools have issues
    
    logger.debug("mcp_tools_registration_complete", registered=registered_count, total=len(tool_registrations))

    # Register prompts for agent guidance
    register_prompts(mcp)
    print("Agent guidance prompts registered", file=sys.stderr)
    print(f"Tool registration complete: {registered_count}/{len(tool_registrations)} categories registered", file=sys.stderr)

    # SPARQL query tool with pyanzo
    @mcp.tool()
    def execute_sparql_query(query: str, graphmart_uri: str = None) -> dict:
        """
        Execute a SPARQL query against the Anzo database using pyanzo.
        
        Args:
            query: SPARQL query string
            graphmart_uri: Optional graphmart URI to query against (defaults to ANZO_GRAPHMART_IRI from env)
            
        Returns:
            Query results as JSON with status, results, and row_count
        """
        # Check if pyanzo client is available
        if pyanzo_client is None:
            logger.error("pyanzo_unavailable")
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
            
            # Execute query using the pre-initialized pyanzo client
            results = pyanzo_client.query_graphmart(target_graphmart, query)
            
            # Convert results to list of dictionaries
            result_list = []
            if results:
                for row in results.as_table_results().as_record_dictionaries():
                    result_list.append(row)
            
            logger.debug("sparql_query_executed", rows=len(result_list), graphmart=target_graphmart)
            
            return {
                "status": "success",
                "graphmart": target_graphmart,
                "results": result_list,
                "row_count": len(result_list)
            }
            
        except Exception as e:
            logger.error("sparql_query_failed", error=str(e), error_type=type(e).__name__)
            return {
                "status": "error",
                "error": f"SPARQL query failed: {type(e).__name__}: {str(e)}",
                "results": []
            }

    # Run the MCP server with stdio transport
    # This will block and handle MCP protocol communication via stdin/stdout
    # NO HTTP server, NO uvicorn, NO SSE endpoints
    logger.debug("starting_mcp_stdio_server", server_name="anzo-graphmart", mode="stdio", tools_registered=registered_count)
    
    # Log tool count for debugging (to stderr, so it won't interfere with MCP protocol)
    if hasattr(mcp, '_tool_manager') and hasattr(mcp._tool_manager, '_tools'):
        tool_count = len(mcp._tool_manager._tools)
        print(f"MCP Server 'anzo-graphmart' starting with {tool_count} tools registered", file=sys.stderr)
        print(f"Tools: {', '.join(sorted(mcp._tool_manager._tools.keys())[:10])}...", file=sys.stderr)
    else:
        print("WARNING: Cannot access tool manager to verify tool registration", file=sys.stderr)
    
    try:
        # FastMCP.run() auto-detects stdio mode when stdin/stdout are pipes
        # Do NOT pass transport parameter - it's not supported
        print("MCP server ready, waiting for client connection...", file=sys.stderr)
        mcp.run()  # Blocks here for stdio communication
    except KeyboardInterrupt:
        logger.debug("mcp_server_interrupted")
        print("MCP server interrupted by user", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        logger.error("mcp_server_crashed", error=str(e), error_type=type(e).__name__, exc_info=True)
        print(f"FATAL ERROR: MCP server crashed: {type(e).__name__}: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


def main():
    """Entry point for anzo-mcp-stdio console script."""
    # Verify we're in stdio mode (Cursor should set this)
    if not IS_STDIO_MODE:
        print("Warning: MCP_TRANSPORT=stdio not set. Assuming stdio mode.", file=sys.stderr)
    
    # Run stdio-only server (no HTTP/uvicorn)
    run_stdio()


# MCP stdio server entry point
if __name__ == "__main__":
    main()
