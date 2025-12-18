# SCLM: Stateful Coherent Language Models with EARCP Architecture

**Mike Amega**  
Ame Web Studio  
December 2025

---

## Abstract

We introduce **SCLM** (Stateful Coherent Language Model), a novel architecture that augments transformer language models with persistent latent memory. Unlike traditional transformers that process each input independently, SCLM maintains a learned latent state that evolves across conversation turns, enabling improved entity coherence, narrative consistency, and long-range memory without expanding the context window. Our key contribution is the **EARCP** (Encapsulation, Alignment, Revision, Coherence, Propagation) module, a lightweight addition (~2-5% parameter overhead) that can be applied to any pretrained transformer. We demonstrate that SCLM achieves 85% entity retention across multi-turn conversations compared to 45% for baseline models, while maintaining generation quality.

**Keywords:** Language Models, Memory, Transformers, Coherence, Neural Architecture

---

## 1. Introduction

Large Language Models (LLMs) based on the transformer architecture have achieved remarkable performance across diverse NLP tasks. However, a fundamental limitation persists: transformers lack persistent memory across inference steps. Each forward pass operates independently, with context limited to the attention window.

This limitation manifests as:
- **Entity Drift**: Characters and objects change properties unexpectedly
- **Context Loss**: Information from earlier turns disappears
- **Repetition**: Models re-introduce already-stated facts
- **Inconsistency**: Contradictions emerge in long generations

We propose SCLM, which addresses these issues through a persistent latent state that:
1. Evolves with each input using GRU-style updates
2. Injects context into transformer layers via cross-attention
3. Detects and corrects narrative drift
4. Maintains coherence through mixture-of-experts

### 1.1 Contributions

- A novel **EARCP architecture** for adding persistent memory to transformers
- **State injection mechanism** that minimally perturbs base model behavior
- **Edit mode** allowing local changes without global memory updates
- Empirical validation showing 85% entity retention vs 45% baseline

---

## 2. Related Work

### 2.1 Memory-Augmented Neural Networks

Memory Networks (Weston et al., 2015) and Neural Turing Machines (Graves et al., 2014) pioneered external memory for neural networks. However, these require explicit read/write operations and separate memory modules.

### 2.2 Recurrent Approaches

RNNs and LSTMs naturally maintain hidden state but suffer from vanishing gradients and limited parallelization. Transformer-XL (Dai et al., 2019) caches previous segment activations but still lacks a compressed persistent state.

### 2.3 Retrieval Augmentation

RAG (Lewis et al., 2020) retrieves external documents but doesn't maintain evolving conversational state. REALM and similar approaches focus on knowledge retrieval rather than episodic memory.

### 2.4 State Space Models

Mamba (Gu & Dao, 2023) and other SSMs offer linear-time alternatives to attention with implicit state. SCLM differs by adding explicit, interpretable latent state to existing transformers.

---

## 3. Architecture

### 3.1 Overview

SCLM wraps a pretrained transformer $f_\theta$ with an EARCP module $g_\phi$:

$$
y = \text{SCLM}(x, s) = f_\theta(x \mid g_\phi(s))
$$

Where:
- $x$ is the input sequence
- $s \in \mathbb{R}^d$ is the latent state (typically $d=256$)
- $g_\phi$ provides state-conditioned modifications to $f_\theta$

### 3.2 EARCP Module

EARCP consists of five components:

#### 3.2.1 Encapsulation (E)

Updates latent state using GRU-style gating:

$$
z = \sigma(W_z[h; s])
$$
$$
r = \sigma(W_r[h; s])
$$
$$
\tilde{s} = \tanh(W_s[h; r \odot s])
$$
$$
s' = (1-z) \odot s + z \odot \tilde{s}
$$

Where $h = \text{MeanPool}(H)$ projects hidden states to state space.

**Key insight**: We remove LayerNorm from the final state to allow natural evolution. Instead, we apply soft clipping: $s' = 10 \cdot \tanh(s'/10)$.

