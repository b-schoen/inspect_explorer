import subprocess
import dataclasses
import json
import os
import pathlib


@dataclasses.dataclass(frozen=True)
class BashCommandResult:
    command: str
    exit_code: int
    output: str  # note: we don't separate stdout and sterr since docker doesn't when streaming


# TODO(bschoen): Common higher level abstraction args like `timeout_in_seconds` are really a property of the workspace, but do I want a shared class here with them?`
def execute_bash_command(
    command: str, current_working_directory: pathlib.Path
) -> BashCommandResult:
    """Directly execute a raw unchecked bash command. Should ALWAYS be wrapped before use.

    This is useful for experimenting with, but for extremely obvious reasons not intended for
    broader use.

    Use should usually look something like:

      import functools

      execute_bash_command_fn = functools.partial(
        execute_bash_command,
        current_working_directory=pathlib.Path("model_workspace").resolve(),
      )

      ToolDefinitionWithCallable(
        tool_definition=ToolDefinition(
            function_name="execute_bash_command",
            description="Execute a bash command inside the model workspace",
            arguments=["command"],
            return_value="The result of the bash command.",
        ),
        callable_fn=execute_bash_command_fn,
    )

    The output will be provided as a json string, containing:
        - command: The bash command that was run.
        - exit_code: The exit code of the command.
        - output: The standard output and error of the command.

    Args:
        command (str): The bash command to execute.

    """
    # Don't check the result, just pass `stdout` and `stderr` to model
    #
    # from docs:
    #
    #   If you wish to capture and combine both streams into one,
    #     - set stdout to PIPE
    #     - stderr to STDOUT
    #     - instead of using capture_output
    #
    DEFAULT_TIMEOUT_IN_SECONDS = 60.0

    result: subprocess.CompletedProcess = subprocess.run(
        command,
        text=True,
        check=False,
        timeout=DEFAULT_TIMEOUT_IN_SECONDS,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
        cwd=current_working_directory,
    )

    return BashCommandResult(
        command=result.args,
        exit_code=result.returncode,
        output=result.stdout,
    )
