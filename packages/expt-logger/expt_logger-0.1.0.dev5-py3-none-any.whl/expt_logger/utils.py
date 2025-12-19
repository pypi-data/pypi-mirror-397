"""Utility functions for the expt_logger library."""

import json
import os
import warnings
from typing import Any, TypeVar


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


def sanitize_config(config: Any) -> tuple[dict[str, Any], list[str]]:
    """
    Sanitize config to ensure it's JSON-serializable.

    This function:
    1. Validates that config is a dict (raises TypeError if not)
    2. Removes any non-JSON-serializable values with warnings
    3. Returns (sanitized_config, list_of_errors)

    Args:
        config: Configuration to sanitize (should be a dict)

    Returns:
        Tuple of (sanitized_config_dict, list_of_error_messages)

    Raises:
        TypeError: If config is not a dict

    Example:
        config = {"lr": 0.001, "callback": lambda x: x, "nested": {"fn": print}}
        sanitized, errors = sanitize_config(config)
        # sanitized = {"lr": 0.001}
        # errors = ["Removed non-serializable value for key 'callback': ...", ...]
    """
    if not isinstance(config, dict):
        raise TypeError(
            f"config must be a dict, got {type(config).__name__}. "
            f"Expected format: {{'learning_rate': 0.001, 'batch_size': 32}}"
        )

    sanitized = {}
    errors = []

    def is_json_serializable(value: Any) -> bool:
        """Check if a value can be serialized to JSON."""
        try:
            json.dumps(value)
            return True
        except (TypeError, ValueError, OverflowError):
            return False

    def sanitize_value(key_path: str, value: Any) -> tuple[Any | None, bool]:
        """
        Recursively sanitize a value.

        Returns:
            Tuple of (sanitized_value, is_valid)
            - is_valid=True means the value (or parts of it) is serializable
            - is_valid=False means the value should be discarded
        """
        # Try to serialize the whole value first
        if is_json_serializable(value):
            return value, True

        # If it's a dict, try to sanitize recursively
        if isinstance(value, dict):
            sanitized_dict = {}
            for k, v in value.items():
                nested_key = f"{key_path}.{k}"
                sanitized_v, is_valid = sanitize_value(nested_key, v)
                if is_valid:
                    sanitized_dict[k] = sanitized_v
            # Return the dict if it has any valid values
            if sanitized_dict:
                return sanitized_dict, True
            return None, False

        # If it's a list, try to sanitize each element
        if isinstance(value, list):
            sanitized_list = []
            for i, item in enumerate(value):
                nested_key = f"{key_path}[{i}]"
                sanitized_item, is_valid = sanitize_value(nested_key, item)
                if is_valid:
                    sanitized_list.append(sanitized_item)
            # Return the list if it has any valid values
            if sanitized_list:
                return sanitized_list, True
            return None, False

        # Value is not serializable and can't be recursively sanitized
        return None, False

    for key, value in config.items():
        sanitized_value, is_valid = sanitize_value(key, value)

        if is_valid:
            sanitized[key] = sanitized_value
        else:
            # Record error
            value_type = type(value).__name__
            value_repr = repr(value) if len(repr(value)) < 50 else f"{repr(value)[:47]}..."
            error_msg = (
                f"Removed non-serializable value for key '{key}': "
                f"{value_type} ({value_repr})"
            )
            errors.append(error_msg)
            warnings.warn(error_msg, UserWarning, stacklevel=3)

    return sanitized, errors
