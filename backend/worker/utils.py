from celery import Celery
from kombu import Exchange, Queue


def make_exchange(name: str, exchange_type: str, durable: bool, auto_delete: bool):
    exchange = Exchange(name, type=exchange_type, durable=durable, auto_delete=auto_delete)
    return exchange

def make_queue(name: str, exchange: Exchange, routing_key: str, durable: bool, auto_delete: bool, count: int=1):
    queues = []
    for i in range(count):
        queue = Queue(f'{name}{i+1}', exchange=exchange, routing_key=f'{routing_key}{i+1}', durable=durable, auto_delete=auto_delete)
        queues.append(queue)

    return queues


def make_celery(app_name=__name__):
    backend = "redis://localhost:6380/0"
    broker  = "amqp://admin:admin@localhost:5672/"

    celery = Celery(app_name, backend=backend, broker=broker)
    celery.conf.broker_connection_retry_on_startup = True 
    celery.conf.broker_connection_max_retries = 4
    celery.conf.broker_connection_retry_delay = 2 
    return celery