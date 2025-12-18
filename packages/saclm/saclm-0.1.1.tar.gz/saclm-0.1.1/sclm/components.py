"""
SCLM Components - EARCP Architecture
=====================================

This module contains the core components of the EARCP 
(Encapsulation, Alignment, Revision, Coherence, Propagation) architecture.

Components:
-----------
- StateInjectionLayer: Cross-attention for state injection
- Encapsulation: GRU-style state update
- CoherenceExperts: Mixture of Experts for consistency
- DriftRevision: Drift detection and correction
- EARCPModule: Complete EARCP module

Architecture Diagram:
--------------------
```
                    ┌─────────────────┐
                    │  Hidden States  │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
    ┌─────────────────┐ ┌─────────┐ ┌─────────────┐
    │ StateInjection  │ │Encapsul.│ │  Coherence  │
    │   (Alignment)   │ │         │ │  Experts    │
    └────────┬────────┘ └────┬────┘ └──────┬──────┘
             │               │             │
             │               ▼             │
             │        ┌───────────┐        │
             │        │  Latent   │        │
             │        │   State   │        │
             │        └───────────┘        │
             │               │             │
             │               ▼             │
             │        ┌───────────┐        │
             │        │   Drift   │        │
             │        │ Revision  │        │
             │        └─────┬─────┘        │
             │              │              │
             └──────────────┼──────────────┘
                            ▼
                   ┌────────────────┐
                   │ Enhanced Output│
                   └────────────────┘
```
"""

import math
from typing import Dict, Optional, Tuple, Any

import torch
import torch.nn as nn
import torch.nn.functional as F

from .config import SCLMConfig


class StateInjectionLayer(nn.Module):
    """
    Cross-attention layer for injecting latent state into hidden states.
    
    This layer uses multi-head cross-attention where:
    - Query (Q) comes from hidden states
    - Key (K) and Value (V) come from latent state
    
    The injection is gated and scaled by alpha to minimize perturbation.
    
    Parameters
    ----------
    hidden_size : int
        Dimension of hidden states from transformer
    state_dim : int
        Dimension of latent state vector
    n_heads : int, optional
        Number of attention heads (default: 4)
    
    Attributes
    ----------
    n_heads : int
        Number of attention heads
    head_dim : int
        Dimension per head
    q_proj : nn.Linear
        Query projection
    k_proj : nn.Linear
        Key projection from state
    v_proj : nn.Linear
        Value projection from state
    o_proj : nn.Linear
        Output projection (zero-initialized)
    gate : nn.Linear
        Learnable gating mechanism
    
    Example
    -------
    >>> layer = StateInjectionLayer(4096, 256, n_heads=4)
    >>> hidden = torch.randn(1, 10, 4096)  # (batch, seq, hidden)
    >>> state = torch.randn(1, 256)        # (batch, state_dim)
    >>> output = layer(hidden, state, alpha=0.02)
    >>> output.shape
    torch.Size([1, 10, 4096])
    """
    
    def __init__(self, hidden_size: int, state_dim: int, n_heads: int = 4):
        super().__init__()
        self.n_heads = n_heads
        self.head_dim = hidden_size // n_heads
        
        # Projections
        self.q_proj = nn.Linear(hidden_size, hidden_size, bias=False)
        self.k_proj = nn.Linear(state_dim, hidden_size, bias=False)
        self.v_proj = nn.Linear(state_dim, hidden_size, bias=False)
        self.o_proj = nn.Linear(hidden_size, hidden_size, bias=False)
        
        # Gating
        self.gate = nn.Linear(hidden_size, 1)
        
        # Zero-initialize output to start with identity
        nn.init.zeros_(self.o_proj.weight)
    
    def forward(
        self, 
        hidden: torch.Tensor, 
        state: torch.Tensor, 
        alpha: float = 0.02
    ) -> torch.Tensor:
        """
        Apply state injection to hidden states.
        
        Parameters
        ----------
        hidden : torch.Tensor
            Hidden states from transformer, shape (batch, seq_len, hidden_size)
        state : torch.Tensor
            Latent state vector, shape (batch, state_dim)
        alpha : float, optional
            Injection strength (default: 0.02)
            
        Returns
        -------
        torch.Tensor
            Enhanced hidden states, shape (batch, seq_len, hidden_size)
        """
        B, T, H = hidden.shape
        
        # Expand state for cross-attention
        state_exp = state.unsqueeze(1)  # (B, 1, state_dim)
        
        # Project to Q, K, V
        Q = self.q_proj(hidden).view(B, T, self.n_heads, self.head_dim).transpose(1, 2)
        K = self.k_proj(state_exp).view(B, 1, self.n_heads, self.head_dim).transpose(1, 2)
        V = self.v_proj(state_exp).view(B, 1, self.n_heads, self.head_dim).transpose(1, 2)
        
        # Scaled dot-product attention
        scale = math.sqrt(self.head_dim)
        attn_weights = F.softmax(torch.matmul(Q, K.transpose(-2, -1)) / scale, dim=-1)
        attn_output = torch.matmul(attn_weights, V)
        
        # Reshape and project
        attn_output = attn_output.transpose(1, 2).contiguous().view(B, T, H)
        output = self.o_proj(attn_output)
        
        # Gated injection
        gate = torch.sigmoid(self.gate(hidden.mean(dim=1, keepdim=True)))
        
        return hidden + alpha * gate * output


