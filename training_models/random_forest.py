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

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from training_models.parent_model import ParentModel as Model

class RandomForestModel(Model):
    def __init__(self, params=None):
        self.params = {
            'n_estimators': 100,
            'max_depth': None,
            'min_samples_split': 2,
            'min_samples_leaf': 1,
            'random_state': 42,
        }
        if params:
            updated = False
            for k, v in params.items():
                if k in self.params:
                    self.params[k] = v
                    updated = True
            if updated:
                self.model = GridSearchCV(RandomForestClassifier(), self.params, cv=5)
        else:
            self.model = RandomForestClassifier(**self.params)