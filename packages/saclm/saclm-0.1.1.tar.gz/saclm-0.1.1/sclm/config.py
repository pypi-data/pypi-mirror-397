"""
SCLM Configuration
==================

Configuration classes for SCLM models.

Example:
--------
>>> from sclm import SCLMConfig
>>> 
>>> # Default configuration
>>> config = SCLMConfig()
>>> 
>>> # Custom configuration
>>> config = SCLMConfig(
...     latent_state_dim=512,
...     n_experts=4,
...     state_injection_layers=[4, 8, 12, 16],
...     alpha_inject=0.05
... )
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any, Union
from pathlib import Path
import json


@dataclass
class SCLMConfig:
    """
    Configuration for SCLM (Stateful Coherent Language Model).
    
    This configuration controls the EARCP module that adds persistent
    memory capabilities to transformer language models.
    
    Attributes
    ----------
    vocab_size : int
        Vocabulary size of the base model (default: 32000 for Mistral)
    hidden_size : int
        Hidden dimension of the base model (default: 4096 for 7B models)
    num_hidden_layers : int
        Number of transformer layers in base model (default: 32)
    latent_state_dim : int
        Dimension of the persistent latent state vector (default: 256)
    n_experts : int
        Number of coherence experts in MoE layer (default: 2)
    n_coherence_heads : int
        Number of attention heads for state injection (default: 4)
    expert_intermediate : int
        Intermediate dimension in expert FFN (default: 1024)
    state_injection_layers : List[int]
        Which transformer layers receive state injection (default: [8, 16])
    alpha_inject : float
        Injection strength, lower = less perturbation (default: 0.02)
    use_drift_revision : bool
        Whether to use drift detection/correction (default: True)
    use_gating : bool
        Whether to use learnable gating for injection (default: True)
    
    Examples
    --------
    >>> # Minimal config for small models
    >>> config = SCLMConfig(
    ...     hidden_size=2048,
    ...     latent_state_dim=128,
    ...     state_injection_layers=[4, 8]
    ... )
    
    >>> # Full config for large models
    >>> config = SCLMConfig(
    ...     hidden_size=4096,
    ...     latent_state_dim=512,
    ...     n_experts=4,
    ...     state_injection_layers=[8, 16, 24],
    ...     alpha_inject=0.03
    ... )
    
    Notes
    -----
    The default parameters are optimized for Mistral-7B and similar models.
    For smaller models (1-3B), reduce latent_state_dim and n_experts.
    For larger models (13B+), you may increase these values.
    """
    
    # Base model parameters
    vocab_size: int = 32000
    hidden_size: int = 4096
    num_hidden_layers: int = 32
    
    # EARCP parameters
    latent_state_dim: int = 256
    n_experts: int = 2
    n_coherence_heads: int = 4
    expert_intermediate: int = 1024
    
    # Injection parameters
    state_injection_layers: List[int] = field(default_factory=lambda: [8, 16])
    alpha_inject: float = 0.02
    
    # Optional features
    use_drift_revision: bool = True
    use_gating: bool = True
    
    # Model metadata
    base_model_name: Optional[str] = None
    sclm_version: str = "2.0.0"
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.latent_state_dim <= 0:
            raise ValueError(f"latent_state_dim must be positive, got {self.latent_state_dim}")
        if self.n_experts <= 0:
            raise ValueError(f"n_experts must be positive, got {self.n_experts}")
        if self.alpha_inject < 0 or self.alpha_inject > 1:
            raise ValueError(f"alpha_inject must be in [0, 1], got {self.alpha_inject}")
        if not self.state_injection_layers:
            raise ValueError("state_injection_layers cannot be empty")
        for layer in self.state_injection_layers:
            if layer < 0 or layer >= self.num_hidden_layers:
                raise ValueError(
                    f"Invalid injection layer {layer}, must be in [0, {self.num_hidden_layers})"
                )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return asdict(self)
    
    def save(self, path: Union[str, Path]) -> None:
        """
        Save configuration to JSON file.
        
        Parameters
        ----------
        path : str or Path
            Path to save the configuration
        """
        path = Path(path)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load(cls, path: Union[str, Path]) -> "SCLMConfig":
        """
        Load configuration from JSON file.
        
        Parameters
        ----------
        path : str or Path
            Path to the configuration file
            
        Returns
        -------
        SCLMConfig
            Loaded configuration
        """
        path = Path(path)
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls(**data)
    
    @classmethod
    def from_pretrained(cls, model_name_or_path: str) -> "SCLMConfig":
        """
        Load configuration from HuggingFace Hub or local path.
        
        Parameters
        ----------
        model_name_or_path : str
            HuggingFace model ID or local path
            
        Returns
        -------
        SCLMConfig
            Loaded configuration
        """
        from huggingface_hub import hf_hub_download
        
        path = Path(model_name_or_path)
        if path.exists():
            config_path = path / "sclm_config.json"
        else:
            config_path = hf_hub_download(
                repo_id=model_name_or_path,
                filename="sclm_config.json"
            )
        return cls.load(config_path)
    
    def estimate_parameters(self) -> Dict[str, int]:
        """
        Estimate the number of parameters for EARCP module.
        
        Returns
        -------
        dict
            Dictionary with parameter counts for each component
        """
        H = self.hidden_size
        S = self.latent_state_dim
        I = self.expert_intermediate
        N_inj = len(self.state_injection_layers)
        N_exp = self.n_experts
        
        # State Injectors: Q, K, V, O projections + gate
        injector_params = N_inj * (H * H + S * H * 2 + H * H + H)
        
        # Encapsulation: hidden_proj + 3 gates
        encap_params = H * S + (S * 2) * S * 3
        
        # Coherence Experts: router + experts
        coherence_params = H * N_exp + N_exp * (H * I + I * H)
        
        # Drift Revision: drift_score + correction
        drift_params = (H + S) * 256 + 256 + S * H
        
        total = injector_params + encap_params + coherence_params
        if self.use_drift_revision:
            total += drift_params
        
        return {
            "injectors": injector_params,
            "encapsulation": encap_params,
            "coherence": coherence_params,
            "drift_revision": drift_params if self.use_drift_revision else 0,
            "total": total,
            "total_millions": total / 1e6,
        }
    
    def __repr__(self) -> str:
        params = self.estimate_parameters()
        return (
            f"SCLMConfig(\n"
            f"  latent_state_dim={self.latent_state_dim},\n"
            f"  n_experts={self.n_experts},\n"
            f"  injection_layers={self.state_injection_layers},\n"
            f"  alpha={self.alpha_inject},\n"
            f"  estimated_params={params['total_millions']:.1f}M\n"
            f")"
        )


# Preset configurations for common models
PRESETS = {
    "mistral-7b": SCLMConfig(
        vocab_size=32000,
        hidden_size=4096,
        num_hidden_layers=32,
        latent_state_dim=256,
        n_experts=2,
        state_injection_layers=[8, 16],
        alpha_inject=0.02,
        base_model_name="mistralai/Mistral-7B-v0.1",
    ),
    "llama-7b": SCLMConfig(
        vocab_size=32000,
        hidden_size=4096,
        num_hidden_layers=32,
        latent_state_dim=256,
        n_experts=2,
        state_injection_layers=[8, 16],
        alpha_inject=0.02,
        base_model_name="meta-llama/Llama-2-7b-hf",
    ),
    "llama-13b": SCLMConfig(
        vocab_size=32000,
        hidden_size=5120,
        num_hidden_layers=40,
        latent_state_dim=384,
        n_experts=3,
        state_injection_layers=[10, 20, 30],
        alpha_inject=0.02,
        base_model_name="meta-llama/Llama-2-13b-hf",
    ),
    "phi-2": SCLMConfig(
        vocab_size=51200,
        hidden_size=2560,
        num_hidden_layers=32,
        latent_state_dim=192,
        n_experts=2,
        state_injection_layers=[8, 16],
        alpha_inject=0.02,
        base_model_name="microsoft/phi-2",
    ),
    "tiny": SCLMConfig(
        vocab_size=32000,
        hidden_size=768,
        num_hidden_layers=12,
        latent_state_dim=64,
        n_experts=2,
        state_injection_layers=[3, 6, 9],
        alpha_inject=0.03,
    ),
}


def get_preset(name: str) -> SCLMConfig:
    """
    Get a preset configuration by name.
    
    Parameters
    ----------
    name : str
        Preset name: 'mistral-7b', 'llama-7b', 'llama-13b', 'phi-2', 'tiny'
        
    Returns
    -------
    SCLMConfig
        Preset configuration
        
    Raises
    ------
    ValueError
        If preset name is not found
    """
    if name not in PRESETS:
        available = ", ".join(PRESETS.keys())
        raise ValueError(f"Unknown preset '{name}'. Available: {available}")
    return PRESETS[name]
