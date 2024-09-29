"""Defines functionality for in context tool use (ex: needed with o1)."""

from inspect_explorer.in_context_tool_use.initial_explanation import (
    get_in_context_tool_use_initial_explanation,
)
from inspect_explorer.in_context_tool_use.parsing import parse_tool_use_request_from_model_response
from inspect_explorer.in_context_tool_use.tool_use_types import (
    ToolUseRequest,
    ToolUseResponse,
    ToolDefinition,
    ToolDefinitionWithCallable,
    Constants,
)
from inspect_explorer.in_context_tool_use.function_call_manager import FunctionCallManager
