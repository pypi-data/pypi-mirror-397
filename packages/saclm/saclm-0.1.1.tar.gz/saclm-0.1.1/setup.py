#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SCLM - Stateful Coherent Language Model
=======================================

Proprietary Software - Dual License Model
Copyright (c) 2025 Mike Amega (Ame Web Studio)

See LICENSE for details.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read version
version = "0.1.1"

setup(
    name="saclm",
    version=version,
    author="Mike Amega",
    author_email="info@amewebstudio.com",
    description="SCLM: Stateful Coherent Language Model - Persistent memory for transformers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Volgat/sclm",
    project_urls={
        "Bug Tracker": "https://github.com/Volgat/sclm/issues",
        "Documentation": "https://sclm.readthedocs.io",
        "Commercial Licensing": "mailto:info@amewebstudio.com",
    },
    packages=find_packages(exclude=["tests", "tests.*", "examples", "notebooks"]),
    package_data={
        "sclm": ["py.typed"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.8",
    install_requires=[
        "torch>=2.0.0",
        "transformers>=4.35.0",
        "accelerate>=0.20.0",
        "safetensors>=0.3.0",
        "huggingface-hub>=0.16.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "quantization": [
            "bitsandbytes>=0.41.0",
        ],
        "full": [
            "bitsandbytes>=0.41.0",
            "sentencepiece>=0.1.99",
            "protobuf>=3.20.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "sclm=sclm.cli:main",
        ],
    },
    keywords=[
        "nlp", "transformers", "language-model", "memory", 
        "stateful", "coherence", "earcp", "deep-learning", 
        "pytorch", "huggingface"
    ],
    zip_safe=False,
)