#### 3.2.2 Alignment (A)

Cross-attention injects state into transformer layers:

$$
Q = H W_Q, \quad K = s W_K, \quad V = s W_V
$$
$$
A = \text{softmax}(QK^T / \sqrt{d_k}) V
$$
$$
H' = H + \alpha \cdot \sigma(g) \cdot W_O A
$$

Where:
- $\alpha = 0.02$ (injection strength)
- $g = W_g H$ (learnable gate)
- $W_O$ is zero-initialized

#### 3.2.3 Revision (R)

Detects and corrects drift:

$$
d = \sigma(\text{MLP}([h; s]))
$$
$$
H' = H + 0.01 \cdot d \cdot W_c s
$$

Where $d \in [0,1]$ is the drift score.

#### 3.2.4 Coherence (C)

Mixture-of-Experts for consistency:

$$
w = \text{softmax}(W_r h)
$$
$$
H' = \sum_{i=1}^{N} w_i \cdot E_i(H)
$$

Where $E_i$ are expert FFNs (typically $N=2$).

#### 3.2.5 Propagation (P)

State is injected at selected transformer layers (typically layers 8 and 16 for a 32-layer model) via forward hooks.

### 3.3 Edit Mode

When frozen, encapsulation returns unchanged state:

$$
s' = s \quad \text{if edit\_mode}
$$

This allows local text modifications without affecting persistent memory.

---

## 4. Implementation

### 4.1 Integration with HuggingFace

SCLM is implemented as a wrapper around HuggingFace transformers:

```python
from sclm import SCLMModel

model = SCLMModel.from_pretrained("mistralai/Mistral-7B-v0.1")
model.reset_state()
model.add_context("The wizard Elara lives in Silverwood.")
output = model.generate("One day, Elara decided to")
```

### 4.2 Hook-Based Injection

State injection uses PyTorch forward hooks:

```python
def make_hook(layer_idx):
    def hook(module, input, output):
        hidden = output[0]
        state = self.latent_state.expand(hidden.size(0), -1)
        injected = self.earcp.inject_state(hidden, state, layer_idx)
        return (injected,) + output[1:]
    return hook
```

### 4.3 Configuration

Key hyperparameters:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `latent_state_dim` | 256 | State vector dimension |
| `n_experts` | 2 | Number of MoE experts |
| `state_injection_layers` | [8, 16] | Injection points |
| `alpha_inject` | 0.02 | Injection strength |
| `expert_intermediate` | 1024 | Expert FFN dimension |

### 4.4 Parameter Efficiency

For Mistral-7B (3.75B params):
- EARCP adds 91.7M parameters (2.4% overhead)
- Memory requirement increase: ~180MB (FP16)

---

## 5. Experiments

### 5.1 Entity Retention Benchmark

**Setup**: 
- Context: 3 sentences introducing entities (characters, locations, objects)
- Prompt: Continuation requiring entity knowledge
- Metric: Percentage of entities appearing in generated text

**Results**:

| Model | Entity Retention | State Evolution |
|-------|-----------------|-----------------|
| Mistral-7B (baseline) | 45% | N/A |
| Mistral-7B + SCLM | 85% | 0→4.6→7.5 |
| LLaMA-7B (baseline) | 43% | N/A |
| LLaMA-7B + SCLM | 83% | 0→4.4→7.2 |

### 5.2 Coherence Across Turns

**Setup**: 5-turn conversation with consistent entity references

| Turn | Baseline Coherence | SCLM Coherence |
|------|-------------------|----------------|
| 1 | 100% | 100% |
| 2 | 78% | 95% |
| 3 | 61% | 91% |
| 4 | 45% | 87% |
| 5 | 34% | 85% |

### 5.3 Generation Quality

Perplexity on WikiText-103 (lower is better):

| Model | Perplexity |
|-------|------------|
| Mistral-7B | 5.21 |
| Mistral-7B + SCLM | 5.24 |

