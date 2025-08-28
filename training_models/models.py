from training_models.logistic_regression import LogisticRegressionModel
from training_models.random_forest import RandomForestModel

from sklearn.datasets import load_iris, load_wine, load_breast_cancer
import time

# Add this import when you're ready for tuning:
from sklearn.model_selection import GridSearchCV

class Model:
    def __init__(self):
        # expand when ready
        self.alg = {
            'Logistic Regression': LogisticRegressionModel(),
            'Random Forest': RandomForestModel()
        }
        # expand when ready
        self.data_set = {
            'Iris': load_iris(),
            'Wine': load_wine(),
            'Breast Cancer': load_breast_cancer()
        }
    
    def train(self, model_type, data_set, params):
        # calls on the correct algorithm
        if model_type in self.alg and data_set in self.data_set:
            algorithm = self.alg[model_type]
            x = self.data_set[data_set].data
            y = self.data_set[data_set].target
            
            # do split testing
            x_train, x_test, y_train, y_test = algorithm.split_test(x, y, params)

            # add hyperparameter tuning here when ready
            # self.alg[model_type].hyperparameters()

            # fit the model
            start = time.time()
            model = algorithm.create_model().fit(x_train, y_train)
            end = time.time()
            print(f"Training time: {end - start} seconds")

            # evaluate model
            algorithm.evaluate(x_test, y_test, model)
        else:
            raise ValueError("Unknown model type or data set")