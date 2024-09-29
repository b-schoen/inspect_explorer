import tiktoken


# note: this is roughly expected to be the same as o1, but not sure
def create_gpt4o_tokenizer() -> tiktoken.Encoding:
    return tiktoken.encoding_for_model("gpt-4o")


def estimate_token_count(text: str, tokenizer: tiktoken.Encoding | None = None) -> int:
    """Estimate token count using the GPT-4o tokenizer."""

    tokenizer = tokenizer or create_gpt4o_tokenizer()

    return len(tokenizer.encode(text))
