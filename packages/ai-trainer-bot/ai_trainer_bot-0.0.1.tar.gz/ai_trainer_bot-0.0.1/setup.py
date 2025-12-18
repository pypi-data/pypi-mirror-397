"""
Setup script for AI Trainer Bot.
"""

from setuptools import setup, find_packages
import os

# Determine project root
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

# Read README
readme_path = os.path.join(PROJECT_ROOT, "README.md")
try:
    with open(readme_path, "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = ""

# Read requirements
def read_requirements(filename):
    path = os.path.join(PROJECT_ROOT, filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        return []

requirements = read_requirements("requirements.txt")

setup(
    name="ai-trainer-bot",
    version="0.0.1",
    author="Girish Kor",
    author_email="girishkor05@gmail.com",
    description="A comprehensive machine learning training framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/girish-kor/ai-trainer-bot",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    # Use SPDX license expression instead of deprecated license classifiers
    license="MIT",
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "black>=21.0.0",
            "flake8>=4.0.0",
            "mypy>=0.910",
            "pre-commit>=2.15.0",
            "pytest>=6.2.0",
            "pytest-cov>=2.12.0",
        ],
        "docs": [
            "sphinx>=4.2.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
        "gpu": [
            "torch>=1.9.0",
            "torchvision>=0.10.0",
            "torchaudio>=0.9.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ai-trainer-bot=ai_trainer_bot.cli.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "ai_trainer_bot": ["config/*.yml"],
    },
    keywords="machine learning, deep learning, pytorch, training, framework",
    project_urls={
        "Bug Reports": "https://github.com/girish-kor/ai-trainer-bot/issues",
        "Source": "https://github.com/girish-kor/ai-trainer-bot",
        "Documentation": "https://ai-trainer-bot.readthedocs.io/",
    },
)