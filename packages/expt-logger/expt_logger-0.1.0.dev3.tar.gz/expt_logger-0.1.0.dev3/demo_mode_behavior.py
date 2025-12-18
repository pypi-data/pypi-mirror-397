"""
Demonstration of the new mode parameter behavior with slash-prefixed keys.
"""

from unittest.mock import MagicMock, patch

from expt_logger.run import Run


def demo():
    """Demonstrate the three scenarios for mode parameter behavior."""

    # Mock the client
    with patch("expt_logger.run.Client") as mock_client:
        mock_client_instance = MagicMock()
        mock_client_instance.create_experiment.return_value = "demo-exp-id"
        mock_client.return_value = mock_client_instance

        run = Run(
            name="mode-behavior-demo",
            config=None,
            api_key="demo-key",
            base_url="http://localhost:3000",
        )

        print("=" * 70)
        print("Demo: Mode Parameter Behavior")
        print("=" * 70)

        # Scenario 1: No mode parameter (original behavior)
        print("\n1. No mode parameter - uses parsed mode from key:")
        print('   Input: {"train/sampling/sampling_logp_difference/mean": 0.018}')
        run.log({"train/sampling/sampling_logp_difference/mean": 0.018})
        scalar = run._scalar_buffer[-1]
        print(f"   Result: mode='{scalar.mode}', type='{scalar.type}'")

        # Scenario 2: Mode matches prefix - strips the mode
        print("\n2. Mode matches prefix - strips mode from key:")
        print('   Input: {"train/sampling/sampling_logp_difference/mean": 0.018}, mode="train"')
        run.log({"train/sampling/sampling_logp_difference/mean": 0.018}, mode="train")
        scalar = run._scalar_buffer[-1]
        print(f"   Result: mode='{scalar.mode}', type='{scalar.type}'")

        # Scenario 3: Mode doesn't match prefix - uses explicit mode with full key
        print("\n3. Mode doesn't match prefix - uses explicit mode with full key:")
        print('   Input: {"train/sampling/sampling_logp_difference/mean": 0.018}, mode="eval"')
        run.log({"train/sampling/sampling_logp_difference/mean": 0.018}, mode="eval")
        scalar = run._scalar_buffer[-1]
        print(f"   Result: mode='{scalar.mode}', type='{scalar.type}'")

        # Scenario 4: Multiple metrics with mode parameter
        print("\n4. Multiple metrics with mode parameter:")
        print('   Input: {"train/loss": 0.5, "train/accuracy": 0.9}, mode="train"')
        run._scalar_buffer.clear()  # Clear for clean demo
        run.log({"train/loss": 0.5, "train/accuracy": 0.9}, mode="train")
        for scalar in run._scalar_buffer:
            print(f"   Result: mode='{scalar.mode}', type='{scalar.type}', value={scalar.value}")

        # Scenario 5: No slash with mode parameter
        print("\n5. No slash in key - uses mode parameter:")
        print('   Input: {"loss": 0.5}, mode="eval"')
        run._scalar_buffer.clear()
        run.log({"loss": 0.5}, mode="eval")
        scalar = run._scalar_buffer[-1]
        print(f"   Result: mode='{scalar.mode}', type='{scalar.type}'")

        print("\n" + "=" * 70)
        print("Summary:")
        print("- If mode matches key prefix: strips prefix from metric name")
        print("- If mode doesn't match: uses explicit mode with full key as name")
        print("- If no mode provided: uses parsed mode from key (original behavior)")
        print("=" * 70)


if __name__ == "__main__":
    demo()
