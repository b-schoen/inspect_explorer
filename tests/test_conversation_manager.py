import pytest
import pathlib
from inspect_explorer.conversation_manager import ConversationManager, MessageParam

@pytest.fixture
def temp_dir(tmp_path):
    return tmp_path / "test_conversations"

@pytest.fixture
def conversation_manager(temp_dir):
    return ConversationManager(temp_dir)

def test_create_new_conversation(conversation_manager):
    conversation_id = conversation_manager.create_new_conversation()
    assert conversation_id in conversation_manager.get_conversation_ids()

def test_get_conversation_ids(conversation_manager):
    conversation_id1 = conversation_manager.create_new_conversation()
    conversation_id2 = conversation_manager.create_new_conversation()
    conversation_ids = conversation_manager.get_conversation_ids()
    assert conversation_id1 in conversation_ids
    assert conversation_id2 in conversation_ids

def test_get_conversation_messages(conversation_manager):
    conversation_id = conversation_manager.create_new_conversation()
    messages = conversation_manager.get_conversation_messages(conversation_id)
    assert isinstance(messages, list)
    assert len(messages) == 0

def test_add_conversation_message(conversation_manager):
    conversation_id = conversation_manager.create_new_conversation()
    message: MessageParam = {"role": "user", "content": "Hello, world!"}
    conversation_manager.add_conversation_message(conversation_id, message)
    messages = conversation_manager.get_conversation_messages(conversation_id)
    assert len(messages) == 1
    assert messages[0] == message

def test_multiple_conversations(conversation_manager):
    conversation_id1 = conversation_manager.create_new_conversation()
    conversation_id2 = conversation_manager.create_new_conversation()
    
    message1: MessageParam = {"role": "user", "content": "Hello from conversation 1"}
    message2: MessageParam = {"role": "user", "content": "Hello from conversation 2"}
    
    conversation_manager.add_conversation_message(conversation_id1, message1)
    conversation_manager.add_conversation_message(conversation_id2, message2)
    
    messages1 = conversation_manager.get_conversation_messages(conversation_id1)
    messages2 = conversation_manager.get_conversation_messages(conversation_id2)
    
    assert len(messages1) == 1
    assert len(messages2) == 1
    assert messages1[0] == message1
    assert messages2[0] == message2

def test_conversation_persistence(temp_dir):
    # Create a conversation and add a message
    cm1 = ConversationManager(temp_dir)
    conversation_id = cm1.create_new_conversation()
    message: MessageParam = {"role": "user", "content": "Persistent message"}
    cm1.add_conversation_message(conversation_id, message)
    
    # Create a new ConversationManager instance and verify the message is still there
    cm2 = ConversationManager(temp_dir)
    messages = cm2.get_conversation_messages(conversation_id)
    assert len(messages) == 1
    assert messages[0] == message
