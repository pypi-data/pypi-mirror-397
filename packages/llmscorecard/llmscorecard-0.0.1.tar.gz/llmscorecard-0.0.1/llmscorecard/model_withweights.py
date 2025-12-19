import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder  # One hot encoding for model binary creation of my array when passing it in
from typing import Callable, Sequence, Dict, Any

PredictionFn = Callable[[Sequence[Dict[str, Any]]], Sequence[Any]]
MetricFn = Callable[[Sequence[Any], Sequence[Any]], float]


class Model_Evaluator:
    """Runs predictions over rows and computes metrics."""

    def __init__(self, predict: PredictionFn, metrics: Dict[str, MetricFn]) -> None:
        self.predict = predict
        self.metrics = metrics
