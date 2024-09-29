from inspect_explorer.affordances import aider_cli


def test_aider_cli() -> None:

    result = aider_cli.show_repo_map()

    print(result.output)

    assert result.command == "aider --show-repo-map"
    assert result.exit_code == 0
