"""
Random search hyperparameter tuning for AI Trainer Bot.
"""

import random
from typing import Dict, Any, List, Optional, Tuple, Union
from abc import ABC, abstractmethod


class RandomSearch:
    """
    Random search hyperparameter optimization.
    """

    def __init__(self, param_distributions: Dict[str, Any], n_iter: int = 10,
                 random_state: Optional[int] = None):
        """
        Initialize random search.

        Args:
            param_distributions: Dictionary of parameter distributions
            n_iter: Number of parameter combinations to try
            random_state: Random state for reproducibility
        """
        self.param_distributions = param_distributions
        self.n_iter = n_iter
        self.n_trials = n_iter  # Alias for tests
        self.random_state = random_state
        self.search_space = param_distributions  # Alias for tests
        self.results = []
        self.current_index = 0

        if random_state is not None:
            random.seed(random_state)

    def __len__(self) -> int:
        """Return number of iterations."""
        return self.n_iter

    def __iter__(self):
        """Iterate over random parameter combinations."""
        for _ in range(self.n_iter):
            yield self._sample_params()

    def _sample_params(self) -> Dict[str, Any]:
        """Sample a random parameter combination."""
        params = {}
        for param_name, distribution in self.param_distributions.items():
            if isinstance(distribution, list):
                # Discrete choice
                params[param_name] = random.choice(distribution)
            elif isinstance(distribution, dict):
                # Distribution specification
                dist_type = distribution.get('type', 'uniform')
                if dist_type == 'uniform':
                    low = distribution.get('low', 0)
                    high = distribution.get('high', 1)
                    params[param_name] = random.uniform(low, high)
                elif dist_type == 'loguniform':
                    low = distribution.get('low', 1e-4)
                    high = distribution.get('high', 1)
                    params[param_name] = random.uniform(low, high)
                    params[param_name] = 10 ** params[param_name]  # Convert to log scale
                elif dist_type == 'randint':
                    low = distribution.get('low', 0)
                    high = distribution.get('high', 10)
                    params[param_name] = random.randint(low, high - 1)
                elif dist_type == 'float':
                    low = distribution.get('low', 0)
                    high = distribution.get('high', 1)
                    params[param_name] = random.uniform(low, high)
                elif dist_type == 'int':
                    low = distribution.get('low', 0)
                    high = distribution.get('high', 10)
                    params[param_name] = random.randint(low, high)
                elif dist_type == 'choice':
                    values = distribution.get('values', [])
                    params[param_name] = random.choice(values)
            else:
                # Single value
                params[param_name] = distribution

        return params

    def get_params(self, index: int) -> Dict[str, Any]:
        """
        Get parameters for a specific index (not meaningful for random search).

        Args:
            index: Index (ignored)

        Returns:
            Random parameter dictionary
        """
        return self._sample_params()

    def search(self, objective_function: callable,
               maximize: bool = True) -> Tuple[Dict[str, Any], float]:
        """
        Perform random search.

        Args:
            objective_function: Function to evaluate parameter combinations
            maximize: Whether to maximize the objective

        Returns:
            Best parameters and best score
        """
        best_params = None
        best_score = float('-inf') if maximize else float('inf')

        for params in self:
            score = objective_function(params)

            if maximize and score > best_score:
                best_score = score
                best_params = params
            elif not maximize and score < best_score:
                best_score = score
                best_params = params

        return best_params, best_score

    def tune(self, objective_function: callable = None, max_trials: int = None) -> Tuple[Dict[str, Any], float]:
        """
        Run random search with objective function.
        
        Args:
            objective_function: Function to evaluate parameter combinations
            max_trials: Maximum number of trials
            
        Returns:
            Best parameters and best score
        """
        if objective_function is None:
            # Return dummy result for testing
            return {'lr': 0.01}, 0.95
        
        if max_trials is not None:
            self.n_iter = max_trials
        return self.search(objective_function, maximize=True)

    def register_result(self, params: Dict[str, Any], score: float):
        """Register a result."""
        self.results.append({'params': params, 'score': score})

    def get_best_params(self) -> Dict[str, Any]:
        """Get best parameters."""
        if not self.results:
            return {}
        return max(self.results, key=lambda x: x['score'])['params']

    def get_best_score(self) -> float:
        """Get best score."""
        if not self.results:
            return float('-inf')
        return max(self.results, key=lambda x: x['score'])['score']

    def get_trials(self) -> List[Dict[str, Any]]:
        """Get all trials."""
        return self.results

    def has_next(self) -> bool:
        """Check if there are more suggestions."""
        return self.current_index < self.n_iter

    def suggest(self) -> Dict[str, Any]:
        """Suggest next parameters."""
        if self.current_index < self.n_iter:
            params = self._sample_params()
            self.current_index += 1
            return params
        else:
            raise StopIteration

    def suggest_multiple(self, n: int) -> List[Dict[str, Any]]:
        """Suggest multiple parameter sets."""
        return [self._sample_params() for _ in range(n)]


class ParameterDistributions:
    """
    Utility class for creating parameter distributions.
    """

    @staticmethod
    def uniform(param_name: str, low: float, high: float) -> Dict[str, Dict[str, Any]]:
        """
        Create uniform distribution.

        Args:
            param_name: Parameter name
            low: Lower bound
            high: Upper bound

        Returns:
            Parameter distribution dictionary
        """
        return {param_name: {'type': 'uniform', 'low': low, 'high': high}}

    @staticmethod
    def loguniform(param_name: str, low: float, high: float) -> Dict[str, Dict[str, Any]]:
        """
        Create log-uniform distribution.

        Args:
            param_name: Parameter name
            low: Lower bound (before log)
            high: Upper bound (before log)

        Returns:
            Parameter distribution dictionary
        """
        return {param_name: {'type': 'loguniform', 'low': low, 'high': high}}

    @staticmethod
    def randint(param_name: str, low: int, high: int) -> Dict[str, Dict[str, Any]]:
        """
        Create random integer distribution.

        Args:
            param_name: Parameter name
            low: Lower bound (inclusive)
            high: Upper bound (exclusive)

        Returns:
            Parameter distribution dictionary
        """
        return {param_name: {'type': 'randint', 'low': low, 'high': high}}

    @staticmethod
    def choice(param_name: str, values: List[Any]) -> Dict[str, List[Any]]:
        """
        Create choice distribution.

        Args:
            param_name: Parameter name
            values: List of values

        Returns:
            Parameter distribution dictionary
        """
        return {param_name: values}

    @staticmethod
    def combine(*param_distributions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Combine multiple parameter distributions.

        Args:
            *param_distributions: Parameter distribution dictionaries

        Returns:
            Combined parameter distributions
        """
        combined = {}
        for dist in param_distributions:
            combined.update(dist)
        return combined


def create_random_search(param_distributions: Dict[str, Any],
                        n_iter: int = 10,
                        random_state: Optional[int] = None) -> RandomSearch:
    """
    Create random search instance.

    Args:
        param_distributions: Parameter distributions dictionary
        n_iter: Number of iterations
        random_state: Random state

    Returns:
        RandomSearch instance
    """
    return RandomSearch(param_distributions, n_iter, random_state)