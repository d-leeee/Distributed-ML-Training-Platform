import redis

def redis_example():
    r = redis.Redis(host='localhost', port=6379, db=0)
    
    print("testing connection")
    try:
        r.ping()
        print("Redis connection successful")
    except redis.ConnectionError:
        print("Redis connection failed")
        return

    r.hset('myhash', mapping = {
        'type': 'model',
        'status': 'active',
        'version': '1.0'
    })

    data = r.hgetall('myhash')
    print('job details:', {k.decode(): v.decode() for k, v in data.items()})

if __name__ == "__main__":
    redis_example()