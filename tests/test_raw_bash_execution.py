import tempfile
import pathlib
import functools

from inspect_explorer.affordances import raw_bash_execution


# TODO(bschoen): Check error case, timeout, etc
def test_execute_bash_command() -> None:

    # use temporary directory for all actions
    with tempfile.TemporaryDirectory() as temp_dir:

        execute_bash_command_fn = functools.partial(
            raw_bash_execution.execute_bash_command,
            current_working_directory=pathlib.Path(temp_dir),
        )

        # check that expected file isn't already in directory
        command = "cat test_file.txt"
        result: raw_bash_execution.BashCommandResult = execute_bash_command_fn(command=command)

        assert result.exit_code != 0

        # create a file
        command = "echo 'Hello, World!' > test_file.txt"
        result = execute_bash_command_fn(command=command)

        assert result.exit_code == 0

        # check that we can see it
        command = "ls"
        result = execute_bash_command_fn(command=command)

        assert result.command == command
        assert result.exit_code == 0
        assert "test_file.txt" in result.output

        # check we can access the file in this environment
        command = f"cat test_file.txt"
        result = execute_bash_command_fn(command=command)

        # check the result
        assert result.command == command
        assert result.exit_code == 0
        assert result.output == "Hello, World!\n"
