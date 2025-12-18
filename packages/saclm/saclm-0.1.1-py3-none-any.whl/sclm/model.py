"""
SCLM Model
==========

Main SCLM model classes that wrap HuggingFace transformers with EARCP memory.

Classes:
--------
- SCLMModel: High-level API for easy usage
- SCLMModelV2: Low-level implementation with full control

Example:
--------
>>> from sclm import SCLMModel
>>> 
>>> # Load model with memory
>>> model = SCLMModel.from_pretrained("mistralai/Mistral-7B-v0.1")
>>> 
>>> # Reset state for new conversation
>>> model.reset_state()
>>> 
>>> # Build context
>>> model.add_context("The wizard Elara lives in Silverwood.")
>>> model.add_context("Her cat Nimbus has silver fur.")
>>> 
>>> # Generate with memory
>>> output = model.generate("One day, Elara decided to", max_new_tokens=50)
>>> print(output)
"""

from typing import Dict, List, Optional, Tuple, Any, Union
from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F

from .config import SCLMConfig
from .components import EARCPModule


class SCLMModelV2(nn.Module):
    """
    Low-level SCLM implementation with full control.
    
    Wraps a HuggingFace transformer with EARCP module for persistent memory.
    Use this class when you need fine-grained control over the model.
    
    Parameters
    ----------
    config : SCLMConfig
        SCLM configuration
    base_model : nn.Module
        HuggingFace transformer model
        
    Attributes
    ----------
    config : SCLMConfig
        Configuration
    base_model : nn.Module
        Underlying transformer
    earcp : EARCPModule
        EARCP memory module
    latent_state : torch.Tensor
        Current persistent state
    state_frozen : bool
        Whether state updates are frozen
    edit_mode : bool
        Whether in edit mode
        
    Example
    -------
    >>> from transformers import AutoModelForCausalLM
    >>> from sclm import SCLMConfig, SCLMModelV2
    >>> 
    >>> base = AutoModelForCausalLM.from_pretrained("gpt2")
    >>> config = SCLMConfig(hidden_size=768, num_hidden_layers=12)
    >>> model = SCLMModelV2(config, base)
    """
    
    def __init__(self, config: SCLMConfig, base_model: nn.Module):
        super().__init__()
        self.config = config
        self.base_model = base_model
        
        # Detect device and dtype from base model
        self.model_device = next(base_model.parameters()).device
        self.model_dtype = next(base_model.parameters()).dtype
        
        # Create EARCP module on same device/dtype
        self.earcp = EARCPModule(config).to(self.model_device).to(self.model_dtype)
        
        # Initialize latent state
        self.latent_state = torch.zeros(
            1, config.latent_state_dim,
            device=self.model_device,
            dtype=self.model_dtype
        )
        
        # State management
        self.state_frozen = False
        self.edit_mode = False
        
        # Hook management
        self.hooks = []
        self._setup_hooks()
    
    def _setup_hooks(self) -> None:
        """Setup forward hooks for state injection."""
        def make_hook(layer_idx: int):
            def hook(module, input, output):
                if isinstance(output, tuple) and len(output) > 0:
                    hidden = output[0]
                    B = hidden.size(0)
                    
                    # Get state on correct device/dtype
                    state = self.latent_state.to(hidden.device, hidden.dtype)
                    state = state.expand(B, -1)
                    
                    # Move injector if needed
                    inj_key = str(layer_idx)
                    inj = self.earcp.state_injectors[inj_key]
                    if next(inj.parameters()).device != hidden.device:
                        self.earcp.state_injectors[inj_key] = inj.to(hidden.device)
                    
                    # Apply injection
                    injected = self.earcp.state_injectors[inj_key](
                        hidden, state, self.config.alpha_inject
                    )
                    return (injected,) + output[1:]
                return output
            return hook
        
        # Find decoder layers
        layers = self._get_decoder_layers()
        
        if layers is not None:
            for idx in self.config.state_injection_layers:
                if idx < len(layers):
                    hook = layers[idx].register_forward_hook(make_hook(idx))
                    self.hooks.append(hook)
    
    def _get_decoder_layers(self) -> Optional[nn.ModuleList]:
        """Find decoder layers in base model."""
        # Try common patterns
        if hasattr(self.base_model, 'model'):
            if hasattr(self.base_model.model, 'layers'):
                return self.base_model.model.layers
            if hasattr(self.base_model.model, 'decoder'):
                return self.base_model.model.decoder.layers
        if hasattr(self.base_model, 'transformer'):
            if hasattr(self.base_model.transformer, 'h'):
                return self.base_model.transformer.h
        if hasattr(self.base_model, 'layers'):
            return self.base_model.layers
        return None
    
    def reset_state(self) -> None:
        """Reset latent state to zero."""
        self.latent_state = torch.zeros(
            1, self.config.latent_state_dim,
            device=self.model_device,
            dtype=self.model_dtype
        )
        self.state_frozen = False
        self.edit_mode = False
    
    def freeze_state(self) -> None:
        """Freeze state for editing without memory update."""
        self.state_frozen = True
        self.edit_mode = True
    
    def unfreeze_state(self) -> None:
        """Unfreeze state to resume normal operation."""
        self.state_frozen = False
        self.edit_mode = False
    
    def get_state(self) -> torch.Tensor:
        """Get a copy of current latent state."""
        return self.latent_state.clone()
    
    def set_state(self, state: torch.Tensor) -> None:
        """Set latent state directly."""
        self.latent_state = state.to(self.model_device, self.model_dtype)
    
    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Forward pass with state update.
        
        Parameters
        ----------
        input_ids : torch.Tensor
            Token IDs, shape (batch, seq_len)
        attention_mask : torch.Tensor, optional
            Attention mask
        **kwargs
            Additional arguments for base model
            
        Returns
        -------
        Dict[str, Any]
            - 'logits': Output logits
            - 'earcp_metrics': EARCP metrics
            - 'state': Current state
        """
        if attention_mask is None:
            attention_mask = torch.ones_like(input_ids)
        
        # Forward through base model
        base_out = self.base_model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            output_hidden_states=True,
            **kwargs
        )
        
        # Get final hidden states
        hidden = base_out.hidden_states[-1]
        B = hidden.size(0)
        
        # Move EARCP if needed
        if next(self.earcp.encapsulation.parameters()).device != hidden.device:
            self.earcp = self.earcp.to(hidden.device)
        
        # Get state on correct device
        state = self.latent_state.to(hidden.device, hidden.dtype).expand(B, -1)
        
        # EARCP update
        new_state, enhanced, metrics = self.earcp.update_state(
            hidden, state, self.edit_mode
        )
        
        # Update state if not frozen
        if not self.state_frozen:
            self.latent_state = new_state.mean(dim=0, keepdim=True).detach()
        
        # Combine hidden states (light enhancement)
        combined = hidden + 0.05 * (enhanced - hidden)
        
        # Get logits
        if hasattr(self.base_model, 'lm_head'):
            logits = self.base_model.lm_head(combined)
        else:
            logits = base_out.logits
        
        return {
            'logits': logits,
            'earcp_metrics': metrics,
            'state': self.latent_state.clone()
        }
    
    @torch.no_grad()
    def generate(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        max_new_tokens: int = 50,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 50,
        repetition_penalty: float = 1.1,
        **kwargs
    ) -> torch.Tensor:
        """
        Generate text with memory.
        
        Parameters
        ----------
        input_ids : torch.Tensor
            Input token IDs
        attention_mask : torch.Tensor, optional
            Attention mask
        max_new_tokens : int
            Maximum tokens to generate
        temperature : float
            Sampling temperature
        top_p : float
            Nucleus sampling parameter
        top_k : int
            Top-k sampling parameter
        repetition_penalty : float
            Penalty for repetition
        **kwargs
            Additional generation arguments
            
        Returns
        -------
        torch.Tensor
            Generated token IDs
        """
        self.eval()
        
        if attention_mask is None:
            attention_mask = torch.ones_like(input_ids)
        
        # Update state first
        _ = self.forward(input_ids, attention_mask=attention_mask)
        
        # Generate using base model
        return self.base_model.generate(
            input_ids,
            attention_mask=attention_mask,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            repetition_penalty=repetition_penalty,
            pad_token_id=self.base_model.config.eos_token_id,
            **kwargs
        )
    
    def remove_hooks(self) -> None:
        """Remove all hooks."""
        for hook in self.hooks:
            hook.remove()
        self.hooks = []


class SCLMModel:
    """
    High-level SCLM API for easy usage.
    
    Provides a simple interface for using SCLM with common operations
    like loading models, adding context, and generating text.
    
    Parameters
    ----------
    model : SCLMModelV2
        Underlying SCLM model
    tokenizer : PreTrainedTokenizer
        HuggingFace tokenizer
        
    Example
    -------
    >>> from sclm import SCLMModel
    >>> 
    >>> # Load model
    >>> model = SCLMModel.from_pretrained(
    ...     "mistralai/Mistral-7B-v0.1",
    ...     load_in_4bit=True
    ... )
    >>> 
    >>> # Start new conversation
    >>> model.reset_state()
    >>> 
    >>> # Add context
    >>> model.add_context("The wizard Elara lives in Silverwood forest.")
    >>> model.add_context("Her familiar is a silver cat named Nimbus.")
    >>> 
    >>> # Generate
    >>> output = model.generate("One day, Elara decided to")
    >>> print(output)
    >>> 
    >>> # Check state
    >>> print(f"State norm: {model.state_norm:.2f}")
    """
    
    def __init__(self, model: SCLMModelV2, tokenizer):
        self.model = model
        self.tokenizer = tokenizer
        self._device = model.model_device
    
    @classmethod
    def from_pretrained(
        cls,
        model_name_or_path: str,
        config: Optional[SCLMConfig] = None,
        load_in_4bit: bool = False,
        load_in_8bit: bool = False,
        device_map: str = "auto",
        torch_dtype: torch.dtype = torch.float16,
        **kwargs
    ) -> "SCLMModel":
        """
        Load SCLM from pretrained model.
        
        Parameters
        ----------
        model_name_or_path : str
            HuggingFace model ID or path
        config : SCLMConfig, optional
            Custom SCLM config (auto-detected if None)
        load_in_4bit : bool
            Load in 4-bit quantization
        load_in_8bit : bool
            Load in 8-bit quantization
        device_map : str
            Device mapping strategy
        torch_dtype : torch.dtype
            Data type for model weights
        **kwargs
            Additional arguments for model loading
            
        Returns
        -------
        SCLMModel
            Loaded SCLM model
        """
        from transformers import AutoModelForCausalLM, AutoTokenizer
        
        # Setup quantization
        quantization_config = None
        if load_in_4bit or load_in_8bit:
            try:
                from transformers import BitsAndBytesConfig
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=load_in_4bit,
                    load_in_8bit=load_in_8bit,
                    bnb_4bit_compute_dtype=torch_dtype,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4"
                )
            except ImportError:
                raise ImportError(
                    "bitsandbytes is required for quantization. "
                    "Install with: pip install bitsandbytes"
                )
        
        # Load base model
        base_model = AutoModelForCausalLM.from_pretrained(
            model_name_or_path,
            quantization_config=quantization_config,
            device_map=device_map,
            torch_dtype=torch_dtype,
            trust_remote_code=True,
            **kwargs
        )
        
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        # Create or load SCLM config
        if config is None:
            config = SCLMConfig(
                vocab_size=base_model.config.vocab_size,
                hidden_size=base_model.config.hidden_size,
                num_hidden_layers=base_model.config.num_hidden_layers,
                base_model_name=model_name_or_path,
            )
        
        # Create SCLM model
        sclm = SCLMModelV2(config, base_model)
        
        return cls(sclm, tokenizer)
    
    @classmethod
    def from_sclm_checkpoint(
        cls,
        checkpoint_path: str,
        base_model_name: Optional[str] = None,
        **kwargs
    ) -> "SCLMModel":
        """
        Load SCLM from saved checkpoint with EARCP weights.
        
        Parameters
        ----------
        checkpoint_path : str
            Path to SCLM checkpoint directory
        base_model_name : str, optional
            Override base model name
        **kwargs
            Additional loading arguments
            
        Returns
        -------
        SCLMModel
            Loaded model with EARCP weights
        """
        path = Path(checkpoint_path)
        
        # Load config
        config = SCLMConfig.load(path / "sclm_config.json")
        
        # Override base model if specified
        if base_model_name:
            config.base_model_name = base_model_name
        
        # Load base model + SCLM
        model = cls.from_pretrained(config.base_model_name, config=config, **kwargs)
        
        # Load EARCP weights
        earcp_path = path / "earcp_weights.pt"
        if earcp_path.exists():
            state_dict = torch.load(earcp_path, map_location='cpu')
            model.model.earcp.load_state_dict(state_dict)
            print(f"✅ Loaded EARCP weights from {earcp_path}")
        
        return model
    
    def reset_state(self) -> None:
        """Reset memory state for new conversation."""
        self.model.reset_state()
    
    def freeze_state(self) -> None:
        """Freeze state for editing."""
        self.model.freeze_state()
    
    def unfreeze_state(self) -> None:
        """Unfreeze state."""
        self.model.unfreeze_state()
    
    @property
    def state_norm(self) -> float:
        """Get current state norm."""
        return self.model.latent_state.norm().item()
    
    @property
    def state(self) -> torch.Tensor:
        """Get current state."""
        return self.model.get_state()
    
    def add_context(self, text: str) -> Dict[str, Any]:
        """
        Add context text to memory without generating.
        
        Parameters
        ----------
        text : str
            Context text to add
            
        Returns
        -------
        Dict[str, Any]
            Metrics from state update
        """
        ids = self.tokenizer.encode(text, return_tensors='pt').to(self._device)
        mask = torch.ones_like(ids)
        
        with torch.no_grad():
            out = self.model(ids, attention_mask=mask)
        
        return out['earcp_metrics']
    
    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 50,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        Generate text continuation.
        
        Parameters
        ----------
        prompt : str
            Input prompt
        max_new_tokens : int
            Maximum tokens to generate
        temperature : float
            Sampling temperature
        **kwargs
            Additional generation parameters
            
        Returns
        -------
        str
            Generated text (including prompt)
        """
        ids = self.tokenizer.encode(prompt, return_tensors='pt').to(self._device)
        mask = torch.ones_like(ids)
        
        with torch.no_grad():
            gen_ids = self.model.generate(
                ids,
                attention_mask=mask,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                **kwargs
            )
        
        return self.tokenizer.decode(gen_ids[0], skip_special_tokens=True)
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        max_new_tokens: int = 100,
        **kwargs
    ) -> str:
        """
        Multi-turn chat with memory.
        
        Parameters
        ----------
        messages : List[Dict]
            Chat messages with 'role' and 'content' keys
        max_new_tokens : int
            Maximum response tokens
        **kwargs
            Generation parameters
            
        Returns
        -------
        str
            Assistant response
        """
        # Add all messages to context
        for msg in messages[:-1]:
            self.add_context(f"{msg['role']}: {msg['content']}")
        
        # Generate response for last message
        last = messages[-1]
        prompt = f"{last['role']}: {last['content']}\nassistant:"
        
        response = self.generate(prompt, max_new_tokens=max_new_tokens, **kwargs)
        
        # Extract just the response
        if "assistant:" in response:
            response = response.split("assistant:")[-1].strip()
        
        return response
    
    def save_checkpoint(self, path: Union[str, Path]) -> None:
        """
        Save SCLM checkpoint.
        
        Parameters
        ----------
        path : str or Path
            Directory to save checkpoint
        """
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        
        # Save config
        self.model.config.save(path / "sclm_config.json")
        
        # Save EARCP weights
        earcp_state = {k: v.cpu() for k, v in self.model.earcp.state_dict().items()}
        torch.save(earcp_state, path / "earcp_weights.pt")
        
        # Save tokenizer
        self.tokenizer.save_pretrained(path)
        
        print(f"✅ Checkpoint saved to {path}")
    
    def __repr__(self) -> str:
        params = self.model.earcp.get_num_params()
        return (
            f"SCLMModel(\n"
            f"  base_model={self.model.config.base_model_name},\n"
            f"  earcp_params={params/1e6:.1f}M,\n"
            f"  state_dim={self.model.config.latent_state_dim},\n"
            f"  state_norm={self.state_norm:.2f}\n"
            f")"
        )
