from setuptools import setup, find_packages

setup(
    name="ml-trainer-sdk",
    version="0.4.1.10",
    description="A modular SDK for training ML models (image, tabular, timeseries, etc.)",
    author="Hypnotic",
    packages=find_packages(include=["ml_trainer", "ml_trainer.*"]),
    install_requires=[
        # Core ML and Data Science
        "torch==2.6.0",
        "torchvision==0.21.0",
        "numpy==1.26.4",
        "pandas==2.2.3",
        "scikit-learn==1.4.2",
        "matplotlib==3.10.1",
        "tensorboard==2.19.0",
        "Cython==3.1.1",
        # LLM finetuning
        "datasets>=3.4.1,<4.2",
        "unsloth",
        "unsloth_zoo",
        "torchao==0.12.0",
        # Other tasks
        "patool==4.0.1",
        "reformer-pytorch==1.4.4",
        "sktime==0.39.0",
        "PyWavelets==1.8.0",
        "timm==1.0.20",
        "axolotl==0.12.2",
    ],
    python_requires=">=3.10",
    include_package_data=True,
)
