"""
expt_logger - Simple experiment tracking library.

Usage:
    import expt_logger

    run = expt_logger.init(name="experiment-1")

    for step in range(100):
        expt_logger.log({"train/loss": 0.5, "train/accuracy": 0.9})

    expt_logger.end()

Or with context manager:
    with expt_logger.init(name="my-experiment") as run:
        expt_logger.log({"loss": 0.5})
"""

from __future__ import annotations

import os
from typing import Any

from .client import APIError, Client
from .config import DEFAULT_BASE_URL
from .run import Run
from .types import Config, Message, Reward, Rollout, Scalar
from .utils import parse_conversation

__version__ = "0.1.0"
__all__ = [
    # Main API
    "init",
    "log",
    "log_rollout",
    "flush",
    "end",
    # Global state
    "run",
    "config",
    # Classes
    "Run",
    "Config",
    "Client",
    "APIError",
    # Types
    "Scalar",
    "Rollout",
    "Message",
    "Reward",
    # Utils
    "parse_conversation",
]

# Global run instance
_current_run: Run | None = None


def init(
    name: str | None = None,
    config: dict[str, Any] | None = None,
    api_key: str | None = None,
    base_url: str | None = DEFAULT_BASE_URL,
    auto_flush_interval: float = 10.0,
    auto_flush_buffer_size: int = 50,
) -> Run:
    """
    Initialize a new experiment run.

    Args:
        name: Experiment name. Auto-generated if not provided.
        config: Initial configuration dictionary.
        api_key: API key. Falls back to EXPT_LOGGER_API_KEY environment variable.
        base_url: API server URL.
                  Falls back to EXPT_LOGGER_BASE_URL env var or configured default.
        auto_flush_interval: Time in seconds to wait before auto-flushing buffered data.
                            Defaults to 10.0 seconds.
        auto_flush_buffer_size: Number of buffered items that triggers immediate flush.
                               Defaults to 100 items.

    Returns:
        Run instance (also accessible via expt_logger.run).

    Example:
        run = expt_logger.init(
            name="my-experiment",
            config={"lr": 0.001, "batch_size": 32}
        )

        # Custom auto-flush settings
        run = expt_logger.init(
            name="fast-experiment",
            auto_flush_interval=10.0,  # Flush every 10 seconds
            auto_flush_buffer_size=50  # Or when 50 items buffered
        )
    """
    global _current_run

    # Finish any existing run
    if _current_run is not None:
        _current_run.end()

    # Resolve API key
    resolved_api_key = api_key or os.environ.get("EXPT_LOGGER_API_KEY")
    if not resolved_api_key:
        raise ValueError("API key required. Pass api_key or set EXPT_LOGGER_API_KEY env variable.")

    # Resolve base URL
    resolved_base_url = base_url or os.environ.get("EXPT_LOGGER_BASE_URL", DEFAULT_BASE_URL)

    _current_run = Run(
        name=name,
        config=config,
        api_key=resolved_api_key,
        base_url=resolved_base_url,
        auto_flush_interval=auto_flush_interval,
        auto_flush_buffer_size=auto_flush_buffer_size,
    )

    return _current_run


def _get_run() -> Run:
    """Get the current run, raising if not initialized."""
    if _current_run is None:
        raise RuntimeError("No active run. Call expt_logger.init() first.")
    return _current_run


def run() -> Run | None:
    """Get the current active run."""
    return _current_run


def config() -> Config:
    """Get the current run's config."""
    return _get_run().config


def log(
    metrics: dict[str, float],
    step: int | None = None,
    mode: str | None = None,
    commit: bool = True,
) -> None:
    """
    Log scalar metrics to the current run.

    Args:
        metrics: Dictionary of metric names to values.
                 Use slash prefix for mode: "train/loss", "eval/accuracy"
        step: Step number. Auto-increments if not provided.
        mode: Default mode for metrics without slash prefix.
              If specified with slash-prefixed keys:
              - Keys matching "mode/**" are logged as "**" under that mode
              - Keys not matching use the explicit mode parameter
        commit: If False, buffer metrics until next commit=True call.

    Example:
        expt_logger.log({"loss": 0.5, "accuracy": 0.9})
        expt_logger.log({"train/loss": 0.5, "eval/loss": 0.6}, step=10)

        # Multiple metrics at same step
        expt_logger.log({"train/loss": 0.5}, commit=False)
        expt_logger.log({"train/acc": 0.9})  # commits both

        # Mode parameter with matching prefix strips it
        expt_logger.log({"train/sampling/logp": 0.5}, mode="train")
        # Logs as: mode="train", type="sampling/logp"
    """
    _get_run().log(metrics, step=step, mode=mode, commit=commit)


def log_rollout(
    prompt: str | dict[str, str],
    messages: list[dict[str, str]] | str,
    rewards: dict[str, float] | list[dict[str, float | str]],
    step: int | None = None,
    mode: str = "train",
) -> None:
    """
    Log a conversation rollout to the current run.

    Args:
        prompt: The prompt text. Can be:
                - A string
                - A message dict with {"role": "...", "content": "..."}
        messages: Either a list of message dicts [{"role": "...", "content": "..."}]
                  or a string that will be parsed into messages.
        rewards: Either a dict {"reward_name": value} or list [{"name": ..., "value": ...}]
        step: Step number. Uses current step if not provided.
        mode: "train" or "eval".

    Example:
        expt_logger.log_rollout(
            prompt="What is 2+2?",
            messages=[
                {"role": "assistant", "content": "2+2 equals 4."},
                {"role": "user", "content": "Thanks!"},
            ],
            rewards={"correctness": 1.0, "clarity": 0.9},
        )

        # Or with dict prompt:
        expt_logger.log_rollout(
            prompt={"role": "user", "content": "What is 2+2?"},
            messages=[{"role": "assistant", "content": "4"}],
            rewards={"correctness": 1.0},
        )

        # Or with string parsing:
        expt_logger.log_rollout(
            prompt="Explain gravity",
            messages="Assistant: Gravity is a force...\\nUser: Can you elaborate?",
            rewards={"quality": 0.8},
        )
    """
    _get_run().log_rollout(prompt, messages, rewards, step=step, mode=mode)


def flush() -> None:
    """Manually flush buffered data to the server."""
    _get_run().flush()


def end() -> None:
    """
    Finish the current run.

    This is called automatically on program exit, but can be called
    explicitly to end a run early.
    """
    global _current_run
    if _current_run is not None:
        _current_run.end()
        _current_run = None
