import pytest
import openai
import json

from inspect_explorer.in_context_tool_use import (
    FunctionCallManager,
    parse_tool_use_request_from_model_response,
    ToolDefinition,
    ToolDefinitionWithCallable,
    ToolUseRequest,
    ToolUseResponse,
    Constants,
)


def test_function_call_manager():
    def add(a: int, b: int) -> int:
        return a + b

    tool_def = ToolDefinition(
        function_name="add",
        description="Add two numbers",
        arguments=["a", "b"],
        return_value="The sum of a and b",
    )
    tool_def_with_callable = ToolDefinitionWithCallable(tool_definition=tool_def, callable_fn=add)

    fcm = FunctionCallManager([tool_def_with_callable])

    # Test get_tool_definition_list
    tool_definitions = fcm.get_tool_definition_list()
    assert len(tool_definitions) == 1
    assert tool_definitions[0] == tool_def

    # Test execute_tool
    request = ToolUseRequest(function_name="add", arguments={"a": 5, "b": 3})
    response = fcm.execute_tool(request)
    assert response == ToolUseResponse(function_name="add", return_value="8")

    # Test execute_tool with unknown function
    with pytest.raises(ValueError):
        fcm.execute_tool(ToolUseRequest(function_name="unknown", arguments={}))


# note: we use a real client for this to actually make sure it works
def test_parse_tool_use_request_from_model_response():

    tool_use_request = ToolUseRequest(
        function_name="test_function",
        arguments={"arg1": "value1", "arg2": "value2"},
    )

    tool_use_request_json = json.dumps(
        {
            Constants.TOOL_USE_REQUEST_KEY: tool_use_request.model_dump(),
        },
        indent=2,
    )

    print(tool_use_request_json)

    # create a model response where the tool use request is surrounded by other stuff
    model_response = {
        "role": "assistant",
        "content": (
            f"Please use the tool: {tool_use_request_json}\n" "I've provided the request above"
        ),
    }

    client = openai.OpenAI()

    result = parse_tool_use_request_from_model_response(client, model_response)

    assert isinstance(result, ToolUseRequest)
    assert result == tool_use_request

    # now check that if we pass in a model response that doesn't contain the tool use request, we get None
    model_response = {
        "role": "assistant",
        "content": "I've provided the request above",
    }

    result = parse_tool_use_request_from_model_response(client, model_response)
    assert result is None
