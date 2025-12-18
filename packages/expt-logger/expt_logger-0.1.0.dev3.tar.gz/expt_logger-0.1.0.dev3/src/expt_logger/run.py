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
        auto_flush_interval: float = 10.0,
        auto_flush_buffer_size: int = 50,
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

        # Auto-flush configuration
        self._auto_flush_interval = auto_flush_interval
        self._auto_flush_buffer_size = auto_flush_buffer_size
        self._flush_timer: threading.Timer | None = None

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

    def _cancel_flush_timer(self) -> None:
        """Cancel the current flush timer if it exists."""
        if self._flush_timer is not None:
            self._flush_timer.cancel()
            self._flush_timer = None

    def _schedule_auto_flush(self) -> None:
        """Schedule an auto-flush after the configured interval."""
        self._cancel_flush_timer()
        self._flush_timer = threading.Timer(self._auto_flush_interval, self._auto_flush)
        self._flush_timer.daemon = True
        self._flush_timer.start()

    def _auto_flush(self) -> None:
        """Auto-flush callback that sends data to server."""
        if not self._finished:
            self.flush()

    def _should_flush_immediately(self) -> bool:
        """Check if buffer size threshold is reached."""
        with self._lock:
            total_items = len(self._scalar_buffer) + len(self._rollout_buffer)
            return total_items >= self._auto_flush_buffer_size

    def _cleanup(self) -> None:
        """Flush buffers and mark experiment as finished."""
        with self._lock:
            if self._finished:
                return
            self._finished = True

        # Cancel any pending flush timer
        self._cancel_flush_timer()

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
                  If specified with slash-prefixed keys:
                  - Keys matching "mode/**" are logged as "**"
                  - Keys not matching use the explicit mode parameter
            commit: If False, buffer metrics until next commit=True call.
                    Useful for logging multiple metrics at the same step.
        """
        if self._finished:
            return

        # Validate metrics
        if not isinstance(metrics, dict):
            raise TypeError(f"metrics must be dict, got {type(metrics).__name__}")
        if not metrics:
            raise ValueError("metrics dict cannot be empty")

        # Validate step
        if step is not None and not isinstance(step, int):
            raise TypeError(f"step must be int or None, got {type(step).__name__}")
        if step is not None and step < 0:
            raise ValueError(f"step must be non-negative, got {step}")

        # Validate mode
        if mode is not None and not isinstance(mode, str):
            raise TypeError(f"mode must be str or None, got {type(mode).__name__}")

        # Validate commit
        if not isinstance(commit, bool):
            raise TypeError(f"commit must be bool, got {type(commit).__name__}")

        # Determine step
        if step is None:
            if self._pending_step is not None:
                step = self._pending_step
            else:
                step = self._current_step

        default_mode = mode or self._pending_mode or "train"

        # Accumulate metrics and validate each one
        for key, value in metrics.items():
            # Validate key
            if not isinstance(key, str):
                raise TypeError(f"metric key must be str, got {type(key).__name__}")
            if not key:
                raise ValueError("metric key cannot be empty string")

            # Validate value
            if not isinstance(value, (int, float)):
                raise TypeError(
                    f"metric '{key}' value must be int or float, "
                    f"got {type(value).__name__}"
                )
            if "/" in key:
                parsed_mode, metric_name = parse_metric_key(key)
                # If mode is explicitly provided and matches the prefix, strip it
                if mode is not None and parsed_mode == mode:
                    final_mode = mode
                    # metric_name already has the prefix stripped
                elif mode is not None:
                    # Mode doesn't match prefix, use explicit mode
                    final_mode = mode
                    # Use the full original key as metric name (with the original prefix)
                    metric_name = key
                else:
                    # No explicit mode, use parsed mode
                    final_mode = parsed_mode
            else:
                # No slash in key, use default mode
                final_mode = default_mode
                metric_name = key

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

        # Check if we should flush immediately or schedule auto-flush
        if self._should_flush_immediately():
            self.flush()
        else:
            self._schedule_auto_flush()

    def log_rollout(
        self,
        prompt: str | dict[str, str],
        messages: list[dict[str, str]] | str,
        rewards: dict[str, float] | list[dict[str, float | str]],
        step: int | None = None,
        mode: str = "train",
    ) -> None:
        """
        Log a conversation rollout.

        Args:
            prompt: The prompt text. Can be:
                    - A string
                    - A message dict with {"role": "...", "content": "..."}
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

        # Validate and extract prompt text
        if isinstance(prompt, dict):
            if not isinstance(prompt, dict):
                raise TypeError(f"prompt must be str or dict, got {type(prompt).__name__}")
            if "content" not in prompt:
                raise ValueError(
                    f"prompt dict must have 'content' key. Got keys: {list(prompt.keys())}"
                )
            if not isinstance(prompt["content"], str):
                raise TypeError(
                    f"prompt['content'] must be str, got {type(prompt['content']).__name__}"
                )
            prompt_text = prompt["content"]
        elif isinstance(prompt, str):
            prompt_text = prompt
        else:
            raise TypeError(f"prompt must be str or dict, got {type(prompt).__name__}")

        # Validate and parse messages
        if isinstance(messages, str):
            parsed = parse_conversation(messages)
        elif isinstance(messages, list):
            if not messages:
                raise ValueError("messages list cannot be empty")
            # Validate each message
            for i, msg in enumerate(messages):
                if not isinstance(msg, dict):
                    raise TypeError(
                        f"messages[{i}] must be dict, got {type(msg).__name__}"
                    )
                if "role" not in msg:
                    raise ValueError(
                        f"messages[{i}] missing required key 'role'. Got keys: {list(msg.keys())}"
                    )
                if "content" not in msg:
                    raise ValueError(
                        f"messages[{i}] missing required key 'content'. "
                        f"Got keys: {list(msg.keys())}"
                    )
                if not isinstance(msg["role"], str):
                    raise TypeError(
                        f"messages[{i}]['role'] must be str, got {type(msg['role']).__name__}"
                    )
                if not isinstance(msg["content"], str):
                    raise TypeError(
                        f"messages[{i}]['content'] must be str, got {type(msg['content']).__name__}"
                    )
            parsed = messages
        else:
            raise TypeError(
                f"messages must be str or list, got {type(messages).__name__}"
            )

        # Convert to Message objects
        message_objs = [Message(role=m["role"], content=m["content"]) for m in parsed]

        # Validate and parse rewards
        if isinstance(rewards, dict):
            if not rewards:
                raise ValueError("rewards dict cannot be empty")
            for key, value in rewards.items():
                if not isinstance(key, str):
                    raise TypeError(
                        f"reward key must be str, got {type(key).__name__}"
                    )
                if not isinstance(value, (int, float)):
                    raise TypeError(
                        f"reward '{key}' value must be int or float, got {type(value).__name__}"
                    )
            reward_objs = [Reward(name=k, value=float(v)) for k, v in rewards.items()]
        elif isinstance(rewards, list):
            if not rewards:
                raise ValueError("rewards list cannot be empty")
            for i, r in enumerate(rewards):
                if not isinstance(r, dict):
                    raise TypeError(
                        f"rewards[{i}] must be dict, got {type(r).__name__}"
                    )
                if "name" not in r:
                    raise ValueError(
                        f"rewards[{i}] missing required key 'name'. Got keys: {list(r.keys())}"
                    )
                if "value" not in r:
                    raise ValueError(
                        f"rewards[{i}] missing required key 'value'. Got keys: {list(r.keys())}"
                    )
                if not isinstance(r["value"], (int, float)):
                    raise TypeError(
                        f"rewards[{i}]['value'] must be int or float, "
                        f"got {type(r['value']).__name__}"
                    )
            reward_objs = [Reward(name=str(r["name"]), value=float(r["value"])) for r in rewards]
        else:
            raise TypeError(
                f"rewards must be dict or list, got {type(rewards).__name__}"
            )

        # Validate mode
        if not isinstance(mode, str):
            raise TypeError(f"mode must be str, got {type(mode).__name__}")

        with self._lock:
            self._rollout_buffer.append(
                Rollout(
                    step=step,
                    mode=mode,
                    prompt_text=prompt_text,
                    messages=message_objs,
                    rewards=reward_objs,
                )
            )

        # Check if we should flush immediately or schedule auto-flush
        if self._should_flush_immediately():
            self.flush()
        else:
            self._schedule_auto_flush()

    def flush(self) -> None:
        """Send all buffered data to the server."""
        if self._experiment_id is None:
            return

        # Cancel any pending flush timer
        self._cancel_flush_timer()

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
