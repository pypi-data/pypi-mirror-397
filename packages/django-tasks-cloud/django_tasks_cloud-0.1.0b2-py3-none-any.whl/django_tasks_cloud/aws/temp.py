from django.tasks import task


@task(queue_name="email-ingestor", backend="sqs")
def a_task(key: str, value: str):
    pass


@task(queue_name="email-ingestor", backend="sns")
def b_task(key: str, value: str):
    pass


@task(queue_name="email-ingestor", backend="eventbridge_scheduler")
def c_task(key: str, value: str):
    pass
