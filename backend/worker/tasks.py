from celery.result import AsyncResult
from backend.worker.utils import make_exchange, make_celery, make_queue

celery = make_celery()
direct_exchange = make_exchange('direct_exchange', 'direct', False, True)
celery.conf.task_queues = *make_queue('queue', direct_exchange, 'key', durable=False, auto_delete=True, count=1),

task_routes = {
    'tasks.direct_task': {
        'exchange': 'direct_exchange',
        'exchange_type': 'direct',
        'routing_key': 'key1', 
        }
    }

celery.conf.task_routes = task_routes


@celery.task(name='tasks.direct_task')
def generate_task(content: str): 
    return content


def get_task_info(task_id):
    """
    return task info for the given task_id
    """
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result
    }
    return result


# # Worker для queue1
# celery -A worker.tasks worker --loglevel=info -Q queue1

# # Worker для queue2
# celery -A worker.tasks worker --loglevel=info -Q queue2

# # Worker для queue3
# celery -A worker.tasks worker --loglevel=info -Q queue3