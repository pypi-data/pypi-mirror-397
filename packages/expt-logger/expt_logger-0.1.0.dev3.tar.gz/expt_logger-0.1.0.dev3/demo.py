#!/usr/bin/env python3
"""
Example usage of the expt_logger library.

This demo simulates GRPO-style RL training with:
- Multiple reward functions
- Train/eval modes with different prompts
- Rollouts with multiple completions per prompt
- Realistic metric trends (loss, accuracy, KL divergence, entropy)
"""

import random
import time

import expt_logger


def simulate_grpo_training() -> None:
    """
    Simulate GRPO-style RL training loop.

    Mimics the pattern from the GRPO trainer:
    - Multiple reward functions (pass@k, format correctness, etc.)
    - Train and eval modes with separate prompt pools
    - Multiple rollouts per prompt
    - Realistic RL metrics (loss, KL, entropy, clip ratios)
    """

    # Initialize with GRPO-like config
    run = expt_logger.init(
        name="grpo-math-training",
        config={
            "model": "Qwen/Qwen2.5-7B-Instruct",
            "learning_rate": 3e-6,
            "batch_size": 8,
            "num_generations": 64,
            "temperature": 0.7,
            "beta": 0.01,
            "epsilon": 0.2,
            "max_prompt_length": 1024,
            "max_completion_length": 2048,
        },
    )

    print(f"Started GRPO run: {run.name} (ID: {run.id})")
    print(f"Config: learning_rate={run.config.learning_rate}, beta={run.config.beta}")

    # Separate train/eval prompt pools (like GRPO)
    train_prompts = [
        "Solve: 2x + 5 = 13",
        "What is the derivative of x^2?",
        "Calculate the area of a circle with radius 5",
        "Simplify: (x^2 - 4) / (x - 2)",
        "Find the roots of x^2 - 5x + 6 = 0",
    ]

    eval_prompts = [
        "Prove that sqrt(2) is irrational",
        "Explain the Pythagorean theorem",
    ]

    num_steps = 50
    num_rollouts_per_prompt = 3  # Like GRPO's num_generations

    for step in range(num_steps):
        progress = step / num_steps

        # === TRAIN MODE ===
        # Select prompts for this step (cycle through)
        train_prompts_this_step = [
            train_prompts[i % len(train_prompts)]
            for i in range(step, step + 2)  # 2 prompts per step
        ]

        # Generate multiple rollouts per prompt (like GRPO)
        for prompt in train_prompts_this_step:
            for rollout_idx in range(num_rollouts_per_prompt):
                # Simulate different completion quality
                is_correct = random.random() > 0.3  # Gets better over time
                is_well_formatted = random.random() > 0.2

                # Completion as a list of message dicts (conversational format)
                completion = [
                    {
                        "role": "assistant",
                        "content": f"Let me solve this step by step:\n"
                        f"Step 1: {'Correct reasoning...' if is_correct else 'Some errors...'}\n"
                        f"Final answer: {random.randint(1, 100)}",
                    }
                ]

                expt_logger.log_rollout(
                    prompt=prompt,
                    messages=completion,
                    rewards={
                        "pass": 1.0 if is_correct else 0.0,
                        "format": 1.0 if is_well_formatted else 0.0,
                    },
                    step=step,
                    mode="train",
                )

        # === EVAL MODE ===
        if step % 5 == 0:  # Eval less frequently
            for prompt in eval_prompts:
                for rollout_idx in range(num_rollouts_per_prompt):
                    is_correct = random.random() > 0.4
                    is_well_formatted = random.random() > 0.25

                    evaluation_response = "Good reasoning" if is_correct else "Needs work"
                    completion = [
                        {
                            "role": "assistant",
                            "content": f"Evaluation response: {evaluation_response}",
                        }
                    ]

                    expt_logger.log_rollout(
                        prompt=prompt,
                        messages=completion,
                        rewards={
                            "pass": 1.0 if is_correct else 0.0,
                            "format": 1.0 if is_well_formatted else 0.0,
                            "advantage": random.uniform(-0.5, 0.5),
                        },
                        step=step,
                        mode="eval",
                    )

        # === LOG METRICS ===
        # Train metrics (realistic RL trends)
        train_loss = max(0.1, 2.0 - progress * 1.7 + random.uniform(-0.3, 0.3))
        train_kl = (
            random.uniform(0, 2.5) if random.random() > 0.05 else random.uniform(5, 20)
        )  # Occasional spikes
        train_entropy = max(0, min(1, 0.5 + random.uniform(-0.2, 0.2)))
        train_clip_ratio = random.uniform(0.05, 0.25)
        mean_reward = 0.3 + progress * 0.55 + random.uniform(-0.1, 0.1)

        expt_logger.log(
            {
                "train/loss": train_loss,
                "train/kl_divergence": train_kl,
                "train/entropy": train_entropy,
                "train/clip_ratio": train_clip_ratio,
                "train/mean_reward": mean_reward,
                "train/pass_rate": min(0.95, 0.3 + progress * 0.6),
            },
            step=step,
        )

        # Eval metrics (less frequent)
        if step % 5 == 0:
            eval_loss = train_loss + random.uniform(0, 0.2)
            eval_mean_reward = mean_reward - random.uniform(0, 0.1)

            expt_logger.log(
                {
                    "eval/loss": eval_loss,
                    "eval/mean_reward": eval_mean_reward,
                    "eval/pass_rate": min(0.90, 0.25 + progress * 0.55),
                },
                step=step,
            )

        print(
            f"Step {step + 1}/{num_steps}: "
            f"loss={train_loss:.4f}, kl={train_kl:.4f}, "
            f"reward={mean_reward:.4f}, "
            f"rollouts={len(train_prompts_this_step) * num_rollouts_per_prompt}"
        )
        time.sleep(0.05)  # Simulate computation

    expt_logger.end()
    print("GRPO training complete!")
    print(f"Total steps: {num_steps}")
    print(f"Total train rollouts: ~{num_steps * 2 * num_rollouts_per_prompt}")
    print(f"Total eval rollouts: ~{(num_steps // 5) * len(eval_prompts) * num_rollouts_per_prompt}")


