from setuptools import setup, find_packages
from pathlib import Path

readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else "NeuraTensor SDK"

setup(
    name="neuratensor",
    version="1.1.3",
    author="Neuramorphic, Inc.",
    author_email="info@neuramorphic.ai",
    description="Production neuromorphic inference SDK with CUDA acceleration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://neuramorphic.ai",
    
    packages=["neuratensor", "core", "config", "utils"],
    package_dir={"neuratensor": "sdk"},
    
    package_data={
        "core": ["*.pyc", "*.so"],
        "config": ["*.pyc"],
        "sdk": ["*.py"],
        "utils": ["*.py"],
        "": ["lib/*.so"],
    },
    
    include_package_data=True,
    
    install_requires=[
        "torch>=2.0.0",
        "numpy>=1.19.0",
    ],
    
    python_requires=">=3.8",
    zip_safe=False,
    
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3.8",
        "Operating System :: POSIX :: Linux",
    ],
)
