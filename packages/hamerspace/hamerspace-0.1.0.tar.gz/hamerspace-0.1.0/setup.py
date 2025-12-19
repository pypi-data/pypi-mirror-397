"""
hamerspace: Model Compression and Optimization Engine
A compiler-style optimization pass for non-LLM ML models
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="hamerspace",
    version="0.1.0",
    author="Hamerspace Contributors",
    author_email="",
    description="Model compression and optimization engine for non-LLM machine learning models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/hamerspace",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "torch>=2.0.0",
        "tensorflow>=2.13.0",
        "onnx>=1.14.0",
        "onnxruntime>=1.15.0",
        "transformers>=4.30.0",
        "optimum>=1.12.0",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "pydantic>=2.0.0",
        "tqdm>=4.65.0",
        "psutil>=5.9.0",
    ],
    extras_require={
        "full": [
            "openvino>=2023.0.0",
            "bitsandbytes>=0.41.0",
            "apache-tvm>=0.12.0",
        ],
        "dev": [
            "pytest>=7.3.0",
            "pytest-cov>=4.1.0",
            "black>=23.3.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "hamerspace=hamerspace.cli:main",
        ],
    },
)
