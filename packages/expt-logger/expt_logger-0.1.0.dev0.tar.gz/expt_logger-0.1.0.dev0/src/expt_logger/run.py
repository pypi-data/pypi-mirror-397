"""Run class for experiment tracking."""

from __future__ import annotations

import atexit
import signal
import sys
import threading
from typing import Any

from .client import Client
from .config import DEFAULT_BASE_URL
from .types import Config, Message, Reward, Rollout, Scalar
from .utils import parse_conversation, parse_metric_key


class Run:
    """
    A single experiment run.

    Tracks metrics, rollouts, and configuration for an experiment.
    Handles automatic cleanup on exit or interrupt.
    """

    def __init__(
        self,
        name: str | None = None,
        config: dict[str, Any] | None = None,
        api_key: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
    ):
        self.name = name  # May be None initially; set after server response
        self.config = Config()

        if config:
            self.config.update(config)

        # Internal state
        self._client = Client(base_url=base_url, api_key=api_key)
        self._base_url = base_url
        self._experiment_id: str | None = None
        self._current_step = 1
        self._scalar_buffer: list[Scalar] = []
        self._rollout_buffer: list[Rollout] = []
        self._lock = threading.Lock()
        self._finished = False

        # Track pending metrics for commit=False behavior
        self._pending_metrics: dict[str, float] = {}
        self._pending_step: int | None = None
        self._pending_mode: str | None = None

        # Create experiment on server
        self._init_experiment()

        # Setup exit handlers
        self._setup_exit_handlers()

    def _init_experiment(self) -> None:
        """Create the experiment on the server."""
        # Pass both name and config to the server
        # If name is None, server will generate a random one
        config_dict = self.config.to_dict() if self.config.to_dict() else None
        self._experiment_id = self._client.create_experiment(self.name, config_dict)

    def _setup_exit_handlers(self) -> None:
        """Register cleanup handlers for graceful shutdown."""
        atexit.register(self._cleanup)

        # Store original signal handlers
        self._original_handlers: dict[signal.Signals, Any] = {}

        for sig in (signal.SIGINT, signal.SIGTERM):
            self._original_handlers[sig] = signal.getsignal(sig)
            signal.signal(sig, self._signal_handler)

    def _signal_handler(self, signum: int, frame: Any) -> None:
        """Handle interrupt signals."""
        self._cleanup()

        # Restore original handler and re-raise
        sig = signal.Signals(signum)
        original = self._original_handlers.get(sig)
        signal.signal(sig, original or signal.SIG_DFL)

        if signum == signal.SIGINT:
            raise KeyboardInterrupt
        else:
            sys.exit(128 + signum)

    def _cleanup(self) -> None:
        """Flush buffers and mark experiment as finished."""
        with self._lock:
            if self._finished:
                return
            self._finished = True

        # Commit any pending metrics
        self._commit_pending()

        # Flush remaining data
        self.flush()

        # Mark as finished on server
        if self._experiment_id:
            try:
                self._client.end_experiment(self._experiment_id)
            except Exception:
                pass  # Best effort

        # Cleanup
        self._client.close()

        # Unregister atexit
        try:
            atexit.unregister(self._cleanup)
        except Exception:
            pass

    def log(
        self,
        metrics: dict[str, float],
        step: int | None = None,
        mode: str | None = None,
        commit: bool = True,
    ) -> None:
        """
        Log scalar metrics.

        Args:
            metrics: Dictionary of metric names to values.
                     Use slash prefix for mode: "train/loss", "eval/accuracy"
            step: Step number. Auto-increments if not provided.
            mode: Default mode for metrics without slash prefix.
                  If not specified, defaults to "train".
            commit: If False, buffer metrics until next commit=True call.
                    Useful for logging multiple metrics at the same step.

        Note:
            If mode is specified, all metrics should either have slash prefixes
            or none should have slash prefixes. Mixing both styles is not recommended
            as it may lead to unexpected behavior.
        """
        if self._finished:
            return

        # Check for conflicting usage: mode param with slash-prefixed keys
        has_slash_keys = any("/" in key for key in metrics.keys())
        if mode is not None and has_slash_keys:
            raise ValueError(
                "Cannot specify 'mode' parameter when metric keys contain slashes. "
                "Either use slash-prefixed keys like 'train/loss' OR use the mode "
                "parameter, not both."
            )

        # Determine step
        if step is None:
            if self._pending_step is not None:
                step = self._pending_step
            else:
                step = self._current_step

        default_mode = mode or self._pending_mode or "train"

        # Accumulate metrics
        for key, value in metrics.items():
            parsed_mode, metric_name = parse_metric_key(key)
            # Use parsed mode from key, or fall back to default
            final_mode = parsed_mode if "/" in key else default_mode
            self._pending_metrics[f"{final_mode}/{metric_name}"] = value

        self._pending_step = step
        self._pending_mode = default_mode

        if commit:
            self._commit_pending()

    def _commit_pending(self) -> None:
        """Commit all pending metrics to the buffer."""
        if not self._pending_metrics or self._pending_step is None:
            return

        with self._lock:
            for key, value in self._pending_metrics.items():
                mode, metric_name = parse_metric_key(key)
                self._scalar_buffer.append(
                    Scalar(
                        step=self._pending_step,
                        mode=mode,
                        type=metric_name,
                        value=value,
                    )
                )

            # Auto-increment step for next log call
            self._current_step = self._pending_step + 1

        # Clear pending state
        self._pending_metrics = {}
        self._pending_step = None
        self._pending_mode = None

    def log_rollout(
        self,
        prompt: str,
        messages: list[dict[str, str]] | str,
        rewards: dict[str, float] | list[dict[str, float | str]],
        step: int | None = None,
        mode: str = "train",
    ) -> None:
        """
        Log a conversation rollout.

        Args:
            prompt: The prompt text.
            messages: Either a list of message dicts [{"role": "...", "content": "..."}]
                      or a string that will be parsed into messages.
            rewards: Either a dict {"reward_name": value} or list [{"name": ..., "value": ...}]
            step: Step number. Uses current step if not provided.
            mode: "train" or "eval".
        """
        if self._finished:
            return

        if step is None:
            step = self._current_step

        # Parse messages if string
        if isinstance(messages, str):
            parsed = parse_conversation(messages)
        else:
            parsed = messages

        # Convert to Message objects
        message_objs = [Message(role=m["role"], content=m["content"]) for m in parsed]

        # Parse rewards
        if isinstance(rewards, dict):
            reward_objs = [Reward(name=k, value=v) for k, v in rewards.items()]
        else:
            reward_objs = [Reward(name=str(r["name"]), value=float(r["value"])) for r in rewards]

        with self._lock:
            self._rollout_buffer.append(
                Rollout(
                    step=step,
                    mode=mode,
                    prompt_text=prompt,
                    messages=message_objs,
                    rewards=reward_objs,
                )
            )

    def flush(self) -> None:
        """Send all buffered data to the server."""
        if self._experiment_id is None:
            return

        # Commit any pending metrics first
        self._commit_pending()

        with self._lock:
            scalars = self._scalar_buffer.copy()
            rollouts = self._rollout_buffer.copy()
            self._scalar_buffer.clear()
            self._rollout_buffer.clear()

        # Send to server
        if scalars:
            try:
                self._client.log_scalars(self._experiment_id, scalars)
            except Exception as e:
                print(f"Warning: Failed to log scalars: {e}")

        if rollouts:
            try:
                self._client.log_rollouts(self._experiment_id, rollouts)
            except Exception as e:
                print(f"Warning: Failed to log rollouts: {e}")

    def end(self) -> None:
        """Explicitly finish the run."""
        self._cleanup()

    @property
    def id(self) -> str | None:
        """Return the experiment ID."""
        return self._experiment_id

    @property
    def step(self) -> int:
        """Return the current step."""
        return self._current_step

    @property
    def base_url(self) -> str:
        """Return the base URL of the experiment tracking server."""
        return self._base_url

    @property
    def experiment_url(self) -> str | None:
        """Return the full URL to view this experiment in the web interface."""
        if self._experiment_id is None:
            return None
        # Remove /api prefix if present and construct experiment URL
        base = self._base_url.rstrip("/")
        return f"{base}/experiments/{self._experiment_id}"

    def __enter__(self) -> Run:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.end()
        # Don't suppress exceptions

    def __repr__(self) -> str:
        return f"Run(name={self.name!r}, id={self._experiment_id!r}, step={self._current_step})"
