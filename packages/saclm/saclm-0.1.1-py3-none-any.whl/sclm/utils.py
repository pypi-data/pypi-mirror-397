"""
SCLM Utilities
==============

Helper functions for SCLM models.

Functions:
----------
- load_sclm: Load SCLM model
- save_sclm: Save SCLM model
- count_parameters: Count model parameters
- get_device: Get best available device
- benchmark_memory: Benchmark memory coherence
"""

from typing import Dict, Optional, Union, Any
from pathlib import Path
import time

import torch
import torch.nn as nn


def get_device(prefer_cuda: bool = True) -> torch.device:
    """
    Get the best available device.
    
    Parameters
    ----------
    prefer_cuda : bool
        Prefer CUDA if available
        
    Returns
    -------
    torch.device
        Selected device
    """
    if prefer_cuda and torch.cuda.is_available():
        return torch.device('cuda')
    elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        return torch.device('mps')
    else:
        return torch.device('cpu')


def count_parameters(model: nn.Module, trainable_only: bool = False) -> Dict[str, int]:
    """
    Count parameters in a model.
    
    Parameters
    ----------
    model : nn.Module
        PyTorch model
    trainable_only : bool
        Only count trainable parameters
        
    Returns
    -------
    Dict[str, int]
        Parameter counts
    """
    if trainable_only:
        total = sum(p.numel() for p in model.parameters() if p.requires_grad)
    else:
        total = sum(p.numel() for p in model.parameters())
    
    return {
        'total': total,
        'millions': total / 1e6,
        'billions': total / 1e9,
    }


def load_sclm(
    model_name_or_path: str,
    load_in_4bit: bool = True,
    **kwargs
) -> "SCLMModel":
    """
    Convenience function to load SCLM model.
    
    Parameters
    ----------
    model_name_or_path : str
        HuggingFace model ID or local path
    load_in_4bit : bool
        Use 4-bit quantization
    **kwargs
        Additional loading arguments
        
    Returns
    -------
    SCLMModel
        Loaded model
        
    Example
    -------
    >>> from sclm import load_sclm
    >>> model = load_sclm("mistralai/Mistral-7B-v0.1")
    """
    from .model import SCLMModel
    return SCLMModel.from_pretrained(model_name_or_path, load_in_4bit=load_in_4bit, **kwargs)


def save_sclm(
    model: "SCLMModel",
    path: Union[str, Path],
    save_base_model: bool = False
) -> None:
    """
    Save SCLM model.
    
    Parameters
    ----------
    model : SCLMModel
        Model to save
    path : str or Path
        Save directory
    save_base_model : bool
        Also save full base model weights
    """
    path = Path(path)
    model.save_checkpoint(path)
    
    if save_base_model:
        model.model.base_model.save_pretrained(path / "base_model")


def benchmark_memory(
    model: "SCLMModel",
    contexts: list,
    continuation_prompt: str,
    entities: list,
    n_runs: int = 3
) -> Dict[str, Any]:
    """
    Benchmark SCLM memory coherence.
    
    Parameters
    ----------
    model : SCLMModel
        SCLM model to benchmark
    contexts : list
        List of context strings to add
    continuation_prompt : str
        Prompt for continuation
    entities : list
        Entities to check for in output
    n_runs : int
        Number of runs to average
        
    Returns
    -------
    Dict[str, Any]
        Benchmark results
        
    Example
    -------
    >>> results = benchmark_memory(
    ...     model,
    ...     contexts=[
    ...         "The wizard Elara lives in Silverwood.",
    ...         "Her cat Nimbus has silver fur."
    ...     ],
    ...     continuation_prompt="One day, Elara decided to",
    ...     entities=["elara", "nimbus", "silverwood"]
    ... )
    >>> print(f"Entity retention: {results['entity_retention']:.1%}")
    """
    results = {
        'entity_retention': [],
        'state_norms': [],
        'generation_times': [],
        'outputs': []
    }
    
    for _ in range(n_runs):
        # Reset state
        model.reset_state()
        
        # Add contexts
        state_norms = [0.0]
        for ctx in contexts:
            metrics = model.add_context(ctx)
            state_norms.append(metrics.get('state_norm', model.state_norm))
        
        # Generate
        start = time.time()
        output = model.generate(continuation_prompt, max_new_tokens=50)
        gen_time = time.time() - start
        
        # Check entities
        output_lower = output.lower()
        found = sum(1 for e in entities if e.lower() in output_lower)
        retention = found / len(entities) if entities else 0
        
        results['entity_retention'].append(retention)
        results['state_norms'].append(state_norms)
        results['generation_times'].append(gen_time)
        results['outputs'].append(output)
    
    # Aggregate
    return {
        'entity_retention': sum(results['entity_retention']) / n_runs,
        'avg_generation_time': sum(results['generation_times']) / n_runs,
        'state_evolution': results['state_norms'][-1] if results['state_norms'] else [],
        'sample_output': results['outputs'][0],
        'all_outputs': results['outputs'],
    }


