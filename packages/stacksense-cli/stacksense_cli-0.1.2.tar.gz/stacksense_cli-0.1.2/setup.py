#!/usr/bin/env python3
"""
StackSense Setup
================
AI-powered code intelligence for developers.

Install with:
    pip install .
    
Or in development mode:
    pip install -e .
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read version from cli.py
version = "0.1.0"

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = ""
if readme_path.exists():
    long_description = readme_path.read_text(encoding="utf-8")

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    requirements = [
        line.strip() 
        for line in requirements_path.read_text().splitlines() 
        if line.strip() and not line.startswith('#')
    ]

setup(
    name="stacksense",
    version=version,
    author="PilgrimStack",
    author_email="dev@stacksense.dev",
    description="AI-powered code intelligence for developers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://portfolio-pied-five-61.vercel.app/",
    
    # Use src layout - the standard for reliable wheel building
    package_dir={"": "src"},
    packages=[
        "stacksense",
        "stacksense.core",
        "stacksense.cli",
        "stacksense.api",
        "stacksense.models",
        "stacksense.agents",
        "stacksense.parsers",
        "stacksense.persistence",
        "stacksense.credits",
        "stacksense.providers",
        "stacksense.license",
        "stacksense.backend",
    ],
    
    # Include package data
    include_package_data=True,
    package_data={
        "stacksense": ["*.json", "*.yaml", "*.yml"],
    },
    
    # Dependencies
    install_requires=requirements,
    
    # Python version
    python_requires=">=3.8",
    
    # CLI entry point - now in cli folder
    entry_points={
        "console_scripts": [
            "stacksense=stacksense.cli.cli:main",
        ],
    },
    
    # Classifiers
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Documentation",
    ],
    
    # Keywords
    keywords=[
        "ai",
        "code-analysis",
        "developer-tools",
        "cli",
        "code-intelligence",
        "llm",
        "ollama",
    ],
)
