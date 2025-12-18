"""
Integration tests for expt_logger.

These tests require a running logging server at http://localhost:3000
and will create real experiments in the database.

Run with: pytest tests/test_integration.py -v

To skip if server is not available:
    pytest tests/test_integration.py --skip-if-no-server
"""

import os
import random
import time
from collections.abc import Generator
from typing import Any, cast

import httpx
import pytest

import expt_logger

# Configuration
BASE_URL = os.getenv("EXPT_LOGGER_BASE_URL", "https://expt-platform.vercel.app")
TEST_EMAIL = "test@cgft.io"
TEST_PASSWORD = "pass1Word2!@"

# Test parameters (smaller than populate-db.ts for faster tests)
NUM_EXPERIMENTS = 2
MIN_STEPS = 5
MAX_STEPS = 10
ROLLOUTS_PER_PROMPT = 2


# ============================================================================
# Fixtures
# ============================================================================


def check_server_available() -> bool:
    """Check if the logging server is running."""
    try:
        response = httpx.get(f"{BASE_URL}/api/health", timeout=2)
        return response.status_code == 200
    except (httpx.ConnectError, httpx.TimeoutException):
        return False


@pytest.fixture(scope="session")
def server_available() -> None:
    """Skip tests if server is not available."""
    if not check_server_available():
        pytest.skip(f"Logging server not available at {BASE_URL}")


@pytest.fixture(scope="session")
def api_key(server_available: None) -> str:
    """
    Create test account and get API key.

    This fixture runs once per test session and provides the API key
    for all integration tests.
    """
    # Create account (ignore if already exists)
    try:
        httpx.post(
            f"{BASE_URL}/api/auth/sign-up/email",
            json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD,
                "name": "Test User",
            },
            timeout=5,
        )
    except Exception:
        pass  # Account might already exist

    # Sign in
    response = httpx.post(
        f"{BASE_URL}/api/auth/sign-in/email",
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
        },
        timeout=5,
    )
    assert response.status_code == 200, "Failed to sign in"

    session_cookie = response.headers.get("set-cookie")
    assert session_cookie, "No session cookie received"

    # Create API key
    response = httpx.post(
        f"{BASE_URL}/api/api-keys",
        headers={"Cookie": session_cookie},
        json={"name": "Integration Test Key"},
        timeout=5,
    )
    assert response.status_code == 201, "Failed to create API key"

    data = response.json()
    return cast(str, data["key"])


@pytest.fixture(autouse=True)
def setup_api_key(api_key: str) -> Generator[None, None, None]:
    """Automatically set API key environment variable for each test."""
    os.environ["EXPT_LOGGER_API_KEY"] = api_key
    os.environ["EXPT_LOGGER_BASE_URL"] = BASE_URL
    yield
    # Cleanup is handled by expt_logger.end()


# ============================================================================
# Test Data
# ============================================================================


TRAIN_PROMPTS = [
    "Solve: 2x + 5 = 13",
    "What is the derivative of x^2?",
    "Calculate the area of a circle with radius 5",
    "Simplify: (x^2 - 4) / (x - 2)",
    "Find the roots of x^2 - 5x + 6 = 0",
]

EVAL_PROMPTS = [
    "Prove that sqrt(2) is irrational",
    "Explain the Pythagorean theorem",
]

ASSISTANT_RESPONSES = [
    "Let me solve this step by step:\nStep 1: Isolate the variable\nFinal answer: x = 4",
    "The derivative of x^2 is 2x using the power rule.",
    "Using the formula A = πr², the area is approximately 78.54 square units.",
    "Factoring the numerator: (x+2)(x-2)/(x-2) = x+2 for x ≠ 2",
    "Using the quadratic formula: x = 2 or x = 3",
    "This is a proof by contradiction. Assume sqrt(2) is rational...",
    "The Pythagorean theorem states that a² + b² = c² for right triangles.",
]


# ============================================================================
# Helper Functions
# ============================================================================


def random_float(min_val: float, max_val: float) -> float:
    """Generate random float in range."""
    return min_val + random.random() * (max_val - min_val)


def random_choice(items: list[Any]) -> Any:
    """Select random item from list."""
    return random.choice(items)


def generate_scalars(step: int, num_steps: int, mean_reward: float, mode: str) -> dict[str, float]:
    """
    Generate realistic RL training metrics.

    Mimics the generateScalars function from populate-db.ts
    """
    progress = step / num_steps

    # Loss: starts high, trends down
    base_loss = 2.0 - progress * 1.7
    loss = max(0.1, base_loss + random_float(-0.3, 0.3))

    # Accuracy: starts low, trends up
    base_accuracy = 0.3 + progress * 0.55
    accuracy = min(0.95, max(0.1, base_accuracy + random_float(-0.1, 0.1)))

    # KL Divergence: oscillates with occasional spikes
    kl = random_float(0, 2.5)
    if random.random() < 0.05:
        kl = random_float(5, 20)  # Occasional spike

    # Entropy: moderate stable values
    entropy = min(1, max(0, 0.5 + random_float(-0.2, 0.2)))

    return {
        f"{mode}/loss": loss,
        f"{mode}/accuracy": accuracy,
        f"{mode}/kl_divergence": kl,
        f"{mode}/entropy": entropy,
        f"{mode}/mean_reward": mean_reward,
    }


