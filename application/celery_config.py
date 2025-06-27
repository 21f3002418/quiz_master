from celery import Celery
import time

# Configure Celery with Redis as the broker
app = Celery('tasks', broker='redis://localhost:6379/0')

# Configure result backend
app.conf.result_backend = 'redis://localhost:6379/0'

# Additional Celery configuration
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    broker_connection_retry_on_startup=True,
    broker_connection_max_retries=5,
    broker_connection_retry_delay=2,
)

# Test Redis connection with retries
for attempt in range(3):
    try:
        app.control.ping()
        print("Celery connected to Redis broker successfully")
        break
    except Exception as e:
        print(f"Failed to connect Celery to Redis broker (attempt {attempt + 1}/3): {e}")
        if attempt < 2:
            time.sleep(2)
        else:
            print("Celery could not connect to Redis after 3 attempts. Tasks may not run.")