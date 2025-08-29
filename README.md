# Distributed ML Training Platform

A modular platform for distributed machine learning model training, hyperparameter tuning, and job management using Python, scikit-learn, and Redis.

## Features

- Distributed job queue with Redis
- Modular model training (Logistic Regression, Random Forest, etc.)
- Hyperparameter tuning with GridSearchCV
- Support for multiple datasets (Iris, Wine, Breast Cancer, Digits)
- Performance metrics: accuracy, precision, recall, F1 score
- Extensible for new models and datasets

## Usage

1. **Install dependencies:**
	```
	pip install -r requirements.txt
	```

2. **Start Redis server** (if not running):
	```
	redis-server
	```

3. **Run the main script:**
	```
	python main.py
	```

## Project Structure

- `main.py` — Entry point, job submission, and worker management
- `job_queue.py` — Redis job queue logic
- `worker.py` — Worker class for processing jobs
- `training_models/` — Model classes (Logistic Regression, Random Forest, etc.)
- `examples/` — Example scripts for jobs and Redis usage

## Extending

- Add new models in `training_models/`
- Add new datasets in `training_models/models.py`
- Customize hyperparameter grids in `main.py`