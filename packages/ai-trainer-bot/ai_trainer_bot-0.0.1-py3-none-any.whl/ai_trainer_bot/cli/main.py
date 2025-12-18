"""
Command-line interface for AI Trainer Bot.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import yaml

from ..core.trainer import Trainer
from ..core.config import Config
from ..tracking.experiment_tracker import ExperimentManager
from ..serving.inference import InferenceEngine
from ..tuning.grid_search import GridSearch
from ..tuning.random_search import RandomSearch
from ..tuning.bayesian_search import BayesianOptimization


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to config file

    Returns:
        Configuration dictionary
    """
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def create_parser() -> argparse.ArgumentParser:
    """
    Create argument parser.

    Returns:
        Argument parser
    """
    parser = argparse.ArgumentParser(
        description='AI Trainer Bot - Machine Learning Training Framework',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Train a model
  python -m ai_trainer_bot.cli train --config config/train.yml

  # Evaluate a model
  python -m ai_trainer_bot.cli evaluate --config config/eval.yml --checkpoint model.pth

  # Run inference
  python -m ai_trainer_bot.cli predict --model model.pth --input data.npy

  # Tune hyperparameters
  python -m ai_trainer_bot.cli tune --config config/tune.yml --method grid

  # Export model
  python -m ai_trainer_bot.cli export --checkpoint model.pth --format onnx --output model.onnx
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Train command
    train_parser = subparsers.add_parser('train', help='Train a model')
    train_parser.add_argument('--config', required=True, help='Path to training config file')
    train_parser.add_argument('--experiment-name', help='Experiment name')
    train_parser.add_argument('--resume', action='store_true', help='Resume training from checkpoint')

    # Evaluate command
    eval_parser = subparsers.add_parser('evaluate', help='Evaluate a trained model')
    eval_parser.add_argument('--config', required=True, help='Path to evaluation config file')
    eval_parser.add_argument('--checkpoint', required=True, help='Path to model checkpoint')
    eval_parser.add_argument('--experiment-name', help='Experiment name for logging')

    # Predict command
    predict_parser = subparsers.add_parser('predict', help='Run inference on data')
    predict_parser.add_argument('--model', required=True, help='Path to model file')
    predict_parser.add_argument('--input', required=True, help='Path to input data')
    predict_parser.add_argument('--output', help='Path to output file')
    predict_parser.add_argument('--batch-size', type=int, default=32, help='Batch size for inference')

    # Tune command
    tune_parser = subparsers.add_parser('tune', help='Tune hyperparameters')
    tune_parser.add_argument('--config', required=True, help='Path to tuning config file')
    tune_parser.add_argument('--method', choices=['grid', 'random', 'bayesian'],
                           default='grid', help='Tuning method')
    tune_parser.add_argument('--max-trials', type=int, default=10, help='Maximum number of trials')

    # Export command
    export_parser = subparsers.add_parser('export', help='Export model to different formats')
    export_parser.add_argument('--checkpoint', required=True, help='Path to model checkpoint')
    export_parser.add_argument('--format', choices=['torchscript', 'onnx'], default='torchscript',
                             help='Export format')
    export_parser.add_argument('--output', required=True, help='Output file path')
    export_parser.add_argument('--input-sample', help='Path to input sample for tracing')

    # List experiments command
    list_parser = subparsers.add_parser('list', help='List experiments')
    list_parser.add_argument('--status', choices=['running', 'completed', 'failed'],
                           help='Filter by status')

    # Show experiment command
    show_parser = subparsers.add_parser('show', help='Show experiment details')
    show_parser.add_argument('experiment_name', help='Experiment name')

    return parser


def train_model(args):
    """
    Train a model.

    Args:
        args: Parsed arguments
    """
    print(f"Loading config from {args.config}")
    config = load_config(args.config)

    # Initialize experiment tracking
    exp_manager = ExperimentManager()
    experiment = exp_manager.create_experiment(args.experiment_name, config)

    try:
        # Initialize trainer
        trainer = Trainer(config)

        if args.resume:
            # Load checkpoint and resume training
            checkpoint_path = config.get('training', {}).get('resume_from')
            if checkpoint_path:
                trainer.load_checkpoint(checkpoint_path)
                print(f"Resumed training from {checkpoint_path}")
            else:
                print("Warning: --resume specified but no resume_from in config")

        # Train the model
        print("Starting training...")
        trainer.train()

        # Save final model
        final_model_path = experiment.experiment_dir / 'final_model.pth'
        trainer.save_checkpoint(str(final_model_path))
        experiment.log_artifact(str(final_model_path), 'final_model.pth', 'model')

        experiment.set_status('completed')
        print(f"Training completed. Model saved to {final_model_path}")

    except Exception as e:
        experiment.set_status('failed')
        experiment.add_note(f"Training failed: {str(e)}")
        print(f"Training failed: {e}")
        raise


def evaluate_model(args):
    """
    Evaluate a model.

    Args:
        args: Parsed arguments
    """
    print(f"Loading config from {args.config}")
    config = load_config(args.config)

    # Initialize experiment tracking if name provided
    experiment = None
    if args.experiment_name:
        exp_manager = ExperimentManager()
        experiment = exp_manager.create_experiment(args.experiment_name, config)

    try:
        # Initialize trainer for evaluation
        trainer = Trainer(config)
        trainer.load_checkpoint(args.checkpoint)

        print("Starting evaluation...")
        metrics = trainer.evaluate()

        print("Evaluation results:")
        for key, value in metrics.items():
            print(f"  {key}: {value}")

        if experiment:
            experiment.log_metrics(metrics)
            experiment.set_status('completed')

    except Exception as e:
        if experiment:
            experiment.set_status('failed')
            experiment.add_note(f"Evaluation failed: {str(e)}")
        print(f"Evaluation failed: {e}")
        raise


def run_inference(args):
    """
    Run inference on data.

    Args:
        args: Parsed arguments
    """
    print(f"Loading model from {args.model}")

    try:
        # Initialize inference engine
        engine = InferenceEngine(args.model)

        # Load input data
        import numpy as np
        input_data = np.load(args.input)

        print("Running inference...")
        predictions = engine.predict(input_data, batch_size=args.batch_size)

        if args.output:
            np.save(args.output, predictions)
            print(f"Predictions saved to {args.output}")
        else:
            print("Predictions:", predictions)

    except Exception as e:
        print(f"Inference failed: {e}")
        raise


def tune_hyperparameters(args):
    """
    Tune hyperparameters.

    Args:
        args: Parsed arguments
    """
    print(f"Loading config from {args.config}")
    config = load_config(args.config)

    try:
        # Select tuner based on method
        tuning_config = config.get('tuning', {})
        param_grid = tuning_config.get('param_grid', {})
        
        if args.method == 'grid':
            tuner = GridSearch(param_grid)
        elif args.method == 'random':
            n_iter = tuning_config.get('n_iter', args.max_trials)
            tuner = RandomSearch(param_grid, n_iter=n_iter)
        elif args.method == 'bayesian':
            n_iter = tuning_config.get('n_iter', args.max_trials)
            tuner = BayesianOptimization(param_grid, n_iter=n_iter)

        print(f"Starting hyperparameter tuning with {args.method} search...")
        best_params, best_score = tuner.tune(max_trials=args.max_trials)

        print("Best parameters found:")
        for key, value in best_params.items():
            print(f"  {key}: {value}")
        print(f"Best score: {best_score}")

    except Exception as e:
        print(f"Hyperparameter tuning failed: {e}")
        raise


def export_model(args):
    """
    Export model to different formats.

    Args:
        args: Parsed arguments
    """
    print(f"Loading model from {args.checkpoint}")

    try:
        if args.format == 'torchscript':
            from ..serving.torchscript_export import TorchScriptExporter
            exporter = TorchScriptExporter()

            if args.input_sample:
                import torch
                input_sample = torch.load(args.input_sample)
            else:
                input_sample = None

            exporter.export(args.checkpoint, args.output, input_sample)

        elif args.format == 'onnx':
            from ..serving.onnx_export import ONNXExporter
            exporter = ONNXExporter()

            if args.input_sample:
                import numpy as np
                input_sample = np.load(args.input_sample)
            else:
                input_sample = None

            exporter.export(args.checkpoint, args.output, input_sample)

        print(f"Model exported to {args.output} in {args.format} format")

    except Exception as e:
        print(f"Model export failed: {e}")
        raise


def list_experiments(args):
    """
    List experiments.

    Args:
        args: Parsed arguments
    """
    exp_manager = ExperimentManager()
    experiments = exp_manager.list_experiments(args.status)

    if not experiments:
        print("No experiments found.")
        return

    print("Experiments:")
    for exp in experiments:
        print(f"  {exp['experiment_name']} - Status: {exp['status']} - Created: {exp['created_at']}")


def show_experiment(args):
    """
    Show experiment details.

    Args:
        args: Parsed arguments
    """
    exp_manager = ExperimentManager()
    experiment = exp_manager.get_experiment(args.experiment_name)

    if not experiment:
        print(f"Experiment '{args.experiment_name}' not found.")
        return

    summary = experiment.get_summary()
    print(f"Experiment: {summary['experiment_name']}")
    print(f"Status: {summary['status']}")
    print(f"Created: {summary['created_at']}")

    if 'finished_at' in summary:
        print(f"Finished: {summary['finished_at']}")

    if summary.get('config'):
        print("Configuration:")
        for key, value in summary['config'].items():
            print(f"  {key}: {value}")

    if summary.get('metrics'):
        print("Final Metrics:")
        for key, values in summary['metrics'].items():
            if values:
                final_value = values[-1]['value']
                print(f"  {key}: {final_value}")


def main():
    """
    Main CLI entry point.
    """
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Execute command
    commands = {
        'train': train_model,
        'evaluate': evaluate_model,
        'predict': run_inference,
        'tune': tune_hyperparameters,
        'export': export_model,
        'list': list_experiments,
        'show': show_experiment
    }

    try:
        commands[args.command](args)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()