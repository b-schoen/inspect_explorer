import openai
import pydantic

from inspect_explorer import model_ids


def summarize_text(
    client: openai.OpenAI,
    text: str,
    max_tokens: int = 1024,
    model_id: model_ids.ModelID = model_ids.ModelID.GPT_4O_MINI,
) -> str:
    """
    Summarize given text down to `max_tokens` using a smaller model.

    Note:
    - Useful for bash outputs, which are often very long.

    """
    print(f"Using small model to summarize text of length: {len(text)}...")

    model = model_ids.remove_provider_prefix(model_id)

    task_description = f"Summarize the most important information in `{max_tokens}` tokens or less."

    content = f"{task_description}\n\n{text}\n\nRemember, your task is: {task_description}"

    messages = [
        {"role": "system", "content": "Summarize the provided information."},
        {"role": "user", "content": content},
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
    )

    input_tokens = response.usage.prompt_tokens
    output_tokens = response.usage.completion_tokens

    print(f"Summarized text with ~{input_tokens} tokens to ~{output_tokens} tokens.")

    summarized_text = response.choices[0].message.content

    return summarized_text
