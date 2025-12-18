from setuptools import setup, find_packages

setup(
    name="hanerma",
    version="1.0.1", # Updated version
    description="Hierarchical Atomic Nested External Reasoning and Memory Architecture",
    packages=find_packages(),
    install_requires=[
        "requests",
        "numpy",
        "sentence-transformers>=2.2.0",
        "torch"
    ],
    python_requires=">=3.8",
)