class Encapsulation(nn.Module):
    """
    GRU-style state update mechanism.
    
    Updates the latent state based on new hidden states using gated
    recurrent unit (GRU) style update equations without LayerNorm
    to allow natural state evolution.
    
    Parameters
    ----------
    hidden_size : int
        Dimension of hidden states
    state_dim : int
        Dimension of latent state
    
    Attributes
    ----------
    hidden_proj : nn.Linear
        Projects hidden states to state dimension
    update_gate : nn.Linear
        Computes update gate z
    reset_gate : nn.Linear
        Computes reset gate r
    candidate : nn.Linear
        Computes candidate state
    
    Example
    -------
    >>> encap = Encapsulation(4096, 256)
    >>> hidden = torch.randn(1, 10, 4096)
    >>> state = torch.zeros(1, 256)
    >>> new_state, metrics = encap(hidden, state)
    >>> new_state.shape
    torch.Size([1, 256])
    """
    
    def __init__(self, hidden_size: int, state_dim: int):
        super().__init__()
        self.state_dim = state_dim
        
        # Projection from hidden to state space
        self.hidden_proj = nn.Linear(hidden_size, state_dim)
        
        # GRU-style gates
        self.update_gate = nn.Linear(state_dim * 2, state_dim)
        self.reset_gate = nn.Linear(state_dim * 2, state_dim)
        self.candidate = nn.Linear(state_dim * 2, state_dim)
    
    def forward(
        self, 
        hidden: torch.Tensor, 
        state: torch.Tensor, 
        edit_mode: bool = False
    ) -> Tuple[torch.Tensor, Dict[str, float]]:
        """
        Update latent state based on new hidden states.
        
        Parameters
        ----------
        hidden : torch.Tensor
            Hidden states, shape (batch, seq_len, hidden_size)
        state : torch.Tensor
            Current latent state, shape (batch, state_dim)
        edit_mode : bool, optional
            If True, don't update state (for editing)
            
        Returns
        -------
        Tuple[torch.Tensor, Dict[str, float]]
            - New latent state, shape (batch, state_dim)
            - Metrics dictionary with update statistics
        """
        if edit_mode:
            return state, {
                'update_gate': 0.0, 
                'state_change': 0.0, 
                'state_mean': 0.0, 
                'state_std': 0.0
            }
        
        # Project hidden states (mean pooling)
        h_proj = self.hidden_proj(hidden.mean(dim=1))
        
        # Concatenate for gates
        combined = torch.cat([h_proj, state], dim=-1)
        
        # Compute gates
        z = torch.sigmoid(self.update_gate(combined))  # Update gate
        r = torch.sigmoid(self.reset_gate(combined))   # Reset gate
        
        # Compute candidate
        h_cand = torch.tanh(self.candidate(torch.cat([h_proj, r * state], dim=-1)))
        
        # Update state (GRU formula)
        new_state = (1 - z) * state + z * h_cand
        
        # Soft clipping to prevent explosion while allowing evolution
        new_state = torch.tanh(new_state / 10.0) * 10.0
        
        # Compute metrics
        change = (new_state - state).abs().mean().item()
        
        metrics = {
            'update_gate': z.mean().item(),
            'state_change': change,
            'state_mean': new_state.mean().item(),
            'state_std': new_state.std().item(),
        }
        
        return new_state, metrics


