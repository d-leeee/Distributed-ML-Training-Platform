from time import sleep
from redis.redis_client import RedisClient 
import numpy as np

def metrics():
    accumulative_training_time = 0
    total_training_time = 0
    sleep(3)
    while True:
        if RedisClient.r.hget("jobs_completed", "count") == RedisClient.r.hget("jobs_submitted", "count"):
            jobs = RedisClient.r.scan_iter("job:*")
            for k in jobs:
                v = RedisClient.r.hgetall(k)
                for field, value in v.items():
                    if field.decode('utf-8') != 'parameters':
                        RedisClient.r.rpush("logs", f"  {field.decode('utf-8')}: {value.decode('utf-8')}")
                RedisClient.r.rpush("logs", "---------------------------------------------------")
                training_time = float(v.get(b"training_time", 0))
                accumulative_training_time += training_time
                total_training_time = np.maximum(total_training_time, training_time)
            RedisClient.r.rpush("logs", f"Accumulative training time of all workers: {accumulative_training_time} seconds")
            RedisClient.r.rpush("logs", f"Total training time of all workers: {total_training_time} seconds")
            RedisClient.r.rpush("logs", f"Time saved through distribution: {accumulative_training_time - total_training_time} seconds")
            break
        else:
            sleep(2)
def monitor():
    metrics()

if __name__ == "__main__":
    monitor()