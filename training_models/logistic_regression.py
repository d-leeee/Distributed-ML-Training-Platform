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
from training_models.parent_model import ParentModel as Model

class LogisticRegressionModel(Model):
    def __init__(self, params=None):
        default_params = {
            'C': 1.0,
            'penalty': 'l2',
            'solver': 'lbfgs',
            'max_iter': 100,
            'fit_intercept': True,
            'class_weight': 'balanced',
            'random_state': 42,
        }
        # if params provided, change settings
        if params:
            default_params.update(params)
        self.params = default_params
        self.model = LogisticRegression(**self.params)