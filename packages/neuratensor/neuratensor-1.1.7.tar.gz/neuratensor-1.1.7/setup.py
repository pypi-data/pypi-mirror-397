from setuptools import setup, find_packages
from pathlib import Path

readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else "NeuraTensor SDK"

setup(
    name="neuratensor",
    version="1.1.7",
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
    
    # Paquetes reales en disco (sdk/ ya fue renombrado a neuratensor/)
    packages=["neuratensor", "neuratensor.tests", "core", "config", "utils"],
    
    package_data={
        "core": ["*.py", "*.pyc"],
        "config": ["*.py", "*.pyc"],
        "neuratensor": ["*.py"],
        "utils": ["*.py"],
        "": ["lib/*.so", "kernels/*.cu", "kernels/*.cuh"],
    },
    
    include_package_data=True,
    
    install_requires=[
        "torch>=2.0.0",
        "numpy>=1.19.0",
    ],
    
    extras_require={
        "dev": ["pytest>=7.0.0", "black>=22.0.0"],
        "cli": ["click>=8.0.0"],
    },
    
    entry_points={
        "console_scripts": [
            "neuratensor=neuratensor.cli:main",
        ],
    },
    
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
    
    python_requires=">=3.8",
    platforms=["Linux"],
    license="Proprietary",
    keywords="neuromorphic, snn, ssm, cuda, inference, deep-learning, ai",
    zip_safe=False,
)
