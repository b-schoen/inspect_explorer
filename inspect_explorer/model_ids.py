from enum import Enum


# TODO(bschoen): Add cost per 1m tokens
class ModelID(Enum):
    """
    Model IDs for use with inspect.

    Conform to:
    - https://inspect.ai-safety-institute.org.uk/models.html#using-models

    Note:
     - We separate out by model provider because specifying a huggingface model id
       directly is how inspect knows to run locally.

    """

    # TODO(bschoen): Test that each one can be called

    # OpenAI - https://platform.openai.com/docs/models/overview
    GPT_4O = "openai/gpt-4o"
    GPT_4O_MINI = "openai/gpt-4o-mini"
    O1_PREVIEW = "openai/o1-preview"
    O1_MINI = "openai/o1-mini"

    # Anthropic - https://docs.anthropic.com/en/docs/about-claude/models
    CLAUDE_3_OPUS = "anthropic/claude-3-opus-20240229"
    CLAUDE_3_5_SONNET = "anthropic/claude-3-5-sonnet-20240620"
    CLAUDE_3_HAIKU = "anthropic/claude-3-haiku-20240307"

    # TODO(bschoen): Test local running with a small model

    # Together - https://api.together.ai/models

    # Together - Meta - https://huggingface.co/meta-llama
    TOGETHER_LLAMA_3_2_3B_INSTRUCT = "together/meta-llama/Llama-3.2-3B-Instruct-Turbo"
    TOGETHER_LLAMA_3_1_70B_INSTRUCT = "together/meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo"
    TOGETHER_LLAMA_3_1_405B_INSTRUCT = "together/meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo"

    # Together - Nous Research - https://huggingface.co/NousResearch
    TOGETHER_NOUS_HERMES_3_1_405B_TURBO = "together/NousResearch/Hermes-3-Llama-3.1-405B-Turbo"

    # Together - Google - https://huggingface.co/google
    TOGETHER_GOOGLE_GEMMA_2_9B_INSTRUCTION = "together/google/gemma-2-9b-it"
    TOGETHER_GOOGLE_GEMMA_2_27B_INSTRUCTION = "together/google/gemma-2-27b-it"

    # Huggingface
    #
    # NOTE: These run locally
    HUGGINGFACE_LOCAL_GPT2_SMALL = "hf/openai-community/gpt2"


def remove_provider_prefix(model_id: ModelID) -> str:
    """
    Remove the provider prefix from a model id.

    Useful when calling provider api directly. (ex: `gpt-4o-mini` instead of `openai/gpt-4o-mini`)
    """
    return model_id.value.split("/")[1]
