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
    is_valid: bool

    function_name: str
    arguments: list[_ToolUseRequestArgWrapper]


# NOTE: This can be used for arbitrary structured output
def parse_tool_use_request_from_model_response(
    client: openai.OpenAI,
    model_response: openai.types.chat.ChatCompletionMessageParam,
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
        "If you can't find or parse the tool use request, set `is_valid` to False."
        f"\n\n{model_response}"
    )

    response = client.beta.chat.completions.parse(
        model=model,
        messages=[{"role": "user", "content": content}],
        response_format=_ToolUseRequestWrapper,
    )

    tool_use_request_wrapper: _ToolUseRequestWrapper = response.choices[0].message.parsed

    if not tool_use_request_wrapper.is_valid:
        return None

    tool_use_request = ToolUseRequest(
        function_name=tool_use_request_wrapper.function_name,
        arguments={arg.name: arg.value for arg in tool_use_request_wrapper.arguments},
    )

    return tool_use_request
