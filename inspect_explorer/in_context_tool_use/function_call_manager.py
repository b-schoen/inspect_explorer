import rich

from inspect_explorer.in_context_tool_use.tool_use_types import (
    ToolDefinitionWithCallable,
    ToolUseRequest,
    ToolUseResponse,
    ToolDefinition,
)


# TODO(bschoen): Tool use record? Separate from conversation history?
class FunctionCallManager:
    """
    Manages the execution of tool functions in an in-context tool use scenario.

    This class is responsible for:
    1. Storing and managing a collection of tool definitions with their associated callable functions.
    2. Providing a list of available tool definitions.
    3. Executing tool requests by calling the appropriate function and returning the result.

    Note:
     - Can be shared across multiple conversations.

    Example usage:

        # Define tool definitions with callables
        def add(a: int, b: int) -> int:
            return a + b

        tool_def = ToolDefinition(
            function_name="add",
            description="Add two numbers",
            arguments=["a", "b"],
            return_value="The sum of a and b"
        )
        tool_def_with_callable = ToolDefinitionWithCallable(tool_definition=tool_def, callable_fn=add)

        # Initialize FunctionCallManager
        fcm = FunctionCallManager([tool_def_with_callable])

        # Execute a tool
        request = ToolUseRequest(function_name="add", arguments={"a": 5, "b": 3})
        response = fcm.execute_tool(request)
        print(response)  # Output: ToolUseResponse(function_name="add", return_value="8")
    """

    def __init__(self, tool_definitions_with_callables: list[ToolDefinitionWithCallable]) -> None:

        # Store a mapping of function names to their ToolDefinitionWithCallable objects
        self._tool_map: dict[str, ToolDefinitionWithCallable] = {
            tool_def.tool_definition.function_name: tool_def
            for tool_def in tool_definitions_with_callables
        }

    def get_tool_definition_list(self) -> list[ToolDefinition]:
        # available for easy access by outside when defining everything together
        # with it's corresponding callable
        return [x.tool_definition for x in self._tool_map.values()]

    # TODO(bschoen): Ignore type conversion for now (could try ast literal then fall back to
    #                string if can't parse)
    # TODO(bschoen): Ignoring errors for now
    def execute_tool(self, request: ToolUseRequest) -> ToolUseResponse:

        rich.print(f"Executing tool: {request}")

        # Lookup the ToolDefinitionWithCallable for the requested function
        if request.function_name not in self._tool_map:
            raise ValueError(f"Unknown function: {request.function_name}")

        tool_def_with_callable = self._tool_map[request.function_name]

        # Call the function with the provided arguments

        # note: we just assume values are in order instead of enforcing kwargs,
        #       since we want to be able to easily use partial even if we
        #       don't know argument names

        result = tool_def_with_callable.callable_fn(*request.arguments.values())

        # Return the result wrapped in a ToolUseResponse
        response = ToolUseResponse(
            function_name=request.function_name,
            return_value=str(result),
        )

        rich.print(f"Executed request. Tool response for {response.function_name}")

        return response
