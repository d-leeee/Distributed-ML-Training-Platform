from functools import lru_cache

from sklearn.datasets import load_breast_cancer, load_digits, load_iris, load_wine

from training_models.logistic_regression import LogisticRegressionModel
from training_models.random_forest import RandomForestModel

ALGORITHMS = {
    "Logistic Regression": LogisticRegressionModel,
    "Random Forest": RandomForestModel,
}

DATASETS = {
    "Iris": load_iris,
    "Wine": load_wine,
    "Breast Cancer": load_breast_cancer,
    "Digits": load_digits,
}


@lru_cache(maxsize=None)
def load_dataset(name):
    data = DATASETS[name]()
    return data.data, data.target


def train_job(job):
    """Train the requested model on the requested dataset and return its test metrics."""
    if job["type"] not in ALGORITHMS:
        raise ValueError(f"unknown model type {job['type']!r}")
    if job["description"] not in DATASETS:
        raise ValueError(f"unknown dataset {job['description']!r}")

    algorithm = ALGORITHMS[job["type"]](job.get("parameters"))
    x, y = load_dataset(job["description"])
    x_train, x_test, y_train, y_test = algorithm.split_test(x, y)
    model = algorithm.model.fit(x_train, y_train)
    metrics = algorithm.evaluate(x_test, y_test, model)
    if hasattr(model, "best_params_"):
        metrics["best_params"] = model.best_params_
    return metrics
