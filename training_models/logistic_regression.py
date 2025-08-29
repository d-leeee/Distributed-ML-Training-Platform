# start with one training model
# find the accuracy and time
# use hyperparameter tuning
# compare metrics with baseline and tuned models
# multiple metrics not just accuracy
# future engineering

# add all models

# optional: automaticaly choose between training models for each job task based on metrics
# optional: PyTorch Neural Networks deep learning
# optional: cross validation
# optional: create mutliple training models

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV
from training_models.parent_model import ParentModel as Model

class LogisticRegressionModel(Model):
    def __init__(self, params):
        # gridsearch can automatically set these params
        self.params = {
            'C': 1.0,
            'penalty': 'l2',
            'solver': 'lbfgs',
            'max_iter': 100,
            'fit_intercept': True,
            'class_weight': 'balanced',
            'random_state': 42,
        }
        # Only update keys that exist in self.params
        if params:
            updated = False
            for k, v in params.items():
                if k in self.params:
                    self.params[k] = v
                    updated = True
            if updated:
                self.model = GridSearchCV(LogisticRegression(), self.params, cv=5)
        else:
            self.model = LogisticRegression(**self.params)
