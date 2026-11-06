from sklearn.linear_model import LogisticRegression

from parent_model import ParentModel


class LogisticRegressionModel(ParentModel):
    estimator = LogisticRegression
    DEFAULTS = {
        "C": 1.0,
        "penalty": "l2",
        "solver": "lbfgs",
        "max_iter": 1000,
        "fit_intercept": True,
        "class_weight": "balanced",
        "random_state": 42,
    }
