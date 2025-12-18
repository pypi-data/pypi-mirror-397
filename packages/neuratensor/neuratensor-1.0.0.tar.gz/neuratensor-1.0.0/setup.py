"""
NeuraTensor SDK - Production Setup
===================================

Installs the NeuraTensor SDK with proprietary CUDA kernels.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
if readme_file.exists():
    long_description = readme_file.read_text(encoding="utf-8")
else:
    long_description = "NeuraTensor SDK - Neuromorphic Inference at 8ms"

# Read version
version = "1.0.0"

setup(
    name="neuratensor",
    version=version,
    author="Neuramorphic, Inc.",
    author_email="info@neuramorphic.ai",
    description="Production neuromorphic inference SDK with CUDA acceleration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://neuramorphic.ai",
    project_urls={
        "Documentation": "https://docs.neuramorphic.ai",
        "Source": "https://github.com/neuramorphic/neuratensor-sdk",
        "Bug Reports": "https://github.com/neuramorphic/neuratensor-sdk/issues",
    },
    
    # Package discovery - SDK as neuratensor package
    packages=["neuratensor"],
    package_dir={"neuratensor": "sdk"},
    
    # Include binary library (from parent dir)
    package_data={
        "neuratensor": [
            "../lib/*.so",
            "../lib/*.sha256",
        ],
    },
    include_package_data=True,
    
    # Dependencies
    install_requires=[
        "torch>=2.0.0",
        "numpy>=1.19.0",
    ],
    
    # Optional dependencies
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ],
        "cli": [
            "click>=8.0.0",
        ],
    },
    
    # CLI entry points
    entry_points={
        "console_scripts": [
            "neuratensor=neuratensor.cli:main",
        ],
    },
    
    # Classifiers
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
        "Operating System :: POSIX :: Linux",
        "Environment :: GPU :: NVIDIA CUDA",
    ],
    
    # Requirements
    python_requires=">=3.8",
    
    # Platform
    platforms=["Linux"],
    
    # License
    license="Proprietary",
    
    # Keywords
    keywords="neuromorphic, snn, ssm, cuda, inference, deep-learning, ai",
    
    # Zip safe
    zip_safe=False,
)
