"""Unit tests for the expt_logger library."""

from unittest.mock import MagicMock, patch

import pytest

from expt_logger.run import Run
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


class TestMetricKeyWithMultipleSlashes:
    """Tests for metrics with multiple slashes in the name."""

    def test_complex_nested_metric_key(self) -> None:
        """Test parsing of deeply nested metric names."""
        key = "train/sampling/sampling_logp_difference/mean"
        mode, metric_name = parse_metric_key(key)

        assert mode == "train"
        assert metric_name == "sampling/sampling_logp_difference/mean"

    def test_eval_with_nested_metric(self) -> None:
        """Test eval mode with nested metric name."""
        key = "eval/rewards/quality/avg"
        mode, metric_name = parse_metric_key(key)

        assert mode == "eval"
        assert metric_name == "rewards/quality/avg"

    def test_custom_mode_with_nested_metric(self) -> None:
        """Test custom mode with nested metric name."""
        key = "validation/model/params/total_count"
        mode, metric_name = parse_metric_key(key)

        assert mode == "validation"
        assert metric_name == "model/params/total_count"


class TestRunLogModeConflict:
    """Tests for Run.log() behavior with mode parameter and slash-prefixed keys."""

    @patch("expt_logger.run.Client")
    def test_mode_parameter_matching_prefix_strips_mode(self, mock_client: MagicMock) -> None:
        """Test that mode parameter matching the prefix strips the mode from the key."""
        # Mock the client's create_experiment to return an ID
        mock_client_instance = MagicMock()
        mock_client_instance.create_experiment.return_value = "test-exp-id"
        mock_client.return_value = mock_client_instance

        run = Run(
            name="test-mode-match",
            config=None,
            api_key="test-key",
            base_url="http://localhost:3000",
        )

        # Mode matches the prefix - should strip "train/" from the key
        run.log(
            {"train/sampling/sampling_logp_difference/mean": 0.01809814223088324},
            mode="train",
        )

        # Check that the scalar was buffered correctly
        assert len(run._scalar_buffer) == 1
        scalar = run._scalar_buffer[0]

        # Should use the explicit mode and strip it from the key
        assert scalar.mode == "train"
        assert scalar.type == "sampling/sampling_logp_difference/mean"
        assert scalar.value == 0.01809814223088324

    @patch("expt_logger.run.Client")
    def test_mode_parameter_not_matching_prefix_uses_explicit_mode(
        self, mock_client: MagicMock
    ) -> None:
        """Test that mode parameter not matching prefix uses explicit mode with full key."""
        # Mock the client's create_experiment to return an ID
        mock_client_instance = MagicMock()
        mock_client_instance.create_experiment.return_value = "test-exp-id"
        mock_client.return_value = mock_client_instance

        run = Run(
            name="test-mode-mismatch",
            config=None,
            api_key="test-key",
            base_url="http://localhost:3000",
        )

        # Mode doesn't match the prefix - should use explicit mode with full key as metric name
        run.log(
            {"train/sampling/sampling_logp_difference/mean": 0.01809814223088324},
            mode="eval",
        )

        # Check that the scalar was buffered correctly
        assert len(run._scalar_buffer) == 1
        scalar = run._scalar_buffer[0]

        # Should use the explicit mode and keep the full key as metric name
        assert scalar.mode == "eval"
        assert scalar.type == "train/sampling/sampling_logp_difference/mean"
        assert scalar.value == 0.01809814223088324

    @patch("expt_logger.run.Client")
    def test_nested_slash_metric_without_mode(self, mock_client: MagicMock) -> None:
        """Test that deeply nested metric keys work correctly without mode parameter."""
        # Mock the client
        mock_client_instance = MagicMock()
        mock_client_instance.create_experiment.return_value = "test-exp-id"
        mock_client.return_value = mock_client_instance

        run = Run(
            name="test-nested-metric",
            config=None,
            api_key="test-key",
            base_url="http://localhost:3000",
        )

        # Log metric with nested slashes
        run.log({"train/sampling/sampling_logp_difference/mean": 0.01809814223088324})

        # Check that the scalar was buffered correctly
        assert len(run._scalar_buffer) == 1
        scalar = run._scalar_buffer[0]

        # Should split on FIRST slash only
        assert scalar.mode == "train"
        assert scalar.type == "sampling/sampling_logp_difference/mean"
        assert scalar.value == 0.01809814223088324
        assert scalar.step == 1

    @patch("expt_logger.run.Client")
    def test_mode_parameter_without_slash_keys(self, mock_client: MagicMock) -> None:
        """Test that mode parameter works correctly when keys don't have slashes."""
        # Mock the client
        mock_client_instance = MagicMock()
        mock_client_instance.create_experiment.return_value = "test-exp-id"
        mock_client.return_value = mock_client_instance

        run = Run(
            name="test-mode-without-slash",
            config=None,
            api_key="test-key",
            base_url="http://localhost:3000",
        )

        # Log metrics without slashes but with mode parameter
        run.log({"loss": 0.5, "accuracy": 0.9}, mode="eval")

        # Check that the scalars were buffered correctly
        assert len(run._scalar_buffer) == 2

        # Both should use the mode parameter
        for scalar in run._scalar_buffer:
            assert scalar.mode == "eval"

        # Check specific values
        loss_scalar = next(s for s in run._scalar_buffer if s.type == "loss")
        assert loss_scalar.value == 0.5

        acc_scalar = next(s for s in run._scalar_buffer if s.type == "accuracy")
        assert acc_scalar.value == 0.9

    @patch("expt_logger.run.Client")
    def test_mixed_nested_metrics(self, mock_client: MagicMock) -> None:
        """Test logging multiple metrics with different nesting levels."""
        # Mock the client
        mock_client_instance = MagicMock()
        mock_client_instance.create_experiment.return_value = "test-exp-id"
        mock_client.return_value = mock_client_instance

        run = Run(
            name="test-mixed-metrics",
            config=None,
            api_key="test-key",
            base_url="http://localhost:3000",
        )

        # Log multiple metrics with different nesting
        run.log(
            {
                "train/loss": 0.5,
                "train/sampling/logp": 0.123,
                "eval/rewards/quality/avg": 0.888,
            }
        )

        # Check that all scalars were buffered correctly
        assert len(run._scalar_buffer) == 3

        # Check each scalar
        loss_scalar = next(s for s in run._scalar_buffer if s.type == "loss")
        assert loss_scalar.mode == "train"
        assert loss_scalar.value == 0.5

        logp_scalar = next(s for s in run._scalar_buffer if s.type == "sampling/logp")
        assert logp_scalar.mode == "train"
        assert logp_scalar.value == 0.123

        quality_scalar = next(s for s in run._scalar_buffer if s.type == "rewards/quality/avg")
        assert quality_scalar.mode == "eval"
        assert quality_scalar.value == 0.888
