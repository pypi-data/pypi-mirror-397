"""
NEXUS-AIDOS-BRAIN setup configuration.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="nexus-aidos-brain",
    version="0.1.0",
    author="Nexus AI Hub Team",
    author_email="support@nexusaihub.com",
    description="Core Conversational AI Engine for the Nexus Ecosystem",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nexusaihub/NEXUS-AIDOS-BRAIN",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        # LangChain ecosystem
        "langchain>=0.1.20,<0.2.0",
        "langchain-core>=0.1.52,<0.2.0",
        "langchain-community>=0.0.38,<0.1.0",
        "langchain-openai>=0.1.7,<0.2.0",
        
        # LangGraph for agent orchestration
        "langgraph>=0.0.55,<0.1.0",
        
        # Vector store and embeddings
        "qdrant-client>=1.7.0,<2.0.0",
        "sentence-transformers>=3.0.0,<4.0.0",
        
        # Redis for caching and memory
        "redis[hiredis]>=5.0.0,<6.0.0",
        
        # ML and utilities
        "numpy>=1.26.0,<2.0.0",
        "scikit-learn>=1.5.0,<2.0.0",
        "tiktoken>=0.5.0,<1.0.0",
        
        # HTTP and auth
        "requests>=2.31.0,<3.0.0",
        "certifi>=2024.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=6.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "nexus-aidos=nexus_aidos.cli:main",
        ],
    },
)
