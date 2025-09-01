# Distributed ML Training Platform


A modular platform for distributed machine learning model training, hyperparameter tuning, and job management using Python, scikit-learn, Redis, and Docker.

## Features


- Distributed job queue with Redis
- Modular model training (Logistic Regression, Random Forest, etc.)
- Hyperparameter tuning with GridSearchCV
- Support for multiple datasets (Iris, Wine, Breast Cancer, Digits)
- Performance metrics: accuracy, precision, recall, F1 score
- Extensible for new models and datasets
- Docker-based deployment for scalable distributed training


## Usage

### Local Development
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
    python src/submit_jobs.py
	python src/main.py
	```

### Distributed/Docker Deployment
1. **Build and start containers:**
	```
	docker compose up --build --scale worker=3
	```
2. **Submit jobs:**
	- Run `src/submit_jobs.py` locally or as a Docker service to add jobs to the queue.
	- Workers will automatically pick up and process jobs.

## Project Structure


- `src/main.py` — Worker entry point for job processing
- `src/submit_jobs.py` — Script for submitting jobs to Redis
- `src/job_queue.py` — Redis job queue logic
- `src/worker.py` — Worker class for processing jobs
- `src/training_models/` — Model classes (Logistic Regression, Random Forest, etc.)
- `examples/` — Example scripts for jobs and Redis usage

## Extending


- Add new models in `src/training_models/`
- Add new datasets in `src/models.py`
- Customize hyperparameter grids in `src/submit_jobs.py`
- Scale workers with Docker Compose for parallel job processing