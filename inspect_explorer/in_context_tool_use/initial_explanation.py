def get_in_context_tool_use_initial_explanation() -> str:
    """
    Return a fixed string for in context tool use using the format defined in this file.

    This correctly results in:

    ```
    Please add 15 and -3 to demonstrate your understanding.
    ```

    ```
    {
    "assistant_tool_use_request": {
        "function_name": "add",
        "arguments": {
            "first_number": 15,
            "second_number": -3
        }
    }
    }
    ```

    ```
    { "user_tool_use_response": { "function_name": "add", "return_value": 12 } }
    ```

    ```
    "The result of adding 15 and -3 is 12."
    ```

    """

    # TODO(bschoen): Make this generated
    return """

== BEGIN TOOL USE PROTOCOL EXPLANATION ==

You will be provided with tools according to the following protocol. Please note that markers such as [user's turn] and [assistant's turn] are not part of the conversation and are only used to separate turns in the conversation.

```
[user's turn]

"Please add 14 and 21"

{
  "tool_definitions": [
    {
      "function_name": "get_wikipedia_page",
      "description": "Returns full content of a given wikipedia page",
      "arguments": ["title_of_wikipedia_page"],
      "return_value": "returns full content of a given wikipedia page as a json string"
    },
    {
      "function_name": "add",
      "description": "Add two numbers together",
      "arguments": ["first_number", "second_number"],
      "return_value": "returns the numeric value of adding together `first_number` and `second_number`"
    }
  ]
}

[assistant's turn]

{
  "assistant_tool_use_request": {
    "function_name": "add",
    "arguments": {
      "first_number": 14,
      "second_number": 21
    }
  }
}

[user's turn]

{
  "user_tool_use_response": {
    "function_name": "add",
    "return_value": 35
  }
}

[assistant's turn]

"The result of adding 14 and 21 is 35."
```

Again, note that your do not need to prefix anything with `[assistant's turn]`, that was solely to separate conversation messages in our example.

== END TOOL USE PROTOCOL EXPLANATION ==

"""
