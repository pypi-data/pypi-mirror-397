# AI Trainer Bot

[![PyPI version](https://badge.fury.io/py/ai-trainer-bot.svg)](https://pypi.org/project/ai-trainer-bot/)
[![Python versions](https://img.shields.io/pypi/pyversions/ai-trainer-bot.svg)](https://pypi.org/project/ai-trainer-bot/)
[![License](https://img.shields.io/pypi/l/ai-trainer-bot.svg)](https://github.com/girish-kor/ai-trainer-bot/blob/main/LICENSE)
[![Build Status](https://img.shields.io/github/actions/workflow/status/girish-kor/ai-trainer-bot/ci.yml)](https://github.com/girish-kor/ai-trainer-bot/actions)

**AI Trainer Bot** is a production-oriented Python framework designed to **train, evaluate, tune, version, and export machine learning models in a fully automated and reproducible manner**. It enforces a strict, code-first training lifecycle suitable for CI/CD pipelines, research-to-production workflows, and long-running training jobs.

## Features

- **Standardized Training Loop:** Reproducible and framework-consistent training.
- **Modular Architecture:** Separate concerns for data, models, training logic, evaluation, and export.
- **Configuration-Driven:** Run experiments via YAML/CLI without modifying code.
- **Experiment Tracking:** Automatic logging of metrics, checkpoints, and artifacts.
- **Hyperparameter Tuning:** Support for grid, random, and Bayesian search.
- **Deployment Ready:** Export models to ONNX, TorchScript, or other frameworks.
- **Fail-Fast Execution:** Immediate termination on invalid configs or mismatched shapes.
- **Extensible Design:** Add new datasets, models, or losses without modifying core code.

## Requirements

- Python 3.8+
- PyTorch 1.9+
- Additional dependencies listed in `requirements.txt`

## Installation

Install AI Trainer Bot from PyPI:

```bash
pip install ai-trainer-bot
```

For development installation:

```bash
git clone https://github.com/girish-kor/ai-trainer-bot.git
cd ai-trainer-bot
pip install -e .
```

## Quick Start

### Training a Model

```bash
# Train a model with configuration
ai-trainer-bot train --config config/train.yml
```

### Evaluating a Model

```bash
# Evaluate a trained model
ai-trainer-bot evaluate --model path/to/model.pt --config config/eval.yml
```

### Exporting a Model

```bash
# Export model for deployment
ai-trainer-bot export --model path/to/model.pt --format onnx
```

## Usage

### Configuration Files

Create YAML configuration files for training and evaluation. Example `train.yml`:

```yaml
model:
  name: "resnet50"
  num_classes: 10

data:
  train_path: "data/train"
  val_path: "data/val"
  batch_size: 32

training:
  epochs: 100
  optimizer: "adam"
  lr: 0.001

output:
  checkpoint_dir: "checkpoints"
  log_dir: "logs"
```

### Python API

```python
from ai_trainer_bot import Trainer, Config

# Load configuration
config = Config.from_yaml("config/train.yml")

# Initialize trainer
trainer = Trainer(config)

# Train model
trainer.train()

# Evaluate model
metrics = trainer.evaluate()
print(f"Accuracy: {metrics['accuracy']:.4f}")
```

## System Scope

- **Data Handling:** Load datasets from local or remote sources, apply preprocessing and augmentation.
- **Model Instantiation:** Manage models via registry pattern.
- **Training Execution:** Pluggable optimizers, schedulers, and callbacks.
- **Evaluation:** Standardized metrics for classification, regression, and custom tasks.
- **Artifact Management:** Save checkpoints, logs, and exported models.
- **Hyperparameter Search:** Grid, random, and Bayesian search support.

## Non-Negotiable Principles

- No notebooks in core logic.
- No hardcoded paths, models, or hyperparameters.
- No silent failures or implicit defaults.
- No training without evaluation.
- No evaluation without artifact persistence.

## Target Users

- ML engineers building repeatable training pipelines.
- Backend engineers integrating ML into production systems.
- Research teams transitioning from experimentation to deployment.

---

## API Documentation

For detailed API documentation, see the [docs/api.md](docs/api.md) file or visit our [online documentation](https://girish-kor.github.io/ai-trainer-bot/).

## Directory Structure

```bash
├── core/                          # Training loop, orchestrator, state
│   ├── __init__.py
│   ├── trainer.py                 # Main training orchestrator
│   ├── state.py                   # Training state management
│   └── config.py                  # Configuration handling
├── data/                          # Dataset loader, preprocessing, augmentation
│   ├── __init__.py
│   ├── loader.py                  # Dataset loading utilities
│   ├── preprocessor.py            # Data preprocessing pipeline
│   ├── augmentor.py               # Data augmentation functions
│   └── transforms.py              # Data transformation utilities
├── models/                        # Model definitions, registry
│   ├── __init__.py
│   ├── registry.py                # Model registry
│   ├── base.py                    # Base model class
│   └── architectures/             # Model architecture implementations
│       ├── __init__.py
│       ├── cnn.py
│       ├── transformer.py
│       └── rnn.py
├── training/                      # Loss, optimizer, scheduler, callbacks
│   ├── __init__.py
│   ├── losses.py                  # Loss functions
│   ├── optimizers.py              # Optimizer configurations
│   ├── schedulers.py              # Learning rate schedulers
│   └── callbacks.py               # Training callbacks
├── metrics/                       # Standard metrics
│   ├── __init__.py
│   ├── classification.py          # Classification metrics
│   ├── regression.py              # Regression metrics
│   └── custom.py                  # Custom metric implementations
├── tuning/                        # Hyperparameter search
│   ├── __init__.py
│   ├── grid_search.py             # Grid search implementation
│   ├── random_search.py           # Random search implementation
│   └── bayesian_search.py         # Bayesian optimization
├── serving/                       # Export and inference logic
│   ├── __init__.py
│   ├── exporter.py                # Model export utilities
│   ├── onnx_export.py             # ONNX export
│   ├── torchscript_export.py      # TorchScript export
│   └── inference.py               # Inference utilities
├── tracking/                      # Logging and artifact management
│   ├── __init__.py
│   ├── logger.py                  # Logging utilities
│   ├── artifact_store.py          # Artifact storage
│   └── experiment_tracker.py      # Experiment tracking
├── cli/                           # CLI entry points
│   ├── __init__.py
│   ├── main.py                    # Main CLI entry point
│   ├── train.py                   # Train command
│   ├── evaluate.py                # Evaluate command
│   └── export.py                  # Export command
├── utils/                         # Helper functions
│   ├── __init__.py
│   ├── io.py                      # I/O utilities
│   ├── validation.py              # Input validation
│   └── helpers.py                 # General helper functions
├── config/                        # Configuration files
│   ├── train.yml                  # Training configuration
│   ├── eval.yml                   # Evaluation configuration
│   └── model_configs/             # Model-specific configurations
├── tests/                         # Unit and integration tests
│   ├── __init__.py
│   ├── test_trainer.py
│   ├── test_data.py
│   ├── test_models.py
│   └── integration_tests/
├── docs/                          # Documentation
│   ├── api.md
│   ├── examples.md
│   └── contributing.md
├── requirements.txt               # Python dependencies
├── setup.py                       # Package setup
└── README.md                      # This file
```

## Contributing

We welcome contributions! This framework is designed to be **extensible and modular**. Contributions should adhere to the separation-of-concerns principle, deterministic execution, and fail-fast behavior.

### Development Setup

1. Fork the repository
2. Clone your fork: `git clone https://github.com/girish-kor/ai-trainer-bot.git`
3. Create a virtual environment: `python -m venv venv`
4. Activate the environment: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Unix)
5. Install development dependencies: `pip install -e ".[dev]"`
6. Run tests: `pytest`

### Guidelines

- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting PR

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Links

- [PyPI Package](https://pypi.org/project/ai-trainer-bot/)
- [Documentation](https://girish-kor.github.io/ai-trainer-bot/)
- [Issue Tracker](https://github.com/girish-kor/ai-trainer-bot/issues)
- [Source Code](https://github.com/girish-kor/ai-trainer-bot)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and updates.