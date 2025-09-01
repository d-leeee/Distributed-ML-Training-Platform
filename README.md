# 🚀 Distributed ML Training Platform



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

### 🐳 Distributed/Docker Deployment
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