"""Unit tests for the expt_logger library."""

import pytest

from expt_logger.types import Config, Message, Reward, Rollout, Scalar
from expt_logger.utils import parse_metric_key


class TestConfig:
    """Tests for the Config class."""

    def test_attribute_access(self) -> None:
        config = Config()
        config.learning_rate = 0.001
        assert config.learning_rate == 0.001

    def test_dict_access(self) -> None:
        config = Config()
        config["batch_size"] = 32
        assert config["batch_size"] == 32

    def test_mixed_access(self) -> None:
        """Test that attribute and dict access work together."""
        config = Config()
        config.learning_rate = 0.001
        assert config["learning_rate"] == 0.001
        config["batch_size"] = 32
        assert config.batch_size == 32

    def test_update(self) -> None:
        config = Config()
        config.update({"a": 1, "b": 2})
        assert config.a == 1
        assert config.b == 2

    def test_to_dict(self) -> None:
        config = Config()
        config.x = 10
        config.y = 20
        assert config.to_dict() == {"x": 10, "y": 20}

    def test_to_dict_empty(self) -> None:
        config = Config()
        assert config.to_dict() == {}

    def test_contains(self) -> None:
        config = Config()
        config.key = "value"
        assert "key" in config
        assert "missing" not in config

    def test_missing_attribute_raises(self) -> None:
        config = Config()
        with pytest.raises(AttributeError):
            _ = config.nonexistent

    def test_missing_dict_key_raises(self) -> None:
        config = Config()
        with pytest.raises(KeyError):
            _ = config["nonexistent"]

    def test_init_from_dict(self) -> None:
        """Test initializing config with a dict."""
        config = Config()
        config.update(
            {
                "model": "Qwen/Qwen2.5-7B-Instruct",
                "learning_rate": 3e-6,
                "batch_size": 8,
            }
        )
        assert config.model == "Qwen/Qwen2.5-7B-Instruct"
        assert config.learning_rate == 3e-6
        assert config.batch_size == 8


class TestParseMetricKey:
    """Tests for parse_metric_key utility."""

    def test_with_mode_prefix(self) -> None:
        assert parse_metric_key("train/loss") == ("train", "loss")
        assert parse_metric_key("eval/accuracy") == ("eval", "accuracy")

    def test_without_prefix(self) -> None:
        """Metrics without slash default to 'train' mode."""
        assert parse_metric_key("loss") == ("train", "loss")
        assert parse_metric_key("accuracy") == ("train", "accuracy")

    def test_nested_slash(self) -> None:
        """Only splits on first slash."""
        assert parse_metric_key("train/model/loss") == ("train", "model/loss")
        assert parse_metric_key("eval/rewards/pass") == ("eval", "rewards/pass")

    def test_empty_metric_name(self) -> None:
        """Edge case: slash at end."""
        assert parse_metric_key("train/") == ("train", "")

    def test_custom_modes(self) -> None:
        """Supports custom mode names."""
        assert parse_metric_key("validation/accuracy") == ("validation", "accuracy")
        assert parse_metric_key("test/f1_score") == ("test", "f1_score")


class TestDataTypes:
    """Tests for data type classes."""

    def test_scalar_creation(self) -> None:
        scalar = Scalar(step=10, mode="train", type="loss", value=0.5)
        assert scalar.step == 10
        assert scalar.mode == "train"
        assert scalar.type == "loss"
        assert scalar.value == 0.5

    def test_message_creation(self) -> None:
        message = Message(role="assistant", content="Hello!")
        assert message.role == "assistant"
        assert message.content == "Hello!"

    def test_reward_creation(self) -> None:
        reward = Reward(name="pass", value=1.0)
        assert reward.name == "pass"
        assert reward.value == 1.0

    def test_rollout_creation(self) -> None:
        messages = [Message(role="assistant", content="Response")]
        rewards = [Reward(name="quality", value=0.9)]

        rollout = Rollout(
            step=5,
            mode="train",
            prompt_text="What is AI?",
            messages=messages,
            rewards=rewards,
        )

        assert rollout.step == 5
        assert rollout.mode == "train"
        assert rollout.prompt_text == "What is AI?"
        assert len(rollout.messages) == 1
        assert len(rollout.rewards) == 1


class TestParseConversationRemoved:
    """Tests verifying that parse_conversation raises NotImplementedError."""

    def test_raises_not_implemented(self) -> None:
        """parse_conversation should raise NotImplementedError."""
        from expt_logger.utils import parse_conversation

        with pytest.raises(NotImplementedError) as exc_info:
            parse_conversation("User: Hello\nAssistant: Hi!")

        assert "not yet implemented" in str(exc_info.value).lower()
        assert "list of dicts" in str(exc_info.value)