def demonstrate_commit_behavior() -> None:
    """Show how commit=False works for batching metrics at the same step."""

    with expt_logger.init(name="commit-demo") as run:
        print("\nDemonstrating commit=False for batching metrics:")

        # These all go to the same step (step 0)
        expt_logger.log({"metric_a": 1.0}, commit=False)
        print("  Logged metric_a=1.0 (not committed yet)")

        expt_logger.log({"metric_b": 2.0}, commit=False)
        print("  Logged metric_b=2.0 (not committed yet)")

        expt_logger.log({"metric_c": 3.0})  # This commits all three
        print("  Logged metric_c=3.0 (committed! All 3 metrics at step 0)")

        # Next log goes to step 1
        expt_logger.log({"metric_a": 1.1})
        print("  Logged metric_a=1.1 (step 1)")

        print(f"\nFinal step: {run.step}")


def demonstrate_structured_messages() -> None:
    """Show logging with structured message dicts (like GRPO trainer)."""

    with expt_logger.init(name="structured-messages-demo"):
        print("\nDemonstrating structured message logging:")

        # Log rollout with structured messages (list of dicts)
        expt_logger.log_rollout(
            prompt="What is 2 + 2?",
            messages=[
                {"role": "assistant", "content": "The answer is 4."},
                {"role": "user", "content": "Can you show your work?"},
                {"role": "assistant", "content": "Sure! 2 + 2 = 4"},
            ],
            rewards={"correctness": 1.0, "clarity": 0.9},
            mode="train",
        )
        print("  ✓ Logged rollout with structured messages")

        # Log rollout with plain string (single assistant message)
        expt_logger.log_rollout(
            prompt="Explain photosynthesis",
            messages="Photosynthesis is the process by which plants convert light into energy.",
            rewards={"accuracy": 0.8, "completeness": 0.7},
            mode="eval",
        )
        print("  ✓ Logged rollout with plain string message")

        print("\nTotal rollouts logged: 2")


if __name__ == "__main__":
    import sys

    print("=" * 60)
    print("expt_logger Library Demo - GRPO Style")
    print("=" * 60)

    if len(sys.argv) > 1:
        demo = sys.argv[1]
        if demo == "commit":
            demonstrate_commit_behavior()
        elif demo == "messages":
            demonstrate_structured_messages()
        elif demo == "grpo":
            simulate_grpo_training()
        else:
            print(f"Unknown demo: {demo}")
            print("Available demos:")
            print("  (no args)  - Full GRPO-style training simulation")
            print("  commit     - Show commit=False behavior")
            print("  messages   - Show structured message logging")
            print("  grpo       - Full GRPO simulation (same as default)")
    else:
        simulate_grpo_training()
