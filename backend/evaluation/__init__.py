# evaluation/__init__.py
from .test_dataset import get_dataset, get_dataset_by_category
from .evaluator import FDAEvaluator
from .run_evaluation import run_evaluation

__all__ = [
    'get_dataset',
    'get_dataset_by_category',
    'FDAEvaluator',
    'run_evaluation'
]