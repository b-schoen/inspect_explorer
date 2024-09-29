import openai

import datetime
from typing import Iterable, Any
import enum
import json
import pathlib


import coolname
import pytz
from openai.types.chat import ChatCompletionMessageParam
import rich.markdown
import rich.table


from inspect_explorer.model_ids import ModelID
from inspect_explorer import tokenization


type ConversationId = str
MessageParam = ChatCompletionMessageParam


def generate_conversation_id() -> ConversationId:
    """
    Generate a unique conversation id.
    """
    # Get the current time in PST
    pst_timezone = pytz.timezone("America/Los_Angeles")
    current_time = datetime.datetime.now(pst_timezone)

    # Format the time as ex: 10:06 AM
    timestamp_string = current_time.strftime("%Y-%m-%d_%I:%M_%p")
    unique_coolname = "_".join(coolname.generate())

    return f"{timestamp_string}__{unique_coolname}"


def _read_json_file(filepath: pathlib.Path) -> list[MessageParam]:
    """Read and return the data from a JSON file."""
    with filepath.open("r", encoding="utf-8") as file:
        return json.load(file)


def _write_json_file(filepath: pathlib.Path, data: list[MessageParam]) -> None:
    """Write data to a JSON file."""

    with filepath.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


class ConversationManager:
    """
    Handles getting and setting conversations and messages using JSON files in a subdirectory.

    Each conversation is stored as a separate JSON file named <conversation-id>.json
    within the 'conversations' directory.

    This approach replaces the use of Streamlit's session state with persistent storage.
    """

    _CONVERSATIONS_DIR = pathlib.Path("conversations")

    def __init__(self, directory: pathlib.Path | None = None) -> None:
        # if none, default to `_CONVERSATIONS_DIR` (allowing this as input allows easy testing)
        self._directory = directory or self._CONVERSATIONS_DIR

        # Create the conversations directory if it doesn't exist
        self._directory.mkdir(parents=True, exist_ok=True)

    def get_conversation_ids(self) -> list[ConversationId]:
        """
        Returns a list of all conversation IDs by listing JSON files in the conversations directory.
        """
        return [filepath.stem for filepath in self._directory.glob("*.json")]

    def get_conversation_messages(self, conversation_id: ConversationId) -> list[MessageParam]:
        """
        Retrieves the list of messages for a given conversation ID by loading the corresponding JSON file.
        """
        filepath = self._directory / f"{conversation_id}.json"

        print(f"Loading conversation from: {filepath.resolve()}")

        return _read_json_file(filepath)

    def add_conversation_message(
        self,
        conversation_id: ConversationId,
        message: MessageParam,
    ) -> None:
        """
        Adds a new message to the specified conversation and saves it back to the JSON file.
        """
        filepath = self._directory / f"{conversation_id}.json"
        messages = _read_json_file(filepath)
        messages.append(message)
        _write_json_file(filepath, messages)

    def create_new_conversation(self) -> ConversationId:
        """
        Creates a new conversation by generating a unique ID and initializing an empty JSON file.
        """
        conversation_id = generate_conversation_id()
        filepath = self._directory / f"{conversation_id}.json"
        _write_json_file(filepath, [])
        return conversation_id

    def delete_conversation(self, conversation_id: ConversationId) -> None:
        """
        Deletes a conversation file given its conversation ID.
        """
        filepath = self._directory / f"{conversation_id}.json"
        if filepath.exists():
            filepath.unlink()
        else:
            raise FileNotFoundError(f"Conversation file not found: {filepath}")


def show_conversation(
    conversation_manager: ConversationManager,
    conversation_id: ConversationId,
) -> None:
    """
    Show the conversation history for a given conversation ID.
    """
    messages = conversation_manager.get_conversation_messages(conversation_id)

    tokenizer = tokenization.create_gpt4o_tokenizer()

    table = rich.table.Table(
        "role",
        "content",
        "(est) token count",
        title=f"Conversation History: {conversation_id}",
        show_lines=True,
    )

    for message in reversed(messages):
        table.add_row(
            message["role"],
            rich.markdown.Markdown(message["content"]),
            str(tokenization.estimate_token_count(message["content"], tokenizer)),
        )

    rich.print(table)
