"""Utility functions for the expt_logger library."""

import os
from typing import TypeVar


def get_env_var(name: str, default: str | None = None) -> str | None:
    """Get environment variable with optional default."""
    return os.environ.get(name, default)


def parse_metric_key(key: str) -> tuple[str, str]:
    """
    Parse a metric key into (mode, metric_name).

    Examples:
        "train/loss" -> ("train", "loss")
        "eval/accuracy" -> ("eval", "accuracy")
        "loss" -> ("train", "loss")  # default mode
    """
    if "/" in key:
        parts = key.split("/", 1)
        return parts[0], parts[1]
    return "train", key


def parse_conversation(text: str) -> list[dict[str, str]]:
    """
    Parse a conversation string into a list of messages.

    TODO: Implement parsing logic for different conversation formats:
        - "User: hello\nAssistant: hi there"
        - "Human: hello\nAssistant: hi there"
        - "<user>hello</user><assistant>hi</assistant>"

    Returns list of {"role": "user"|"assistant", "content": "..."}
    """
    raise NotImplementedError(
        "Conversation parsing from raw text is not yet implemented. "
        "Please pass messages as a list of dicts with 'role' and 'content' keys."
    )


T = TypeVar("T")


def chunk_list(lst: list[T], chunk_size: int) -> list[list[T]]:
    """Split a list into chunks of specified size."""
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]