class CoherenceExperts(nn.Module):
    """
    Mixture of Experts (MoE) layer for coherence enhancement.
    
    Uses multiple expert networks with learned routing to enhance
    hidden state coherence based on the current context.
    
    Parameters
    ----------
    hidden_size : int
        Dimension of hidden states
    intermediate_size : int
        Intermediate dimension in expert FFN
    n_experts : int, optional
        Number of experts (default: 2)
    
    Attributes
    ----------
    experts : nn.ModuleList
        List of expert FFN networks
    router : nn.Linear
        Routing network for expert selection
    
    Example
    -------
    >>> moe = CoherenceExperts(4096, 1024, n_experts=2)
    >>> hidden = torch.randn(1, 10, 4096)
    >>> output, metrics = moe(hidden)
    >>> metrics['expert_weights']
    [0.6, 0.4]
    """
    
    def __init__(
        self, 
        hidden_size: int, 
        intermediate_size: int, 
        n_experts: int = 2
    ):
        super().__init__()
        self.n_experts = n_experts
        
        # Expert networks
        self.experts = nn.ModuleList([
            nn.Sequential(
                nn.Linear(hidden_size, intermediate_size, bias=False),
                nn.SiLU(),
                nn.Linear(intermediate_size, hidden_size, bias=False)
            ) for _ in range(n_experts)
        ])
        
        # Router
        self.router = nn.Linear(hidden_size, n_experts)
        
        # Zero-initialize output layers
        for expert in self.experts:
            nn.init.zeros_(expert[-1].weight)
    
    def forward(
        self, 
        hidden: torch.Tensor
    ) -> Tuple[torch.Tensor, Dict[str, Any]]:
        """
        Apply mixture of experts to hidden states.
        
        Parameters
        ----------
        hidden : torch.Tensor
            Hidden states, shape (batch, seq_len, hidden_size)
            
        Returns
        -------
        Tuple[torch.Tensor, Dict]
            - Enhanced hidden states
            - Metrics with expert weights
        """
        # Compute routing weights (based on mean of sequence)
        weights = F.softmax(self.router(hidden.mean(dim=1)), dim=-1)
        
        # Apply each expert
        expert_outputs = torch.stack([expert(hidden) for expert in self.experts], dim=0)
        
        # Weighted combination
        w = weights.T.unsqueeze(-1).unsqueeze(-1)
        output = (w * expert_outputs).sum(dim=0)
        
        metrics = {
            'expert_weights': weights[0].tolist(),
            'expert_entropy': -(weights * (weights + 1e-8).log()).sum(dim=-1).mean().item(),
        }
        
        return output, metrics


class DriftRevision(nn.Module):
    """
    Drift detection and correction module.
    
    Detects when hidden states are drifting from the established
    context and applies corrections based on latent state.
    
    Parameters
    ----------
    hidden_size : int
        Dimension of hidden states
    state_dim : int
        Dimension of latent state
    
    Attributes
    ----------
    drift_score : nn.Sequential
        Network to compute drift score (0-1)
    correction : nn.Linear
        Projects state to hidden space for correction
    
    Example
    -------
    >>> drift = DriftRevision(4096, 256)
    >>> hidden = torch.randn(1, 10, 4096)
    >>> state = torch.randn(1, 256)
    >>> output, metrics = drift(hidden, state)
    >>> metrics['drift_score']
    0.5
    """
    
    def __init__(self, hidden_size: int, state_dim: int):
        super().__init__()
        
        # Drift detection
        self.drift_score = nn.Sequential(
            nn.Linear(hidden_size + state_dim, 256),
            nn.SiLU(),
            nn.Linear(256, 1),
            nn.Sigmoid()
        )
        
        # Correction projection
        self.correction = nn.Linear(state_dim, hidden_size)
        
        # Zero-initialize correction
        nn.init.zeros_(self.correction.weight)
    
    def forward(
        self, 
        hidden: torch.Tensor, 
        state: torch.Tensor
    ) -> Tuple[torch.Tensor, Dict[str, float]]:
        """
        Apply drift detection and correction.
        
        Parameters
        ----------
        hidden : torch.Tensor
            Hidden states, shape (batch, seq_len, hidden_size)
        state : torch.Tensor
            Latent state, shape (batch, state_dim)
            
        Returns
        -------
        Tuple[torch.Tensor, Dict[str, float]]
            - Corrected hidden states
            - Metrics with drift score
        """
        # Compute drift score
        combined = torch.cat([hidden.mean(dim=1), state], dim=-1)
        drift = self.drift_score(combined)
        
        # Compute correction
        corr = self.correction(state).unsqueeze(1)
        
        # Apply proportional correction (light touch)
        output = hidden + drift.unsqueeze(1) * corr * 0.01
        
        metrics = {'drift_score': drift.mean().item()}
        
        return output, metrics