Minimal quality degradation (+0.03 perplexity).

### 5.4 Edit Mode Validation

State preservation when editing:

| Operation | State Diff |
|-----------|-----------|
| Normal update | 0.15-0.25 |
| Edit mode | <1e-5 |

---

## 6. Ablation Studies

### 6.1 Injection Strength

| Alpha | Entity Retention | Generation Quality |
|-------|-----------------|-------------------|
| 0.00 | 45% (baseline) | ✓ |
| 0.02 | 85% | ✓ |
| 0.10 | 82% | ⚠️ Minor degradation |
| 0.30 | 71% | ❌ Gibberish |

**Finding**: α=0.02 provides optimal balance.

### 6.2 Injection Layers

| Layers | Entity Retention | Params |
|--------|-----------------|--------|
| [0] | 62% | 45.8M |
| [8, 16] | 85% | 91.7M |
| [0, 8, 16, 24] | 83% | 183.4M |

**Finding**: Middle layers (8, 16) most effective.

### 6.3 State Dimension

| Dim | Entity Retention | Params |
|-----|-----------------|--------|
| 64 | 71% | 23M |
| 128 | 79% | 46M |
| 256 | 85% | 91M |
| 512 | 86% | 183M |

**Finding**: Diminishing returns above 256.

---

## 7. Architecture Variants

### 7.1 Option A: Hook-Based (Recommended)

- Uses forward hooks for injection
- No modification to base model
- Easy to apply to any HuggingFace model
- Overhead: ~2.5%

### 7.2 Option B: Full Integration

- Modifies transformer forward pass
- Deeper integration with attention
- Potentially better performance
- More complex implementation
- Overhead: ~4-5%

---

## 8. Limitations

1. **Training Required**: EARCP requires fine-tuning for optimal performance
2. **Memory Overhead**: Additional 180MB for state and EARCP weights
3. **Latency**: ~5% inference slowdown from hook overhead
4. **Interpretability**: Latent state is not directly interpretable

---

## 9. Future Work

1. **NEUROGENESIS**: Dynamic growth of state dimension based on context complexity
2. **Multi-Modal State**: Extending to vision-language models
3. **Hierarchical State**: Multiple state levels for different context spans
4. **Unsupervised Training**: Self-supervised objectives for state learning

---

## 10. Conclusion

SCLM demonstrates that persistent latent memory can be added to transformer language models with minimal overhead while significantly improving entity coherence and narrative consistency. The EARCP architecture provides a practical, efficient solution applicable to any pretrained transformer.

---

## References

1. Vaswani, A., et al. (2017). Attention is All You Need. NeurIPS.
2. Dai, Z., et al. (2019). Transformer-XL: Attentive Language Models Beyond a Fixed-Length Context. ACL.
3. Graves, A., et al. (2014). Neural Turing Machines. arXiv.
4. Weston, J., et al. (2015). Memory Networks. ICLR.
5. Lewis, P., et al. (2020). Retrieval-Augmented Generation. NeurIPS.
6. Gu, A., & Dao, T. (2023). Mamba: Linear-Time Sequence Modeling with Selective State Spaces. arXiv.

---

## Appendix A: Full Configuration

```python
SCLMConfig(
    vocab_size=32000,
    hidden_size=4096,
    num_hidden_layers=32,
    latent_state_dim=256,
    n_experts=2,
    n_coherence_heads=4,
    expert_intermediate=1024,
    state_injection_layers=[8, 16],
    alpha_inject=0.02,
    use_drift_revision=True,
    use_gating=True,
)
```

## Appendix B: Code Availability

The SCLM library is available at:
- **PyPI**: `pip install sclm`
- **GitHub**: https://github.com/Volgat/sclm
- **HuggingFace**: https://huggingface.co/amewebstudio/sclm-mistral-7b

---

*© 2025 Mike Amega, Ame Web Studio. MIT License.*
