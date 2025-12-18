"""Tests for input validation in log and log_rollout methods."""

from unittest.mock import MagicMock, patch

import pytest

from src.expt_logger.run import Run


@pytest.fixture
def mock_client():
    """Mock client for testing validation without hitting API."""
    with patch("src.expt_logger.run.Client") as mock_client:
        mock = MagicMock()
        mock_client.return_value = mock
        mock.create_experiment.return_value = "test-id"
        yield mock


class TestLogRolloutValidation:
    """Test validation for log_rollout method."""

    def test_dict_prompt_with_content(self, mock_client):
        """Test that dict prompt with 'content' key works."""
        run = Run(name="test", api_key="test-key")
        run.log_rollout(
            prompt={"role": "user", "content": "What is 2+2?"},
            messages=[{"role": "assistant", "content": "4"}],
            rewards={"correctness": 1.0},
        )
        run.end()

    def test_string_prompt(self, mock_client):
        """Test that string prompt works (existing behavior)."""
        run = Run(name="test", api_key="test-key")
        run.log_rollout(
            prompt="What is 3+3?",
            messages=[{"role": "assistant", "content": "6"}],
            rewards={"correctness": 1.0},
        )
        run.end()

    def test_invalid_prompt_dict_missing_content(self, mock_client):
        """Test that prompt dict without 'content' raises ValueError."""
        run = Run(name="test", api_key="test-key")
        with pytest.raises(ValueError, match="prompt dict must have 'content' key"):
            run.log_rollout(
                prompt={"role": "user"},  # Missing 'content'
                messages=[{"role": "assistant", "content": "test"}],
                rewards={"test": 1.0},
            )
        run.end()

    def test_invalid_prompt_type(self, mock_client):
        """Test that non-string, non-dict prompt raises TypeError."""
        run = Run(name="test", api_key="test-key")
        with pytest.raises(TypeError, match="prompt must be str or dict"):
            run.log_rollout(
                prompt=123,  # type: ignore
                messages=[{"role": "assistant", "content": "test"}],
                rewards={"test": 1.0},
            )
        run.end()

    def test_empty_messages_list(self, mock_client):
        """Test that empty messages list raises ValueError."""
        run = Run(name="test", api_key="test-key")
        with pytest.raises(ValueError, match="messages list cannot be empty"):
            run.log_rollout(
                prompt="test",
                messages=[],
                rewards={"test": 1.0},
            )
        run.end()

    def test_message_missing_role(self, mock_client):
        """Test that message dict without 'role' raises ValueError."""
        run = Run(name="test", api_key="test-key")
        with pytest.raises(ValueError, match="missing required key 'role'"):
            run.log_rollout(
                prompt="test",
                messages=[{"content": "test"}],  # Missing 'role'
                rewards={"test": 1.0},
            )
        run.end()

    def test_message_missing_content(self, mock_client):
        """Test that message dict without 'content' raises ValueError."""
        run = Run(name="test", api_key="test-key")
        with pytest.raises(ValueError, match="missing required key 'content'"):
            run.log_rollout(
                prompt="test",
                messages=[{"role": "assistant"}],  # Missing 'content'
                rewards={"test": 1.0},
            )
        run.end()

    def test_message_invalid_role_type(self, mock_client):
        """Test that message with non-string role raises TypeError."""
        run = Run(name="test", api_key="test-key")
        with pytest.raises(TypeError, match=r"messages\[0\]\['role'\] must be str"):
            run.log_rollout(
                prompt="test",
                messages=[{"role": 123, "content": "test"}],  # type: ignore
                rewards={"test": 1.0},
            )
        run.end()

    def test_message_invalid_content_type(self, mock_client):
        """Test that message with non-string content raises TypeError."""
        run = Run(name="test", api_key="test-key")
        with pytest.raises(TypeError, match=r"messages\[0\]\['content'\] must be str"):
            run.log_rollout(
                prompt="test",
                messages=[{"role": "assistant", "content": 123}],  # type: ignore
                rewards={"test": 1.0},
            )
        run.end()

    def test_invalid_messages_type(self, mock_client):
        """Test that non-list, non-string messages raises TypeError."""
        run = Run(name="test", api_key="test-key")
        with pytest.raises(TypeError, match="messages must be str or list"):
            run.log_rollout(
                prompt="test",
                messages=123,  # type: ignore
                rewards={"test": 1.0},
            )
        run.end()

    def test_empty_rewards_dict(self, mock_client):
        """Test that empty rewards dict raises ValueError."""
        run = Run(name="test", api_key="test-key")
        with pytest.raises(ValueError, match="rewards dict cannot be empty"):
            run.log_rollout(
                prompt="test",
                messages=[{"role": "assistant", "content": "test"}],
                rewards={},
            )
        run.end()

    def test_reward_non_numeric_value(self, mock_client):
        """Test that reward with non-numeric value raises TypeError."""
        run = Run(name="test", api_key="test-key")
        with pytest.raises(TypeError, match="reward 'test' value must be int or float"):
            run.log_rollout(
                prompt="test",
                messages=[{"role": "assistant", "content": "test"}],
                rewards={"test": "not a number"},  # type: ignore
            )
        run.end()

    def test_reward_list_missing_name(self, mock_client):
        """Test that reward list item without 'name' raises ValueError."""
        run = Run(name="test", api_key="test-key")
        with pytest.raises(ValueError, match=r"rewards\[0\] missing required key 'name'"):
            run.log_rollout(
                prompt="test",
                messages=[{"role": "assistant", "content": "test"}],
                rewards=[{"value": 1.0}],  # type: ignore
            )
        run.end()

    def test_reward_list_missing_value(self, mock_client):
        """Test that reward list item without 'value' raises ValueError."""
        run = Run(name="test", api_key="test-key")
        with pytest.raises(ValueError, match=r"rewards\[0\] missing required key 'value'"):
            run.log_rollout(
                prompt="test",
                messages=[{"role": "assistant", "content": "test"}],
                rewards=[{"name": "test"}],  # type: ignore
            )
        run.end()

    def test_reward_list_invalid_value_type(self, mock_client):
        """Test that reward list item with non-numeric value raises TypeError."""
        run = Run(name="test", api_key="test-key")
        with pytest.raises(TypeError, match=r"rewards\[0\]\['value'\] must be int or float"):
            run.log_rollout(
                prompt="test",
                messages=[{"role": "assistant", "content": "test"}],
                rewards=[{"name": "test", "value": "not a number"}],  # type: ignore
            )
        run.end()

    def test_invalid_rewards_type(self, mock_client):
        """Test that non-dict, non-list rewards raises TypeError."""
        run = Run(name="test", api_key="test-key")
        with pytest.raises(TypeError, match="rewards must be dict or list"):
            run.log_rollout(
                prompt="test",
                messages=[{"role": "assistant", "content": "test"}],
                rewards="not valid",  # type: ignore
            )
        run.end()

    def test_invalid_mode_type(self, mock_client):
        """Test that non-string mode raises TypeError."""
        run = Run(name="test", api_key="test-key")
        with pytest.raises(TypeError, match="mode must be str"):
            run.log_rollout(
                prompt="test",
                messages=[{"role": "assistant", "content": "test"}],
                rewards={"test": 1.0},
                mode=123,  # type: ignore
            )
        run.end()


