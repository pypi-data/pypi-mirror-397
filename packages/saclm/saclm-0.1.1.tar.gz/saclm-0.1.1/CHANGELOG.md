# Changelog

All notable changes to SCLM will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-12-16

### Added
- **EARCP Architecture**: Complete implementation of Encapsulation, Alignment, Revision, Coherence, Propagation
- **SCLMModel**: High-level API for easy usage
- **SCLMModelV2**: Low-level implementation with full control
- **Option B Architecture**: Deep integration variant with attention/FFN injection
- **Edit Mode**: Freeze state for local editing without memory drift
- **Configuration Presets**: Ready-to-use configs for Mistral-7B, LLaMA-7B/13B, Phi-2
- **CLI Interface**: `sclm chat`, `sclm benchmark`, `sclm info` commands
- **Memory Tracker**: Utility for tracking state evolution across turns
- **Comprehensive Tests**: Unit tests for all components
- **Bilingual Documentation**: English and French documentation

### Changed
- Removed LayerNorm from Encapsulation (allows natural state evolution)
- Reduced default alpha_inject from 0.1 to 0.02 (less perturbation)
- Reduced default injection layers from 4 to 2 (better quality)
- Zero-initialized output projections (start with identity)

### Fixed
- State norm stuck at 16.0 due to LayerNorm normalization
- Gibberish generation from over-injection
- Multi-GPU device mismatch errors
- dtype mismatch (float16 vs float32)

## [1.0.0] - 2025-12-01

### Added
- Initial release
- Basic SCLM wrapper
- Simple state injection

---

## Roadmap

### [2.1.0] - Planned
- NEUROGENESIS: Dynamic state dimension growth
- Training scripts for EARCP fine-tuning
- Gradio demo application

### [3.0.0] - Future
- Multi-modal state (vision-language)
- Hierarchical state levels
- Unsupervised training objectives
