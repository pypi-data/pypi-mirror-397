"""
NeuraTensor SDK - Setup Script
===============================

Installation script for distributable NeuraTensor SDK.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="neuratensor-sdk",
    version="1.0.0",
    author="Peter Fulle",
    author_email="peter@neuramorphic.ai",
    description="High-performance neuromorphic tensor processing SDK for NVIDIA GPUs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/neuramorphic/neuratensor",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "torch>=2.0.0",
        "numpy>=1.20.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ],
    },
    package_data={
        "neuratensor_sdk": [
            "lib/*.so",
            "lib/*.dll",
            "lib/*.dylib",
        ],
    },
    entry_points={
        "console_scripts": [
            "neuratensor=neuratensor_sdk.cli:main",
        ],
    },
)
