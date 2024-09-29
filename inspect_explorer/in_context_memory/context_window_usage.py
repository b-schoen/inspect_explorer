from openai.types import CompletionUsage

from typing import ClassVar

import dataclasses


@dataclasses.dataclass(frozen=True)
class ContextWindowUsageThresholds:
    """
    Thresholds for context window usage.
    """

    fraction_used_before_warning: float = 0.5
    fraction_used_before_truncation: float = 0.8

    max_size_allowed_by_api: int = 128_000

    @property
    def tokens_used_before_warning(self) -> int:
        return int(self.fraction_used_before_warning * self.max_size_allowed_by_api)

    @property
    def tokens_used_before_truncation(self) -> int:
        return int(self.fraction_used_before_truncation * self.max_size_allowed_by_api)

    def get_current_usage_fraction(self, completion_usage: CompletionUsage) -> float:
        return completion_usage.total_tokens / self.max_size_allowed_by_api


def _fraction_to_percentage_string(fraction: float) -> str:
    # note: we use ints to avoid the dreaded 9.11 > 9.9 meme
    return f"{int(fraction * 100)}%"


def get_context_window_usage_message(
    completion_usage: CompletionUsage,
    thresholds: ContextWindowUsageThresholds | None = None,
) -> str:
    """
    Get a message to prepend to a conversation to inform the assistant about the current context window usage.

    This is helpful for informing the assistant about the current context window usage, so that it can make better decisions about when to summarize the conversation history.

    """

    thresholds = thresholds or ContextWindowUsageThresholds()

    current_usage_fraction = thresholds.get_current_usage_fraction(completion_usage)

    current_usage_percentage = _fraction_to_percentage_string(current_usage_fraction)
    warning_threshold_percentage = _fraction_to_percentage_string(
        thresholds.fraction_used_before_warning
    )
    truncation_threshold_percentage = _fraction_to_percentage_string(
        thresholds.fraction_used_before_truncation
    )

    message = (
        f"\n== BEGIN CONTEXT WINDOW USAGE INFO =="
        f"\nCurrent context window usage: {current_usage_percentage} "
        f"({completion_usage.total_tokens} / {thresholds.max_size_allowed_by_api} tokens)\n"
        f"Warning threshold: {warning_threshold_percentage} "
        f"({thresholds.tokens_used_before_warning} tokens)\n"
        f"Truncation threshold: {truncation_threshold_percentage} "
        f"({thresholds.tokens_used_before_truncation} tokens) - Whenever current context window usage exceeds this, older messages will be truncated to fit, make sure to use your memory section to avoid losing information\n"
        f"== END CONTEXT WINDOW USAGE INFO ==\n"
    )

    return message
