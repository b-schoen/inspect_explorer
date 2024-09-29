from typing import Any, Callable
import dataclasses

# note: we use pydantic as this allows easier integration with structured output than dataclasses,
#       this can be done via classvars and tagged types still as well
import pydantic


class Constants:
    """
    Used to make these slightly easier to read for the model.

    Example:

    ```
    {
        "assistant_tool_use_request": {
            "function_name": "add",
            "arguments": {
                "first_number": 15,
                "second_number": -3
            }
        }
    }
    ```
    """

    TOOL_DEFINITIONS_KEY = "tool_definitions"
    TOOL_USE_REQUEST_KEY = "assistant_tool_use_request"
    TOOL_USE_RESPONSE_KEY = "user_tool_use_response"


class ToolDefinition(pydantic.BaseModel):
    function_name: str
    description: str
    arguments: list[str]
    return_value: str


class ToolUseRequest(pydantic.BaseModel):
    function_name: str
    arguments: dict[str, Any]


# TODO(bschoen): Probably want to use tagged types here
class ToolUseResponse(pydantic.BaseModel):
    function_name: str
    return_value: str


@dataclasses.dataclass(frozen=True)
class ToolDefinitionWithCallable[R, **P]:
    """Tool definition with an associated python callable that can be used to execute the tool."""

    tool_definition: ToolDefinition
    callable_fn: Callable[P, R]
