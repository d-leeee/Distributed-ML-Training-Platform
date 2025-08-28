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
    def hyperparameters(self):
        # implement later
        pass
    
    def create_model(self):
        return LogisticRegression()