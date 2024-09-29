import pathlib

from inspect_explorer.affordances import raw_bash_execution


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
