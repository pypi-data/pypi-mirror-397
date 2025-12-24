import functools
import inspect
import cognee
import asyncio
from typing import Optional, List
import logging
from agents import function_tool, FunctionTool
from cognee.modules.engine.models.node_set import NodeSet

logger = logging.getLogger(__name__)

# Lock for serializing cognee operations
_cognee_lock = asyncio.Lock()


async def _add_and_cognify(data: str, node_set: Optional[List[str]] = None):
    """Add data to cognee and run cognify. Uses lock to prevent race conditions."""
    async with _cognee_lock:
        logger.info(f"Adding data to cognee with node_set={node_set}")
        await cognee.add(data, node_set=node_set)
        await cognee.cognify()
        logger.info("Data added and cognified successfully")


async def _search_cognee(query_text: str, node_set: Optional[List[str]] = None):
    """Search cognee with optional NodeSet filtering."""
    logger.info(f"Searching cognee: query='{query_text}', node_set={node_set}")

    if node_set:
        # Use NodeSet filtering when a node_set is provided
        result = await cognee.search(
            query_text=query_text, node_type=NodeSet, node_name=node_set, top_k=100
        )
    else:
        # Default search without node filtering
        result = await cognee.search(query_text, top_k=100)

    logger.info(f"Search completed, found {len(result) if result else 0} results")
    return result


# =============================================================================
# NON-SESSIONIZED TOOLS
# These do NOT use NodeSet - data is global, not tagged to any session
# =============================================================================


@function_tool
async def add_tool(data: str) -> str:
    """
    Store information in the memory for later retrieval.

    Use this tool whenever you need to remember, store, or save information
    that the user provides. This is essential for building up a memory
    that can be searched later. Always use this tool when the user says things
    like "remember", "store", "save", or gives you information to keep track of.

    Args:
        data: The text or information you want to store and remember.

    Returns:
        A confirmation message indicating that the item was added.
    """
    logger.info("add_tool called")
    await _add_and_cognify(data, node_set=None)  # No NodeSet for non-sessionized
    return "Item added to cognee and processed"


@function_tool
async def search_tool(query_text: str) -> str:
    """
    Search and retrieve previously stored information from the memory.

    Use this tool to find and recall information that was previously stored.
    Always use this tool when you need to answer questions about information
    that should be in the memory, or when the user asks questions
    about previously discussed topics.

    Args:
        query_text: What you're looking for, written as a natural language search query.

    Returns:
        A list of search results matching the query.
    """
    logger.info("search_tool called")
    result = await _search_cognee(
        query_text, node_set=None
    )  # No NodeSet for non-sessionized
    return str(result)


# =============================================================================
# SESSIONIZED TOOLS
# These USE NodeSet - data is tagged with session_id for organization
# =============================================================================


async def _add_tool_impl(data: str, node_set: Optional[List[str]] = None) -> str:
    """
    Store information in the memory for later retrieval.

    Use this tool whenever you need to remember, store, or save information
    that the user provides. This is essential for building up a memory
    that can be searched later. Always use this tool when the user says things
    like "remember", "store", "save", or gives you information to keep track of.

    Args:
        data: The text or information you want to store and remember.
        node_set: Node set identifiers for session organization (injected by wrapper).

    Returns:
        A confirmation message indicating that the item was added.
    """
    logger.info(f"_add_tool_impl called with node_set={node_set}")
    await _add_and_cognify(data, node_set=node_set)
    return "Item added to cognee and processed"


async def _search_tool_impl(
    query_text: str, node_set: Optional[List[str]] = None
) -> str:
    """
    Search and retrieve previously stored information from the memory.

    Use this tool to find and recall information that was previously stored.
    Always use this tool when you need to answer questions about information
    that should be in the memory, or when the user asks questions
    about previously discussed topics.

    Args:
        query_text: What you're looking for, written as a natural language search query.
        node_set: Node set identifiers for session isolation (injected by wrapper).

    Returns:
        A list of search results matching the query.
    """
    logger.info(f"_search_tool_impl called with node_set={node_set}")
    result = await _search_cognee(query_text, node_set=node_set)
    return str(result)


def _create_sessionized_wrapper(func, session_id: str):
    """
    Create a sessionized wrapper that injects node_set=[session_id].

    The wrapper preserves the original function signature (minus node_set)
    so that function_tool only exposes 'data' or 'query_text' to the LLM.
    """
    # Get original parameters but exclude 'node_set' from the exposed signature
    original_sig = inspect.signature(func)
    params_without_node_set = [
        p for p in original_sig.parameters.values() if p.name != "node_set"
    ]
    new_sig = original_sig.replace(parameters=params_without_node_set)

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        logger.info(f"Sessionized {func.__name__} called with session_id={session_id}")
        # Inject session_id as node_set for session isolation
        kwargs["node_set"] = [session_id]
        return await func(*args, **kwargs)

    # Set the modified signature (without node_set) for function_tool
    wrapper.__signature__ = new_sig

    return wrapper


def get_sessionized_cognee_tools(
    session_id: Optional[str] = None,
) -> tuple[FunctionTool, FunctionTool]:
    """
    Returns cognee tools sessionized for a specific user/session.

    When using sessionized tools:
    - Data added is tagged with the session's NodeSet
    - Searches only return data from that session's NodeSet
    - Different sessions are completely isolated

    Args:
        session_id: The session ID to bind to all tools. If not provided,
                    a random session ID is auto-generated.

    Returns:
        A tuple of (add_tool, search_tool) sessionized for the given session.
    """
    if session_id is None:
        import uuid

        uid = str(uuid.uuid4())
        session_id = f"cognee-test-user-{uid}"

    logger.info(f"Creating sessionized tools for session_id={session_id}")

    # Create sessionized wrappers that inject node_set=[session_id]
    sessionized_add_func = _create_sessionized_wrapper(_add_tool_impl, session_id)
    sessionized_search_func = _create_sessionized_wrapper(_search_tool_impl, session_id)

    # Apply function_tool decorator to create FunctionTool instances
    sessionized_add = function_tool(sessionized_add_func)
    sessionized_search = function_tool(sessionized_search_func)

    logger.info(f"Sessionized tools created successfully for session_id={session_id}")

    return sessionized_add, sessionized_search
