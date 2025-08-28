from training_models.logistic_regression import LogisticRegressionModel
from training_models.random_forest import RandomForestModel

from sklearn.datasets import load_iris, load_wine, load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Add this import when you're ready for tuning:
from sklearn.model_selection import GridSearchCV

class Model:
    def __init__(self):
        self.model = {
            'Logistic Regression': LogisticRegressionModel(),
            'Random Forest': RandomForestModel()
        }

    def train(self, model_type, params):
        if model_type in self.model:
            self.model[model_type].train(params)
        else:
            raise ValueError("Unknown model type")