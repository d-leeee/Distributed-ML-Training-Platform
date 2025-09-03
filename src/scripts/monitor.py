import os
from time import sleep
import redis
import numpy as np

def metrics():
    redis_host = os.getenv('REDIS_HOST', 'localhost')
    r = redis.Redis(host=redis_host, port=6379, db=0)
    accumulative_training_time = 0
    total_training_time = 0
    sleep(3)
    while True:
        if r.hget("jobs_completed", "count") == r.hget("jobs_submitted", "count"):
            jobs = r.scan_iter("job:*")
            for k in jobs:
                v = r.hgetall(k)
                for field, value in v.items():
                    if field.decode('utf-8') != 'parameters':
                        print(f"  {field.decode('utf-8')}: {value.decode('utf-8')}")
                print("---------------------------------------------------")
                training_time = float(v.get(b"training_time", 0))
                accumulative_training_time += training_time
                total_training_time = np.maximum(total_training_time, training_time)
            print(f"Accumulative training time of all workers: {accumulative_training_time} seconds")
            print(f"Total training time of all workers: {total_training_time} seconds")
            print(f"Time saved through distribution: {accumulative_training_time - total_training_time} seconds")
            break
        else:
            sleep(2)
def monitor():
    metrics()

if __name__ == "__main__":
    monitor()