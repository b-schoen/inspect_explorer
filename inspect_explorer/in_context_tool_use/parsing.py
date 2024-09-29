import openai
import pydantic

from inspect_explorer import model_ids
from inspect_explorer.in_context_tool_use.tool_use_types import ToolUseRequest, Constants


# workaround because structed outputs can't support arbitrary dicts for `arguments`??
#
# note: use of these classes should be entirely contained in this file
#
class _ToolUseRequestArgWrapper(pydantic.BaseModel):
    name: str
    value: str


class _ToolUseRequestWrapper(pydantic.BaseModel):

    # allow the model to indicate that it couldn't find or parse anything valid, in which case
    # is sets this to False and we return None
    completely_failed_to_parse: bool

    function_name: str
    arguments: list[_ToolUseRequestArgWrapper]


# NOTE: This can be used for arbitrary structured output
def parse_tool_use_request_from_model_response(
    client: openai.OpenAI,
    model_response: str,
) -> ToolUseRequest | None:
    """
    Parses a ToolUseRequest from a model response using a smaller model.

    From:
    - https://cookbook.openai.com/examples/o1/using_chained_calls_for_o1_structured_outputs

    """

    model = model_ids.remove_provider_prefix(model_ids.ModelID.GPT_4O_MINI)

    content = (
        "Given the following data, format the value "
        f"for `{Constants.TOOL_USE_REQUEST_KEY}` with the given response format. "
        f"\n\n{model_response}"
    )

    messages = [
        {"role": "system", "content": "Extract the tool use request information."},
        {"role": "user", "content": content},
    ]

    response = client.beta.chat.completions.parse(
        model=model,
        messages=messages,
        response_format=_ToolUseRequestWrapper,
    )

    tool_use_request_wrapper: _ToolUseRequestWrapper = response.choices[0].message.parsed

    if tool_use_request_wrapper.completely_failed_to_parse:
        print(
            f"Failed to find a valid tool use request in\n\n{model_response}.\n\n"
            f"Parser model was given:\n\n{messages}\n\n"
            f"Parser model responded with: {response.model_dump_json(indent=4)}"
        )
        return None

    tool_use_request = ToolUseRequest(
        function_name=tool_use_request_wrapper.function_name,
        arguments={arg.name: arg.value for arg in tool_use_request_wrapper.arguments},
    )

    return tool_use_request
