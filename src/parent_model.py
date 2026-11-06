from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.preprocessing import MinMaxScaler


class ParentModel:
    """Shared setup for every algorithm.

    DEFAULTS holds each algorithm's default hyperparameters. If a job passes parameters, any value
    given as a list becomes a GridSearchCV grid (5-fold cross-validation); single values are fixed.
    """

    estimator = None
    DEFAULTS = {}

    def __init__(self, params=None):
        params = {k: v for k, v in (params or {}).items() if k in self.DEFAULTS}
        fixed = {**self.DEFAULTS, **{k: v for k, v in params.items() if not isinstance(v, list)}}
        grid = {k: v for k, v in params.items() if isinstance(v, list)}
        base = self.estimator(**fixed)
        self.model = GridSearchCV(base, grid, cv=5, n_jobs=1) if grid else base

    def split_test(self, x, y):
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25, random_state=42)
        scaler = MinMaxScaler()
        return scaler.fit_transform(x_train), scaler.transform(x_test), y_train, y_test

    def evaluate(self, x_test, y_test, model):
        predictions = model.predict(x_test)
        return {
            "accuracy": accuracy_score(y_test, predictions),
            "precision": precision_score(y_test, predictions, average="weighted"),
            "recall": recall_score(y_test, predictions, average="weighted"),
            "f1": f1_score(y_test, predictions, average="weighted"),
        }