class EARCPModule(nn.Module):
    """
    Complete EARCP module combining all components.
    
    EARCP = Encapsulation + Alignment + Revision + Coherence + Propagation
    
    This module provides:
    - State injection into transformer layers (Alignment/Propagation)
    - State update from hidden states (Encapsulation)
    - Drift detection and correction (Revision)
    - Coherence enhancement via MoE (Coherence)
    
    Parameters
    ----------
    config : SCLMConfig
        Configuration object with all parameters
    
    Attributes
    ----------
    config : SCLMConfig
        Configuration
    state_injectors : nn.ModuleDict
        Injection layers for each configured transformer layer
    encapsulation : Encapsulation
        State update module
    coherence : CoherenceExperts
        MoE coherence module
    revision : DriftRevision
        Drift detection/correction
    
    Example
    -------
    >>> from sclm import SCLMConfig
    >>> config = SCLMConfig(hidden_size=4096, latent_state_dim=256)
    >>> earcp = EARCPModule(config)
    >>> 
    >>> # Inject state at layer 8
    >>> hidden = torch.randn(1, 10, 4096)
    >>> state = torch.randn(1, 256)
    >>> injected = earcp.inject_state(hidden, state, layer_idx=8)
    >>> 
    >>> # Update state
    >>> new_state, enhanced, metrics = earcp.update_state(hidden, state)
    """
    
    def __init__(self, config: SCLMConfig):
        super().__init__()
        self.config = config
        
        H = config.hidden_size
        S = config.latent_state_dim
        
        # State injection layers
        self.state_injectors = nn.ModuleDict({
            str(i): StateInjectionLayer(H, S, config.n_coherence_heads)
            for i in config.state_injection_layers
        })
        
        # Encapsulation
        self.encapsulation = Encapsulation(H, S)
        
        # Coherence experts
        self.coherence = CoherenceExperts(
            H, config.expert_intermediate, config.n_experts
        )
        
        # Drift revision (optional)
        if config.use_drift_revision:
            self.revision = DriftRevision(H, S)
        else:
            self.revision = None
    
    def inject_state(
        self, 
        hidden: torch.Tensor, 
        state: torch.Tensor, 
        layer_idx: int
    ) -> torch.Tensor:
        """
        Inject latent state into hidden states at a specific layer.
        
        Parameters
        ----------
        hidden : torch.Tensor
            Hidden states from transformer layer
        state : torch.Tensor
            Current latent state
        layer_idx : int
            Index of the transformer layer
            
        Returns
        -------
        torch.Tensor
            Enhanced hidden states
        """
        key = str(layer_idx)
        if key in self.state_injectors:
            return self.state_injectors[key](hidden, state, self.config.alpha_inject)
        return hidden
    
    def update_state(
        self, 
        hidden: torch.Tensor, 
        state: torch.Tensor, 
        edit_mode: bool = False
    ) -> Tuple[torch.Tensor, torch.Tensor, Dict[str, Any]]:
        """
        Full EARCP forward pass: update state and enhance hidden states.
        
        Parameters
        ----------
        hidden : torch.Tensor
            Final hidden states from transformer
        state : torch.Tensor
            Current latent state
        edit_mode : bool, optional
            If True, don't update state
            
        Returns
        -------
        Tuple[torch.Tensor, torch.Tensor, Dict]
            - New latent state
            - Enhanced hidden states
            - Combined metrics
        """
        metrics = {}
        
        # Update state via encapsulation
        new_state, m = self.encapsulation(hidden, state, edit_mode)
        metrics.update(m)
        
        # Apply drift revision if enabled
        if self.revision is not None:
            hidden, m = self.revision(hidden, new_state)
            metrics.update(m)
        
        # Apply coherence experts
        hidden, m = self.coherence(hidden)
        metrics.update(m)
        
        # Add state norm to metrics
        metrics['state_norm'] = new_state.norm(dim=-1).mean().item()
        
        return new_state, hidden, metrics
    
    def get_num_params(self) -> int:
        """Get total number of parameters."""
        return sum(p.numel() for p in self.parameters())
