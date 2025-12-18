"""
SCLM Component Tests
====================

Unit tests for SCLM components.

Run with:
    pytest tests/test_components.py -v
"""

import pytest
import torch
import torch.nn as nn

from sclm.config import SCLMConfig, get_preset, PRESETS
from sclm.components import (
    StateInjectionLayer,
    Encapsulation,
    CoherenceExperts,
    DriftRevision,
    EARCPModule,
)


class TestSCLMConfig:
    """Tests for SCLMConfig."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = SCLMConfig()
        assert config.latent_state_dim == 256
        assert config.n_experts == 2
        assert config.alpha_inject == 0.02
        assert len(config.state_injection_layers) == 2
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = SCLMConfig(
            latent_state_dim=512,
            n_experts=4,
            alpha_inject=0.05
        )
        assert config.latent_state_dim == 512
        assert config.n_experts == 4
        assert config.alpha_inject == 0.05
    
    def test_validation(self):
        """Test config validation."""
        with pytest.raises(ValueError):
            SCLMConfig(latent_state_dim=-1)
        
        with pytest.raises(ValueError):
            SCLMConfig(alpha_inject=2.0)
        
        with pytest.raises(ValueError):
            SCLMConfig(state_injection_layers=[])
    
    def test_to_dict(self):
        """Test config serialization."""
        config = SCLMConfig(latent_state_dim=128)
        d = config.to_dict()
        assert d['latent_state_dim'] == 128
        assert 'vocab_size' in d
    
    def test_save_load(self, tmp_path):
        """Test config save and load."""
        config = SCLMConfig(latent_state_dim=192)
        path = tmp_path / "config.json"
        config.save(path)
        
        loaded = SCLMConfig.load(path)
        assert loaded.latent_state_dim == 192
    
    def test_estimate_parameters(self):
        """Test parameter estimation."""
        config = SCLMConfig()
        params = config.estimate_parameters()
        assert 'total' in params
        assert 'total_millions' in params
        assert params['total'] > 0
    
    def test_presets(self):
        """Test configuration presets."""
        for name in PRESETS:
            config = get_preset(name)
            assert isinstance(config, SCLMConfig)
        
        with pytest.raises(ValueError):
            get_preset("nonexistent")


class TestStateInjectionLayer:
    """Tests for StateInjectionLayer."""
    
    @pytest.fixture
    def layer(self):
        return StateInjectionLayer(hidden_size=256, state_dim=64, n_heads=4)
    
    def test_forward_shape(self, layer):
        """Test output shape."""
        hidden = torch.randn(2, 10, 256)
        state = torch.randn(2, 64)
        
        output = layer(hidden, state, alpha=0.02)
        
        assert output.shape == hidden.shape
    
    def test_identity_at_zero_alpha(self, layer):
        """Test that alpha=0 gives identity."""
        hidden = torch.randn(1, 5, 256)
        state = torch.randn(1, 64)
        
        output = layer(hidden, state, alpha=0.0)
        
        # Should be very close to input
        assert torch.allclose(output, hidden, atol=1e-5)
    
    def test_gradients(self, layer):
        """Test gradient flow."""
        hidden = torch.randn(1, 5, 256, requires_grad=True)
        state = torch.randn(1, 64, requires_grad=True)
        
        output = layer(hidden, state)
        loss = output.sum()
        loss.backward()
        
        assert hidden.grad is not None
        assert state.grad is not None


class TestEncapsulation:
    """Tests for Encapsulation."""
    
    @pytest.fixture
    def encap(self):
        return Encapsulation(hidden_size=256, state_dim=64)
    
    def test_forward_shape(self, encap):
        """Test output shape."""
        hidden = torch.randn(2, 10, 256)
        state = torch.randn(2, 64)
        
        new_state, metrics = encap(hidden, state)
        
        assert new_state.shape == state.shape
        assert 'state_change' in metrics
    
    def test_edit_mode(self, encap):
        """Test edit mode preserves state."""
        hidden = torch.randn(1, 5, 256)
        state = torch.randn(1, 64)
        
        new_state, metrics = encap(hidden, state, edit_mode=True)
        
        assert torch.equal(new_state, state)
        assert metrics['state_change'] == 0.0
    
    def test_state_evolves(self, encap):
        """Test state changes with input."""
        hidden = torch.randn(1, 10, 256)
        state = torch.zeros(1, 64)
        
        new_state, metrics = encap(hidden, state)
        
        # State should change
        assert not torch.equal(new_state, state)
        assert metrics['state_change'] > 0


class TestCoherenceExperts:
    """Tests for CoherenceExperts."""
    
    @pytest.fixture
    def moe(self):
        return CoherenceExperts(hidden_size=256, intermediate_size=128, n_experts=2)
    
    def test_forward_shape(self, moe):
        """Test output shape."""
        hidden = torch.randn(2, 10, 256)
        
        output, metrics = moe(hidden)
        
        assert output.shape == hidden.shape
        assert 'expert_weights' in metrics
    
    def test_expert_weights_sum_to_one(self, moe):
        """Test expert weights sum to 1."""
        hidden = torch.randn(1, 5, 256)
        
        _, metrics = moe(hidden)
        
        weights_sum = sum(metrics['expert_weights'])
        assert abs(weights_sum - 1.0) < 1e-5


class TestDriftRevision:
    """Tests for DriftRevision."""
    
    @pytest.fixture
    def drift(self):
        return DriftRevision(hidden_size=256, state_dim=64)
    
    def test_forward_shape(self, drift):
        """Test output shape."""
        hidden = torch.randn(2, 10, 256)
        state = torch.randn(2, 64)
        
        output, metrics = drift(hidden, state)
        
        assert output.shape == hidden.shape
        assert 'drift_score' in metrics
    
    def test_drift_score_range(self, drift):
        """Test drift score is in [0, 1]."""
        hidden = torch.randn(1, 5, 256)
        state = torch.randn(1, 64)
        
        _, metrics = drift(hidden, state)
        
        assert 0 <= metrics['drift_score'] <= 1


class TestEARCPModule:
    """Tests for complete EARCP module."""
    
    @pytest.fixture
    def config(self):
        return SCLMConfig(
            hidden_size=256,
            latent_state_dim=64,
            n_experts=2,
            state_injection_layers=[0, 1],
            num_hidden_layers=4
        )
    
    @pytest.fixture
    def earcp(self, config):
        return EARCPModule(config)
    
    def test_inject_state(self, earcp):
        """Test state injection."""
        hidden = torch.randn(1, 10, 256)
        state = torch.randn(1, 64)
        
        # Layer 0 should inject
        output = earcp.inject_state(hidden, state, layer_idx=0)
        assert output.shape == hidden.shape
        
        # Layer 5 should not inject (not in config)
        output = earcp.inject_state(hidden, state, layer_idx=5)
        assert torch.equal(output, hidden)
    
    def test_update_state(self, earcp):
        """Test full EARCP update."""
        hidden = torch.randn(1, 10, 256)
        state = torch.zeros(1, 64)
        
        new_state, enhanced, metrics = earcp.update_state(hidden, state)
        
        assert new_state.shape == state.shape
        assert enhanced.shape == hidden.shape
        assert 'state_norm' in metrics
        assert 'state_change' in metrics
    
    def test_get_num_params(self, earcp):
        """Test parameter counting."""
        n_params = earcp.get_num_params()
        assert n_params > 0


class TestIntegration:
    """Integration tests."""
    
    def test_full_pipeline(self):
        """Test full EARCP pipeline."""
        config = SCLMConfig(
            hidden_size=128,
            latent_state_dim=32,
            n_experts=2,
            state_injection_layers=[0],
            num_hidden_layers=2
        )
        earcp = EARCPModule(config)
        
        # Simulate multiple turns
        state = torch.zeros(1, 32)
        states = [state.clone()]
        
        for _ in range(5):
            hidden = torch.randn(1, 10, 128)
            
            # Injection
            hidden = earcp.inject_state(hidden, state, layer_idx=0)
            
            # Update
            state, hidden, _ = earcp.update_state(hidden, state)
            states.append(state.clone())
        
        # State should evolve
        initial_norm = states[0].norm().item()
        final_norm = states[-1].norm().item()
        assert final_norm != initial_norm


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