# ============================================================================
# Integration Tests
# ============================================================================


class TestBasicLogging:
    """Test basic logging functionality with real server."""

    def test_init_and_finish(self) -> None:
        """Test experiment creation and cleanup."""
        run = expt_logger.init(
            name="test-basic-init",
            config={"test": True, "value": 123},
        )

        assert run.id is not None
        assert run.name == "test-basic-init"
        assert run.config.test is True
        assert run.config.value == 123

        expt_logger.end()

    def test_log_scalars(self) -> None:
        """Test logging scalar metrics."""
        run = expt_logger.init(name="test-scalars")

        # Log some metrics
        expt_logger.log({"train/loss": 1.5, "train/accuracy": 0.6})
        expt_logger.log({"train/loss": 1.2, "train/accuracy": 0.7})
        expt_logger.log({"eval/loss": 1.3}, step=2)

        expt_logger.end()

        # Verify run completed
        assert run.id is not None

    def test_log_rollouts(self) -> None:
        """Test logging conversation rollouts."""
        expt_logger.init(name="test-rollouts")

        # Log rollout with structured messages
        expt_logger.log_rollout(
            prompt="What is 2+2?",
            messages=[{"role": "assistant", "content": "The answer is 4."}],
            rewards={"correctness": 1.0, "clarity": 0.9},
            mode="train",
        )

        # Log another rollout with multiple messages
        expt_logger.log_rollout(
            prompt="Explain AI",
            messages=[{"role": "assistant", "content": "AI stands for Artificial Intelligence..."}],
            rewards={"quality": 0.8},
            mode="eval",
        )

        expt_logger.end()

    def test_commit_behavior(self) -> None:
        """Test commit=False batching behavior."""
        run = expt_logger.init(name="test-commit")

        # These all go to step 1 (initial step)
        expt_logger.log({"metric_a": 1.0}, commit=False)
        expt_logger.log({"metric_b": 2.0}, commit=False)
        expt_logger.log({"metric_c": 3.0})  # Commits all

        assert run.step == 2  # Should be at step 2 now (incremented after commit)

        expt_logger.end()


