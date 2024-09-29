import pytest
from unittest.mock import Mock
import openai
from inspect_explorer.in_context_tool_use.function_call_manager import FunctionCallManager
from inspect_explorer.in_context_tool_use.parsing import parse_tool_use_request_from_model_response
from inspect_explorer.in_context_tool_use.tool_use_types import (
    ToolDefinition,
    ToolDefinitionWithCallable,
    ToolUseRequest,
    ToolUseResponse,
)

def test_function_call_manager():
    def add(a: int, b: int) -> int:
        return a + b

    tool_def = ToolDefinition(
        function_name="add",
        description="Add two numbers",
        arguments=["a", "b"],
        return_value="The sum of a and b"
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

def test_parse_tool_use_request_from_model_response():
    mock_client = Mock(spec=openai.OpenAI)
    mock_response = Mock()
    mock_response.choices = [
        Mock(
            message=Mock(
                parsed=ToolUseRequest(
                    function_name="test_function",
                    arguments={"arg1": "value1", "arg2": "value2"}
                )
            )
        )
    ]
    mock_client.beta.chat.completions.parse.return_value = mock_response

    model_response = {"role": "assistant", "content": "Test content"}
    result = parse_tool_use_request_from_model_response(mock_client, model_response)

    assert isinstance(result, ToolUseRequest)
    assert result.function_name == "test_function"
    assert result.arguments == {"arg1": "value1", "arg2": "value2"}

    mock_client.beta.chat.completions.parse.assert_called_once()
