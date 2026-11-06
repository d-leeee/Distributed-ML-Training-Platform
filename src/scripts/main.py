"""Run one worker. Start several (docker compose --scale worker=N) to train in parallel."""
import warnings

from sklearn.exceptions import ConvergenceWarning

from handlers import HANDLERS
from job_queue import JobQueue
from worker import Worker

warnings.filterwarnings("ignore", category=ConvergenceWarning)

if __name__ == "__main__":
    Worker(JobQueue(), HANDLERS).run()