class TestGRPOStyleLogging:
    """
    Test GRPO-style RL training patterns.

    Mimics the populate-db.ts script but with fewer experiments/steps.
    """

    def test_grpo_experiment(self) -> None:
        """
        Run a complete GRPO-style experiment.

        This test mimics the TypeScript populate-db.ts script, logging:
        - Multiple rollouts per prompt
        - Separate train/eval modes
        - Multiple reward functions
        - Realistic metric trends
        """
        num_steps = random.randint(MIN_STEPS, MAX_STEPS)

        # Create experiment with RL config
        expt_logger.init(
            name="test-grpo-training",
            config={
                "model": random_choice(["Qwen/Qwen2.5-7B-Instruct", "Qwen/Qwen2.5-14B-Instruct"]),
                "learning_rate": random_float(1e-6, 1e-4),
                "batch_size": random_choice([4, 8, 16, 32]),
                "num_generations": 64,
                "temperature": 0.7,
                "beta": random_float(0.01, 0.1),
            },
        )

        print(f"\nRunning GRPO experiment: {num_steps} steps")

        # Calculate prompts per step
        train_prompts_per_step = max(1, len(TRAIN_PROMPTS) // 2)
        eval_prompts_per_step = max(1, len(EVAL_PROMPTS) // 2)

        train_prompt_idx = 0
        eval_prompt_idx = 0

        for step in range(num_steps):
            # === TRAIN MODE ===
            train_rollouts = []
            for _ in range(train_prompts_per_step):
                prompt = TRAIN_PROMPTS[train_prompt_idx % len(TRAIN_PROMPTS)]
                train_prompt_idx += 1

                # Multiple rollouts per prompt
                for _ in range(ROLLOUTS_PER_PROMPT):
                    expt_logger.log_rollout(
                        prompt=prompt,
                        messages=[
                            {"role": "assistant", "content": random_choice(ASSISTANT_RESPONSES)}
                        ],
                        rewards={
                            "pass": random_float(0, 1),
                            "format": random_float(0, 1),
                        },
                        step=step,
                        mode="train",
                    )
                    train_rollouts.append(1)

            # === EVAL MODE ===
            eval_rollouts = []
            for _ in range(eval_prompts_per_step):
                prompt = EVAL_PROMPTS[eval_prompt_idx % len(EVAL_PROMPTS)]
                eval_prompt_idx += 1

                for _ in range(ROLLOUTS_PER_PROMPT):
                    expt_logger.log_rollout(
                        prompt=prompt,
                        messages=[
                            {"role": "assistant", "content": random_choice(ASSISTANT_RESPONSES)}
                        ],
                        rewards={
                            "pass": random_float(0, 1),
                            "format": random_float(0, 1),
                        },
                        step=step,
                        mode="eval",
                    )
                    eval_rollouts.append(1)

            # Calculate mean rewards for this step
            train_mean_reward = random_float(0.3, 0.9)
            eval_mean_reward = train_mean_reward - random_float(0, 0.1)

            # Log train scalars
            train_metrics = generate_scalars(step, num_steps, train_mean_reward, "train")
            expt_logger.log(train_metrics, step=step)

            # Log eval scalars
            eval_metrics = generate_scalars(step, num_steps, eval_mean_reward, "eval")
            expt_logger.log(eval_metrics, step=step)

            print(
                f"  Step {step + 1}/{num_steps}: "
                f"train_rollouts={len(train_rollouts)}, "
                f"eval_rollouts={len(eval_rollouts)}"
            )

        expt_logger.end()

        print(f"✓ Completed {num_steps} steps")
        print(f"  Total train rollouts: {num_steps * train_prompts_per_step * ROLLOUTS_PER_PROMPT}")
        print(f"  Total eval rollouts: {num_steps * eval_prompts_per_step * ROLLOUTS_PER_PROMPT}")

    def test_multiple_experiments(self) -> None:
        """Test creating multiple experiments like populate-db.ts."""
        for i in range(NUM_EXPERIMENTS):
            num_steps = random.randint(MIN_STEPS, MAX_STEPS)

            expt_logger.init(
                name=f"test-multi-{i + 1}",
                config={
                    "experiment_num": i + 1,
                    "model": random_choice(
                        ["Qwen/Qwen2.5-7B-Instruct", "Qwen/Qwen2.5-14B-Instruct"]
                    ),
                    "learning_rate": random_float(1e-6, 1e-4),
                },
            )

            print(f"\nExperiment {i + 1}/{NUM_EXPERIMENTS}: {num_steps} steps")

            for step in range(num_steps):
                # Log some rollouts
                expt_logger.log_rollout(
                    prompt=random_choice(TRAIN_PROMPTS),
                    messages=[{"role": "assistant", "content": random_choice(ASSISTANT_RESPONSES)}],
                    rewards={"pass": random_float(0, 1)},
                    step=step,
                    mode="train",
                )

                # Log metrics
                expt_logger.log(
                    generate_scalars(step, num_steps, random_float(0.3, 0.9), "train"),
                    step=step,
                )

            expt_logger.end()
            print(f"  ✓ Completed experiment {i + 1}")


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_auto_generated_name(self) -> None:
        """Test that experiments can be created without a name."""
        run = expt_logger.init(config={"test": True})

        assert run.id is not None
        # Name should be auto-generated by server

        expt_logger.end()

    def test_empty_config(self) -> None:
        """Test creating experiment with no config."""
        run = expt_logger.init(name="test-no-config")

        assert run.id is not None
        assert run.config.to_dict() == {}

        expt_logger.end()

    def test_context_manager(self) -> None:
        """Test using Run as context manager."""
        with expt_logger.init(name="test-context") as run:
            expt_logger.log({"metric": 1.0})
            assert run.id is not None

        # Should auto-finish after context

    def test_multiple_reward_functions(self) -> None:
        """Test logging rollouts with many reward functions (like GRPO)."""
        expt_logger.init(name="test-many-rewards")

        expt_logger.log_rollout(
            prompt="Test prompt",
            messages=[{"role": "assistant", "content": "Response"}],
            rewards={
                "pass": 1.0,
                "format": 0.9,
                "correctness": 0.8,
                "clarity": 0.7,
                "helpfulness": 0.6,
                "advantage": 0.15,  # GRPO-specific
            },
            mode="train",
        )

        expt_logger.end()


# ============================================================================
# Performance Tests
# ============================================================================


class TestPerformance:
    """Test performance with larger data volumes."""

    @pytest.mark.slow
    def test_many_rollouts(self) -> None:
        """Test logging many rollouts in a single experiment."""
        expt_logger.init(name="test-performance-rollouts")

        num_rollouts = 100
        start_time = time.time()

        for i in range(num_rollouts):
            expt_logger.log_rollout(
                prompt=random_choice(TRAIN_PROMPTS),
                messages=[{"role": "assistant", "content": random_choice(ASSISTANT_RESPONSES)}],
                rewards={"pass": random_float(0, 1)},
                mode="train",
            )

        expt_logger.end()

        elapsed = time.time() - start_time
        rate = num_rollouts / elapsed
        print(f"\n  Logged {num_rollouts} rollouts in {elapsed:.2f}s ({rate:.1f}/s)")

    @pytest.mark.slow
    def test_many_steps(self) -> None:
        """Test logging many training steps."""
        expt_logger.init(name="test-performance-steps")

        num_steps = 100
        start_time = time.time()

        for step in range(num_steps):
            expt_logger.log(
                generate_scalars(step, num_steps, 0.5, "train"),
                step=step,
            )

        expt_logger.end()

        elapsed = time.time() - start_time
        print(f"\n  Logged {num_steps} steps in {elapsed:.2f}s ({num_steps / elapsed:.1f}/s)")
