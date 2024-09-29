import pathlib

from inspect_explorer.affordances import raw_bash_execution


# note: could ask it to write tests first
# note: just supporting one for now
def send_aider_message(
    read_filepath: pathlib.Path,
    edit_filepath: pathlib.Path,
    message_to_coder_model: str,
) -> raw_bash_execution.BashCommandResult:
    """
    Example aider usage
    > aider --read inspect_explorer/conversation_manager.py --file tests/test_conversation_manager
    .py --yes --message 'Write unit tests for conversation manager that can be run with pytest'

    """

    assert read_filepath.exists()
    assert edit_filepath.exists()

    command = (
        f"aider "
        f"--read {read_filepath} "
        f"--file {edit_filepath} "
        # automatically accept all suggestions
        f"--yes "
        f"--message '{message_to_coder_model}'"
    )

    # note: aider needs to use the actual root directory of git
    return raw_bash_execution.execute_bash_command(
        command=command,
        current_working_directory=pathlib.Path.cwd(),
    )


def show_repo_map() -> raw_bash_execution.BashCommandResult:
    """
    Show the repo map.

    This generates a (default 1024 token) summary of the current repo.

    Example:

        inspect_explorer/in_context_tool_use/initial_explanation.py:
        │def get_in_context_tool_use_initial_explanation() -> str:
        ⋮...

        inspect_explorer/in_context_tool_use/parsing.py:
        ⋮...
        │def parse_tool_use_request_from_model_response(
        │    client: openai.OpenAI,
        │    model_response: openai.types.chat.ChatCompletionMessageParam,
        ⋮...

        inspect_explorer/in_context_tool_use/tool_use_types.py:
        ⋮...
        │class ToolDefinition(pydantic.BaseModel):
        ⋮...
        │class ToolUseRequest(pydantic.BaseModel):
        ⋮...
        │class ToolUseResponse(pydantic.BaseModel):
        ⋮...
        │@dataclasses.dataclass(frozen=True)
        │class ToolDefinitionWithCallable[R, **P]:
        ⋮...

    """
    command = "aider --show-repo-map"
    return raw_bash_execution.execute_bash_command(
        command=command,
        current_working_directory=pathlib.Path.cwd(),
    )
