# Guide de Démarrage SCLM

## Installation

### Installation Basique

```bash
pip install saclm
```

### Avec Support Quantification

```bash
pip install saclm[quantization]
```

### Installation Complète

```bash
pip install saclm[full]
```

### Depuis les Sources

```bash
git clone https://github.com/Volgat/sclm.git
cd sclm
pip install -e .
```

## Prérequis

- Python 3.8+
- PyTorch 2.0+
- transformers 4.35+
- GPU compatible CUDA (recommandé, 16GB+ VRAM)

## Démarrage Rapide

### 1. Charger un Modèle

```python
from sclm import SCLMModel

# Charger avec quantification 4-bit (économise la VRAM)
model = SCLMModel.from_pretrained(
    "mistralai/Mistral-7B-v0.1",
    load_in_4bit=True
)
```

### 2. Réinitialiser l'État pour une Nouvelle Conversation

```python
model.reset_state()
```

### 3. Ajouter du Contexte

```python
# Ajouter des informations à la mémoire
model.add_context("Le sorcier Élara vit dans la forêt de Boisargent.")
model.add_context("Son familier est un chat argenté nommé Nimbus.")
model.add_context("Elle a découvert un artefact appelé l'Œil du Dragon.")
```

### 4. Générer avec Mémoire

```python
output = model.generate(
    "Un jour, Élara décida de",
    max_new_tokens=50,
    temperature=0.7
)
print(output)
# "Un jour, Élara décida d'emmener Nimbus en voyage pour retrouver l'Œil du Dragon..."
```

### 5. Vérifier l'État

```python
print(f"Norme de l'état: {model.state_norm:.2f}")
# Norme de l'état: 7.54
```

## Concepts Fondamentaux

### État Latent

SCLM maintient un vecteur d'état latent persistant qui:
- Commence à zéro (norme = 0)
- Évolue avec chaque entrée (la norme augmente)
- Capture le contexte sémantique
- Persiste entre les tours de génération

### Évolution de l'État

```python
model.reset_state()
print(f"Initial: {model.state_norm:.2f}")  # 0.00

model.add_context("Le chevalier portait une armure bleue.")
print(f"Après 1: {model.state_norm:.2f}")  # 4.56

model.add_context("Son épée était ancienne et magique.")
print(f"Après 2: {model.state_norm:.2f}")  # 6.23

model.add_context("Le château se dressait sur la colline.")
print(f"Après 3: {model.state_norm:.2f}")  # 7.54
```

### Mode Édition

Faire des modifications locales sans affecter la mémoire globale:

```python
# Établir le contexte
model.add_context("L'épée était BLEUE.")
etat_avant = model.state_norm

# Geler l'état pour édition
model.freeze_state()
output = model.generate("L'épée était ROUGE")  # Génère mais ne met pas à jour l'état
etat_apres = model.state_norm

print(f"État changé: {abs(etat_apres - etat_avant) > 0.001}")  # False

# Reprendre le fonctionnement normal
model.unfreeze_state()
```

## Configuration

### Configuration Personnalisée

```python
from sclm import SCLMConfig, SCLMModel

config = SCLMConfig(
    latent_state_dim=256,      # Taille du vecteur d'état
    n_experts=2,                # Experts MoE
    state_injection_layers=[8, 16],  # Points d'injection
    alpha_inject=0.02,          # Force d'injection
)

model = SCLMModel.from_pretrained("nom-du-modele", config=config)
```

### Utiliser les Préréglages

```python
from sclm.config import get_preset

# Préréglages disponibles: mistral-7b, llama-7b, llama-13b, phi-2, tiny
config = get_preset("mistral-7b")
```

## Sauvegarde et Chargement

### Sauvegarder un Point de Contrôle

```python
model.save_checkpoint("./mon_modele_sclm")
```

### Charger un Point de Contrôle

```python
model = SCLMModel.from_sclm_checkpoint(
    "./mon_modele_sclm",
    load_in_4bit=True
)
```

## Prochaines Étapes

- [Référence API](api.md)
- [Exemples](exemples.md)
- [Architecture](architecture.md)
- [FAQ](faq.md)
