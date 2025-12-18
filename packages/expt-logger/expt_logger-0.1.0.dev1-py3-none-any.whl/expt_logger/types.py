"""Type definitions for the expt_logger library."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Message:
    """A single message in a conversation."""

    role: str  # "user", "assistant", "system"
    content: str


@dataclass
class Reward:
    """A named reward value."""

    name: str
    value: float


@dataclass
class Scalar:
    """A scalar metric logged at a specific step."""

    step: int
    mode: str
    type: str  # metric name
    value: float


@dataclass
class Rollout:
    """A conversation rollout with rewards."""

    step: int
    mode: str
    prompt_text: str
    messages: list[Message]
    rewards: list[Reward]


@dataclass
class Config:
    """
    Experiment configuration that supports both dict-style and attribute-style access.

    Usage:
        config = Config()
        config.learning_rate = 0.001
        config["batch_size"] = 32
        config.update({"epochs": 10})
    """

    _data: dict[str, Any] = field(default_factory=dict)

    def __setattr__(self, name: str, value: Any) -> None:
        if name == "_data":
            object.__setattr__(self, name, value)
        else:
            self._data[name] = value

    def __getattr__(self, name: str) -> Any:
        if name == "_data":
            return object.__getattribute__(self, name)
        try:
            return self._data[name]
        except KeyError:
            raise AttributeError(f"Config has no attribute '{name}'")

    def __setitem__(self, key: str, value: Any) -> None:
        self._data[key] = value

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def update(self, data: dict[str, Any]) -> None:
        """Update config with a dictionary of values."""
        self._data.update(data)

    def to_dict(self) -> dict[str, Any]:
        """Return config as a plain dictionary."""
        return self._data.copy()

    def __repr__(self) -> str:
        return f"Config({self._data})"
