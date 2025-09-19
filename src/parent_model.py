from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import os
import redis

# parent extends all algorithms
class ParentModel:
    def split_test(self, x, y, params):
        # split test
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25, random_state=42)

        # ml preprocessing
        scaler = MinMaxScaler()
        x_train = scaler.fit_transform(x_train)
        x_test = scaler.transform(x_test)

        return x_train, x_test, y_train, y_test
    
    def evaluate(self, x_test, y_test, model, job_id):
        # provides metrics
        predictions = model.predict(x_test)

        accuracy = accuracy_score(y_test, predictions)
        precision = precision_score(y_test, predictions, average='weighted')
        recall = recall_score(y_test, predictions, average='weighted')
        f1 = f1_score(y_test, predictions, average='weighted')

        redis_host = os.getenv('REDIS_HOST', 'localhost')
        self.r = redis.Redis(host=redis_host, port=6379, db=0)

        updates = {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1
        }
        self.r.hset(f"job:{job_id}", mapping=updates)
        # Also return metrics so callers can log/propagate results
        return updates