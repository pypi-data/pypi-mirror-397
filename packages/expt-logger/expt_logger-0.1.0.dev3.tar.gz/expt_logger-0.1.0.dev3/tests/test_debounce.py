"""Test auto-flush debouncing functionality."""

import time
from unittest.mock import MagicMock, patch

import pytest

from src.expt_logger.run import Run


@pytest.fixture
def mock_client():
    """Create a mocked Client instance."""
    with patch("src.expt_logger.run.Client") as mock_client:
        mock = MagicMock()
        mock_client.return_value = mock
        mock.create_experiment.return_value = "test-id"
        yield mock


def test_auto_flush_on_timer(mock_client):
    """Test that data is flushed after the interval."""
    # Create run with short interval for testing
    run = Run(
        name="test",
        api_key="test-key",
        auto_flush_interval=1.0,  # 1 second
        auto_flush_buffer_size=1000,  # High threshold so it doesn't trigger
    )

    # Log some data
    run.log({"loss": 0.5})

    # Should not have flushed yet
    assert mock_client.log_scalars.call_count == 0

    # Wait for auto-flush
    time.sleep(1.5)

    # Should have flushed
    assert mock_client.log_scalars.call_count == 1

    run.end()


def test_auto_flush_on_buffer_size(mock_client):
    """Test that data is flushed when buffer size is reached."""
    # Create run with small buffer size
    run = Run(
        name="test",
        api_key="test-key",
        auto_flush_interval=1000.0,  # Long interval so it doesn't trigger
        auto_flush_buffer_size=5,  # Small threshold
    )

    # Log data below threshold
    for i in range(4):
        run.log({"loss": float(i)})

    # Should not have flushed yet
    assert mock_client.log_scalars.call_count == 0

    # Log one more to reach threshold
    run.log({"loss": 5.0})

    # Should have flushed immediately
    assert mock_client.log_scalars.call_count == 1

    run.end()


def test_debouncing(mock_client):
    """Test that timer is reset on each new data point."""
    # Create run with 2 second interval
    run = Run(
        name="test",
        api_key="test-key",
        auto_flush_interval=2.0,
        auto_flush_buffer_size=1000,
    )

    # Log data at 0s
    run.log({"loss": 0.0})

    # Wait 1.5s (not enough to trigger)
    time.sleep(1.5)

    # Log more data (should reset timer)
    run.log({"loss": 1.0})

    # Wait another 1.5s (total 3s from first log, but only 1.5s from second)
    time.sleep(1.5)

    # Should not have flushed yet (timer was reset)
    assert mock_client.log_scalars.call_count == 0

    # Wait another 1s (now 2.5s from second log)
    time.sleep(1.0)

    # Should have flushed now
    assert mock_client.log_scalars.call_count == 1

    run.end()


def test_manual_flush_cancels_timer(mock_client):
    """Test that manual flush cancels the auto-flush timer."""
    # Create run
    run = Run(
        name="test",
        api_key="test-key",
        auto_flush_interval=2.0,
        auto_flush_buffer_size=1000,
    )

    # Log data
    run.log({"loss": 0.5})

    # Manually flush
    run.flush()
    assert mock_client.log_scalars.call_count == 1

    # Wait for what would have been auto-flush time
    time.sleep(2.5)

    # Should not have flushed again
    assert mock_client.log_scalars.call_count == 1

    run.end()


def test_flush_on_cleanup(mock_client):
    """Test that data is flushed when run ends."""
    run = Run(
        name="test",
        api_key="test-key",
        auto_flush_interval=1000.0,
        auto_flush_buffer_size=1000,
    )

    # Log data but don't wait for auto-flush
    run.log({"loss": 0.5})
    assert mock_client.log_scalars.call_count == 0

    # End should flush remaining data
    run.end()
    assert mock_client.log_scalars.call_count == 1


def test_rollout_triggers_auto_flush(mock_client):
    """Test that logging rollouts also triggers auto-flush logic."""
    run = Run(
        name="test",
        api_key="test-key",
        auto_flush_interval=1000.0,
        auto_flush_buffer_size=2,  # Small threshold
    )

    # Log one rollout (below threshold)
    run.log_rollout(
        prompt="test",
        messages=[{"role": "assistant", "content": "test"}],
        rewards={"reward": 1.0},
    )
    assert mock_client.log_rollouts.call_count == 0

    # Log another rollout (reaches threshold)
    run.log_rollout(
        prompt="test2",
        messages=[{"role": "assistant", "content": "test2"}],
        rewards={"reward": 0.5},
    )

    # Should have flushed
    assert mock_client.log_rollouts.call_count == 1

    run.end()
