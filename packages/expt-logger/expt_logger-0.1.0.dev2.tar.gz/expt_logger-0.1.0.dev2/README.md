# expt_logger

Simple experiment tracking for RL training with a W&B-style API.

## Quick Start

**Install:**
```bash
uv add expt-logger
# or
pip install expt-logger
```

**Set your API key:**
```bash
export EXPT_LOGGER_API_KEY=your_api_key
```

**Start logging:**
```python
import expt_logger

# Initialize run with config
run = expt_logger.init(
    name="grpo-math",
    config={"lr": 3e-6, "batch_size": 8}
)

# Get experiment URLs
print(f"View experiment: {run.experiment_url}")
print(f"Base URL: {run.base_url}")

# Log RL rollouts with rewards
expt_logger.log_rollout(
    prompt="What is 2+2?",
    messages=[{"role": "assistant", "content": "The answer is 4."}],
    rewards={"correctness": 1.0, "format": 0.9},
    mode="train"
)

# Log scalar metrics
expt_logger.log({
    "train/loss": 0.45,
    "train/kl": 0.02,
    "train/reward": 0.85
})

expt_logger.end()
```

## Core Features

### Scalar Metrics

Log training metrics with automatic step tracking:

```python
# Auto-increment steps (defaults to "train" mode)
expt_logger.log({"loss": 0.5})      # step 0, train/loss
expt_logger.log({"loss": 0.4})      # step 1, train/loss

# Use slash prefixes for train/eval modes
expt_logger.log({
    "train/loss": 0.5,
    "eval/loss": 0.6
}, step=10)

# Or set mode explicitly
expt_logger.log({"loss": 0.5}, mode="eval")
```

**Note:** Metrics default to `"train"` mode when no mode is specified and keys don't have slash prefixes.

**Batching metrics** at the same step:
```python
expt_logger.log({"metric_a": 1.0}, commit=False)
expt_logger.log({"metric_b": 2.0}, commit=False)
expt_logger.log({"metric_c": 3.0})  # commits all three at step 0
```

### Rollouts (RL-specific)

Log conversation rollouts with multiple reward functions:

```python
expt_logger.log_rollout(
    prompt="Solve: x^2 - 5x + 6 = 0",
    messages=[
        {"role": "assistant", "content": "Let me factor this..."},
        {"role": "user", "content": "Can you verify?"},
        {"role": "assistant", "content": "Sure! (x-2)(x-3) = 0..."}
    ],
    rewards={
        "correctness": 1.0,
        "format": 0.9,
        "helpfulness": 0.85
    },
    step=5,
    mode="train"
)
```

- **Messages format:** List of dicts with `"role"` and `"content"` keys
- **Rewards format:** Dict of reward names to float values
- **Mode:** `"train"` or `"eval"` (default: `"train"`)

### Configuration

Track hyperparameters and update them dynamically:

```python
run = expt_logger.init(config={"lr": 0.001, "batch_size": 32})

# Update config during training
run.config.lr = 0.0005              # attribute style
run.config["epochs"] = 100          # dict style
run.config.update({"model": "gpt2"}) # bulk update
```

### API Key & Server Configuration

**API Key** (required):
```bash
export EXPT_LOGGER_API_KEY=your_api_key
```
Or pass directly:
```python
expt_logger.init(api_key="your_key")
```

**Custom server URL** (optional, for self-hosting):
```bash
export EXPT_LOGGER_BASE_URL=https://your-server.com
```
Or:
```python
expt_logger.init(base_url="https://your-server.com")
```

### Accessing Experiment URLs

Get the experiment URL and base URL from the run object:

```python
run = expt_logger.init(name="my-experiment")

# Get the full experiment URL to view in browser
print(run.experiment_url)
# https://expt-platform.vercel.app/experiments/ccf1f879-50a6-492b-9072-fed6effac731

# Get the base URL of the tracking server
print(run.base_url)
# https://expt-platform.vercel.app
```

## API Reference

### `expt_logger.init()`

```python
init(
    name: str | None = None,
    config: dict[str, Any] | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
    auto_flush_interval: float = 10.0,
    auto_flush_buffer_size: int = 100
) -> Run
```

- `name`: Experiment name (auto-generated if not provided)
- `config`: Initial hyperparameters
- `api_key`: API key (or set `EXPT_LOGGER_API_KEY`)
- `base_url`: Custom server URL (or set `EXPT_LOGGER_BASE_URL`)
- `auto_flush_interval`: Seconds to wait before auto-flushing (default: 10.0)
- `auto_flush_buffer_size`: Number of items that trigger immediate flush (default: 100)

### `expt_logger.log()`

```python
log(
    metrics: dict[str, float],
    step: int | None = None,
    mode: str | None = None,
    commit: bool = True
)
```

- `metrics`: Dict of metric names to values
- `step`: Step number (auto-increments if not provided)
- `mode`: Default mode for keys without slashes (default: `"train"`)
- `commit`: If `False`, buffer metrics until next `commit=True`

### `expt_logger.log_rollout()`

```python
log_rollout(
    prompt: str,
    messages: list[dict[str, str]],
    rewards: dict[str, float],
    step: int | None = None,
    mode: str = "train"
)
```

- `prompt`: The prompt text
- `messages`: List of `{"role": ..., "content": ...}` dicts
- `rewards`: Dict of reward names to values
- `step`: Step number (uses current step if not provided)
- `mode`: `"train"` or `"eval"`

### `expt_logger.flush()` / `expt_logger.end()`

- `flush()`: Manually send buffered data to server
- `end()`: Finish the run (called automatically on exit)

**Note:** Data is automatically flushed to the server using a debouncing mechanism:
- Every `auto_flush_interval` seconds after new data is logged (default: 10 seconds)
- Immediately when the buffer reaches `auto_flush_buffer_size` items (default: 100 items)
- On program exit or when `end()` is called

## Advanced

### Context Manager

Ensures automatic cleanup:

```python
with expt_logger.init(name="my-run") as run:
    expt_logger.log({"loss": 0.5})
# end() called automatically
```

### Graceful Shutdown

The library handles cleanup on:
- Normal exit (`atexit`)
- Ctrl+C (`SIGINT`)
- `SIGTERM`

All buffered data is flushed before exit.

## Development

For local development, see [DEVELOPMENT.md](DEVELOPMENT.md).

Run the demo:

```bash
python demo.py          # GRPO-style training simulation
python demo.py commit   # Batching demo
python demo.py messages # Structured messages demo
```
