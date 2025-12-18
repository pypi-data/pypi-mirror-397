"""
Auto-instrumentation module for Aigie SDK.

This module provides automatic instrumentation for:
- LangChain agents and chains
- LangGraph workflows
- LLM clients (OpenAI, Anthropic, Gemini)
- Tool calls
- Automatic trace creation

Usage:
    from aigie import init
    
    # Initialize with auto-instrumentation
    init(api_key="...", api_url="...")
    
    # All workflows are now automatically traced
"""

from typing import Optional

_instrumentation_state = {
    "langchain": False,
    "langgraph": False,
    "llm": False,
    "tools": False,
    "dspy": False,
    "haystack": False,
}


def enable_all() -> None:
    """Enable all available auto-instrumentation."""
    enable_langchain()
    enable_langgraph()
    enable_llm()
    enable_tools()
    enable_dspy()
    enable_haystack()


def enable_langchain() -> None:
    """Enable LangChain auto-instrumentation."""
    if _instrumentation_state["langchain"]:
        return
    
    try:
        from .langchain import patch_langchain
        patch_langchain()
        _instrumentation_state["langchain"] = True
    except ImportError:
        pass  # LangChain not installed


def enable_langgraph() -> None:
    """Enable LangGraph auto-instrumentation."""
    if _instrumentation_state["langgraph"]:
        return
    
    try:
        from .langgraph import patch_langgraph
        patch_langgraph()
        _instrumentation_state["langgraph"] = True
    except ImportError:
        pass  # LangGraph not installed


def enable_llm() -> None:
    """Enable LLM client auto-instrumentation."""
    if _instrumentation_state["llm"]:
        return
    
    try:
        from .llm import patch_all_llms
        patch_all_llms()
        _instrumentation_state["llm"] = True
    except ImportError:
        pass


def enable_tools() -> None:
    """Enable tool call auto-instrumentation."""
    if _instrumentation_state["tools"]:
        return
    
    try:
        from .tools import patch_tools
        patch_tools()
        _instrumentation_state["tools"] = True
    except ImportError:
        pass


def enable_dspy() -> None:
    """Enable DSPy auto-instrumentation."""
    if _instrumentation_state["dspy"]:
        return

    try:
        from .dspy import patch_dspy
        patch_dspy()
        _instrumentation_state["dspy"] = True
    except ImportError:
        pass  # DSPy not installed


def enable_haystack() -> None:
    """Enable Haystack auto-instrumentation."""
    if _instrumentation_state["haystack"]:
        return

    try:
        from .haystack import patch_haystack
        patch_haystack()
        _instrumentation_state["haystack"] = True
    except ImportError:
        pass  # Haystack not installed


def disable_all() -> None:
    """Disable all auto-instrumentation."""
    _instrumentation_state["langchain"] = False
    _instrumentation_state["langgraph"] = False
    _instrumentation_state["llm"] = False
    _instrumentation_state["tools"] = False
    _instrumentation_state["dspy"] = False
    _instrumentation_state["haystack"] = False


def is_enabled(framework: str) -> bool:
    """Check if instrumentation is enabled for a framework."""
    return _instrumentation_state.get(framework, False)