def compare_with_baseline(
    model: "SCLMModel",
    prompt: str,
    context: Optional[str] = None,
    max_new_tokens: int = 50
) -> Dict[str, str]:
    """
    Compare SCLM output with baseline (fresh state).
    
    Parameters
    ----------
    model : SCLMModel
        SCLM model
    prompt : str
        Generation prompt
    context : str, optional
        Context to add before generation
    max_new_tokens : int
        Tokens to generate
        
    Returns
    -------
    Dict[str, str]
        Outputs with and without context
    """
    # With context (if provided)
    model.reset_state()
    if context:
        model.add_context(context)
    with_context = model.generate(prompt, max_new_tokens=max_new_tokens)
    state_with = model.state_norm
    
    # Without context
    model.reset_state()
    without_context = model.generate(prompt, max_new_tokens=max_new_tokens)
    state_without = model.state_norm
    
    return {
        'with_context': with_context,
        'without_context': without_context,
        'state_norm_with': state_with,
        'state_norm_without': state_without,
    }


def visualize_state(
    state: torch.Tensor,
    n_components: int = 10
) -> Dict[str, Any]:
    """
    Analyze and visualize latent state.
    
    Parameters
    ----------
    state : torch.Tensor
        Latent state tensor
    n_components : int
        Number of top components to show
        
    Returns
    -------
    Dict[str, Any]
        State analysis
    """
    state = state.squeeze()
    
    return {
        'norm': state.norm().item(),
        'mean': state.mean().item(),
        'std': state.std().item(),
        'min': state.min().item(),
        'max': state.max().item(),
        'top_indices': state.abs().topk(n_components).indices.tolist(),
        'top_values': state.abs().topk(n_components).values.tolist(),
    }


class MemoryTracker:
    """
    Track SCLM memory state over conversation.
    
    Example
    -------
    >>> tracker = MemoryTracker(model)
    >>> 
    >>> tracker.add("The wizard Elara lives in Silverwood.")
    >>> tracker.add("Her cat Nimbus has silver fur.")
    >>> output = tracker.generate("One day, Elara")
    >>> 
    >>> tracker.plot_state_evolution()  # If matplotlib available
    >>> print(tracker.summary())
    """
    
    def __init__(self, model: "SCLMModel"):
        self.model = model
        self.history = []
        self.model.reset_state()
    
    def add(self, text: str) -> Dict[str, Any]:
        """Add context and record state."""
        metrics = self.model.add_context(text)
        self.history.append({
            'text': text,
            'type': 'context',
            'state_norm': self.model.state_norm,
            'metrics': metrics,
        })
        return metrics
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate and record state."""
        output = self.model.generate(prompt, **kwargs)
        self.history.append({
            'text': prompt,
            'type': 'generation',
            'output': output,
            'state_norm': self.model.state_norm,
        })
        return output
    
    def reset(self) -> None:
        """Reset model and history."""
        self.model.reset_state()
        self.history = []
    
    def summary(self) -> Dict[str, Any]:
        """Get tracking summary."""
        norms = [h['state_norm'] for h in self.history]
        return {
            'n_turns': len(self.history),
            'state_evolution': norms,
            'state_growth': norms[-1] - norms[0] if norms else 0,
            'contexts': [h['text'] for h in self.history if h['type'] == 'context'],
            'generations': [h.get('output', '') for h in self.history if h['type'] == 'generation'],
        }
    
    def plot_state_evolution(self) -> None:
        """Plot state norm evolution (requires matplotlib)."""
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print("matplotlib required for plotting. Install with: pip install matplotlib")
            return
        
        norms = [h['state_norm'] for h in self.history]
        types = [h['type'] for h in self.history]
        
        plt.figure(figsize=(10, 4))
        colors = ['blue' if t == 'context' else 'green' for t in types]
        plt.bar(range(len(norms)), norms, color=colors)
        plt.xlabel('Turn')
        plt.ylabel('State Norm')
        plt.title('SCLM State Evolution')
        plt.legend(['Context', 'Generation'])
        plt.show()
