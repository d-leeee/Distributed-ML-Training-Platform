from training_models.logistic_regression import LogisticRegressionModel
from training_models.random_forest import RandomForestModel

from sklearn.datasets import load_iris, load_wine, load_breast_cancer, load_digits
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
import time

# Add this import when you're ready for tuning:
from sklearn.model_selection import GridSearchCV

class Model:
    def __init__(self, params):
        # expand when ready
        self.alg = {
            'Logistic Regression': LogisticRegressionModel(params),
            'Random Forest': RandomForestModel(params)
        }
        # expand when ready
        self.data_set = {
            'Iris': load_iris(),
            'Wine': load_wine(),
            'Breast Cancer': load_breast_cancer(),
            'Digits': load_digits()
        }
    
    def train(self, job):
        # calls on the correct algorithm
        if job['type'] in self.alg and job['description'] in self.data_set:
            algorithm = self.alg[job['type']]
            x = self.data_set[job['description']].data
            y = self.data_set[job['description']].target

            # do split testing
            x_train, x_test, y_train, y_test = algorithm.split_test(x, y, job['parameters'])

            # fit and evaluate (no tuning)
            print("Fitting model...", flush=True)
            model = algorithm.model.fit(x_train, y_train)

            # evaluate model
            algorithm.evaluate(x_test, y_test, model, job['id'])
        else:
            raise ValueError("Unknown model type or data set")