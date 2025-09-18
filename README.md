# 🚀 Distributed ML Training Platform
#
## 🧑‍💻 Tech Stack

- **Frontend:** Next.js (React, TypeScript), Material UI (Google UI components library)
- **Backend:** FastAPI (Python)
- **ML:** scikit-learn
- **Queue/Cache:** Redis
- **Orchestration:** Docker, Docker Compose
- **Other:** CORS Middleware, tqdm, etc.




Welcome to the **Distributed ML Training Platform**! 🎉

Train, tune, and scale your machine learning models with ease using Python, scikit-learn, Redis, and Docker. Submit jobs, watch your workers hustle, and get results fast!


## ✨ Features



- 🗂️ Distributed job queue with Redis
- 🤖 Modular model training (Logistic Regression, Random Forest, etc.)
- 🔍 Hyperparameter tuning with GridSearchCV
- 📊 Support for multiple datasets (Iris, Wine, Breast Cancer, Digits)
- 🏆 Performance metrics: accuracy, precision, recall, F1 score
- 🧩 Extensible for new models and datasets
- 🐳 Docker-based deployment for scalable distributed training



---

## 🛠️ Usage



### 🖥️ Local Development
1. **Create and activate a virtual environment (recommended):**
	```bash
	python3 -m venv venv
	source venv/bin/activate
	```
2. **Install dependencies:**
	```bash
	pip install -r requirements.txt
	```
3. **Start Redis server** (if not running):
	```bash
	redis-server
	```
4. **Run the main script:**
	```bash
	python src/submit_jobs.py
	python src/main.py
	```

### 🌐 Frontend (Next.js)

1. **Install frontend dependencies:**
	```bash
	cd frontend
	npm install
	```
2. **Start the frontend development server:**
	```bash
	npm run dev
	# App runs at http://localhost:3000
	```
3. **Frontend features:**
	- Dynamic model/solver/hyperparameter selection
	- Form submission to FastAPI backend
	- Real-time job status and results (if implemented)

### 🔗 API Integration

**Submit jobs from frontend:**
Frontend sends POST requests to FastAPI backend (default: http://localhost:8000/create-job)

Example fetch usage:
```js
await fetch('http://localhost:8000/create-job', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
	 type: model,
	 description: dataset,
	 parameters: enabled ? hyperparams : undefined
  })
});
```

**CORS Note:**
Make sure FastAPI backend has CORS enabled:
```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
	 CORSMiddleware,
	 allow_origins=["http://localhost:3000"],
	 allow_credentials=True,
	 allow_methods=["*"],
	 allow_headers=["*"],
)
```


### 🐳 Distributed/Docker Deployment

---

## 📝 Operational Notes & Useful Commands

**Delete all job keys from Docker Redis instance:**
```sh
docker exec distributed-ml-training-platform-redis-1 redis-cli DEL $(docker exec distributed-ml-training-platform-redis-1 redis-cli KEYS 'job:*')
```

**Delete all keys from Redis database:**
```sh
docker exec distributed-ml-training-platform-redis-1 redis-cli FLUSHDB
```

**Run Redis inside Docker:**
```sh
docker compose up redis
```

**Run Redis inside Docker in Detached Mode:**
```sh
docker compose up -d redis
```

**Run Main (with 3 workers):**
```sh
docker compose up --build --scale worker=3
```

**Example: Clean start for distributed training**
```sh
docker compose up -d redis
docker exec distributed-ml-training-platform-redis-1 redis-cli FLUSHDB
docker compose up --build --scale worker=3
```
1. **Build and start containers:**
	```bash
	docker compose up --build --scale worker=3
	```
2. **Submit jobs:**
	- Run `src/submit_jobs.py` locally or as a Docker service to add jobs to the queue.
	- Workers will automatically pick up and process jobs.

---


## 🗂️ Project Structure



- `src/main.py` — Worker entry point for job processing
- `src/submit_jobs.py` — Script for submitting jobs to Redis
- `src/job_queue.py` — Redis job queue logic
- `src/worker.py` — Worker class for processing jobs
- `src/training_models/` — Model classes (Logistic Regression, Random Forest, etc.)
- `examples/` — Example scripts for jobs and Redis usage


---

## 🧩 Extending & Customizing



- Add new models in `src/training_models/`
- Add new datasets in `src/models.py`
- Customize hyperparameter grids in `src/submit_jobs.py`
- Scale workers with Docker Compose for parallel job processing

---

## 🎈 Tips & Fun Ideas

- Try scaling up the number of workers for super-fast job crunching! 🚦
- Visualize your training progress with `tqdm` progress bars. 📈
- Experiment with new models and datasets—make it your own playground! 🧪
- Use Docker Desktop to watch your containers hustle in real time. 👀

---

## 💬 Questions or Feedback?

Open an issue or start a discussion—let’s make ML more fun together! 😄