class TestLogValidation:
    """Test validation for log method."""

    def test_valid_metrics(self, mock_client):
        """Test that valid metrics work."""
        run = Run(name="test", api_key="test-key")
        run.log({"loss": 0.5, "accuracy": 0.9})
        run.end()

    def test_invalid_metrics_type(self, mock_client):
        """Test that non-dict metrics raises TypeError."""
        run = Run(name="test", api_key="test-key")
        with pytest.raises(TypeError, match="metrics must be dict"):
            run.log([1, 2, 3])  # type: ignore
        run.end()

    def test_empty_metrics_dict(self, mock_client):
        """Test that empty metrics dict raises ValueError."""
        run = Run(name="test", api_key="test-key")
        with pytest.raises(ValueError, match="metrics dict cannot be empty"):
            run.log({})
        run.end()

    def test_invalid_metric_key_type(self, mock_client):
        """Test that non-string metric key raises TypeError."""
        run = Run(name="test", api_key="test-key")
        with pytest.raises(TypeError, match="metric key must be str"):
            run.log({123: 0.5})  # type: ignore
        run.end()

    def test_empty_metric_key(self, mock_client):
        """Test that empty string metric key raises ValueError."""
        run = Run(name="test", api_key="test-key")
        with pytest.raises(ValueError, match="metric key cannot be empty string"):
            run.log({"": 0.5})
        run.end()

    def test_invalid_metric_value_type(self, mock_client):
        """Test that non-numeric metric value raises TypeError."""
        run = Run(name="test", api_key="test-key")
        with pytest.raises(TypeError, match="metric 'loss' value must be int or float"):
            run.log({"loss": "not a number"})  # type: ignore
        run.end()

    def test_invalid_step_type(self, mock_client):
        """Test that non-int step raises TypeError."""
        run = Run(name="test", api_key="test-key")
        with pytest.raises(TypeError, match="step must be int or None"):
            run.log({"loss": 0.5}, step="not an int")  # type: ignore
        run.end()

    def test_negative_step(self, mock_client):
        """Test that negative step raises ValueError."""
        run = Run(name="test", api_key="test-key")
        with pytest.raises(ValueError, match="step must be non-negative"):
            run.log({"loss": 0.5}, step=-1)
        run.end()

    def test_invalid_mode_type(self, mock_client):
        """Test that non-string mode raises TypeError."""
        run = Run(name="test", api_key="test-key")
        with pytest.raises(TypeError, match="mode must be str or None"):
            run.log({"loss": 0.5}, mode=123)  # type: ignore
        run.end()

    def test_invalid_commit_type(self, mock_client):
        """Test that non-bool commit raises TypeError."""
        run = Run(name="test", api_key="test-key")
        with pytest.raises(TypeError, match="commit must be bool"):
            run.log({"loss": 0.5}, commit="not a bool")  # type: ignore
        run.end()
