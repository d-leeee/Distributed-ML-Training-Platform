import json
import uuid
from datetime import datetime

def create_job():
    job = {
        'id': str(uuid.uuid4()),
        'type': '???',
        'parameters': {

        },
        'status': 'pending',
        'created_at': datetime.now().isoformat()

    }

    print(json.dumps(job, indent=2))

if __name__ == "__main__":
    create_job()