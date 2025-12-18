# Getting Started with SCLM

## Installation

### Basic Installation

```bash
pip install saclm
```

### With Quantization Support

```bash
pip install saclm[quantization]
```

### Full Installation

```bash
pip install saclm[full]
```

### From Source

```bash
git clone https://github.com/Volgat/sclm.git
cd sclm
pip install -e .
```

## Requirements

- Python 3.8+
- PyTorch 2.0+
- transformers 4.35+
- CUDA-capable GPU (recommended, 16GB+ VRAM)

## Quick Start

### 1. Load a Model

```python
from sclm import SCLMModel

# Load with 4-bit quantization (saves VRAM)
model = SCLMModel.from_pretrained(
    "mistralai/Mistral-7B-v0.1",
    load_in_4bit=True
)
```

### 2. Reset State for New Conversation

```python
model.reset_state()
```

### 3. Add Context

```python
# Add information to memory
model.add_context("The wizard Elara lives in Silverwood forest.")
model.add_context("Her familiar is a silver cat named Nimbus.")
model.add_context("She discovered an artifact called the Dragon's Eye.")
```

### 4. Generate with Memory

```python
output = model.generate(
    "One day, Elara decided to",
    max_new_tokens=50,
    temperature=0.7
)
print(output)
# "One day, Elara decided to take Nimbus on a journey to find the Dragon's Eye..."
```

### 5. Check State

```python
print(f"State norm: {model.state_norm:.2f}")
# State norm: 7.54
```

## Core Concepts

### Latent State

SCLM maintains a persistent latent state vector that:
- Starts at zero (norm = 0)
- Evolves with each input (norm increases)
- Captures semantic context
- Persists across generation turns

### State Evolution

```python
model.reset_state()
print(f"Initial: {model.state_norm:.2f}")  # 0.00

model.add_context("The knight wore blue armor.")
print(f"After 1: {model.state_norm:.2f}")  # 4.56

model.add_context("His sword was ancient and magical.")
print(f"After 2: {model.state_norm:.2f}")  # 6.23

model.add_context("The castle stood on the hill.")
print(f"After 3: {model.state_norm:.2f}")  # 7.54
```

### Edit Mode

Make local changes without affecting global memory:

```python
# Establish context
model.add_context("The sword was BLUE.")
state_before = model.state_norm

# Freeze state for editing
model.freeze_state()
output = model.generate("The sword was RED")  # Generates but doesn't update state
state_after = model.state_norm

print(f"State changed: {abs(state_after - state_before) > 0.001}")  # False

# Resume normal operation
model.unfreeze_state()
```

## Configuration

### Custom Configuration

```python
from sclm import SCLMConfig, SCLMModel

config = SCLMConfig(
    latent_state_dim=256,      # State vector size
    n_experts=2,                # MoE experts
    state_injection_layers=[8, 16],  # Injection points
    alpha_inject=0.02,          # Injection strength
)

model = SCLMModel.from_pretrained("model-name", config=config)
```

### Using Presets

```python
from sclm.config import get_preset

# Available presets: mistral-7b, llama-7b, llama-13b, phi-2, tiny
config = get_preset("mistral-7b")
```

## Saving and Loading

### Save Checkpoint

```python
model.save_checkpoint("./my_sclm_model")
```

### Load Checkpoint

```python
model = SCLMModel.from_sclm_checkpoint(
    "./my_sclm_model",
    load_in_4bit=True
)
```

## Next Steps

- [API Reference](api.md)
- [Examples](examples.md)
- [Architecture](architecture.md)
- [FAQ](faq.md)
