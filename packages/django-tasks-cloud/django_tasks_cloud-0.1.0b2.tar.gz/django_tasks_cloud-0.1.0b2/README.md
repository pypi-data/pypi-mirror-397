# Django Task Backend for AWS and Azure

[![Build and Push to PyPI (and Test PyPI for testing)](https://github.com/papercloudtech/django-tasks-cloud/actions/workflows/cd.yml/badge.svg)](https://github.com/papercloudtech/django-tasks-cloud/actions/workflows/cd.yml)

> ❌ **IMPORTANT**
> This project is in its early stages. While it is functional, it may not cover all edge cases or have comprehensive documentation. Use it at your own risk and feel free to contribute! We are working fast to make it production-ready.

This project aims to use Django's new `Task` back-end to expose AWS and Azure native services to manage long-running tasks asynchronously. This project is useful for tasks that must run outside the request-response cycle, like sending emails, processing images, or running machine learning models. It leverages the power of AWS and Azure native services. You can choose between the two cloud providers (more on this in the installation and setup sections). With the reliance on cloud native services, the project provides a scalable and reliable solution for managing long-running tasks.

## Installation

Installation depends on which cloud provider you want to use. You can install the package using PIP for all cloud providers as follows:

```bash
pip install django-cloud-task
```

For AWS:

```bash
pip install django-cloud-task[aws]
```

For Azure:

```bash
pip install django-cloud-task[azure]
```

Once installed, add it to your Django `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    ...
    "django_cloud_task",
    # Either or Both
    "django_cloud_task_aws",  # For AWS
    "django_cloud_task_azure",  # For Azure
    ...
]
```

## Configuration

### AWS: SQS

To configure AWS SQS as your task backend, add the following settings to your `settings.py`:

### AWS: SNS

### AWS: EventBridge

### Azure: Service Bus Queue

```python
TASKS = {
    "default": {
        "BACKEND": "django_cloud_tasks_azure.backends.service_bus.ServiceBusQueueBackend",
        "QUEUES": ["default"],
        "OPTIONS": {
            "SERVICEBUS_DEFAULT_QUEUE_NAME": "testing",
            "SERVICEBUS_USE_CONNECTION_STRING": True,
            "SERVICEBUS_CONNECTION_STRING": "",
            "SERVICEBUS_NAMESPACE_FQDN": "",
            "SERVICEBUS_CREDENTIAL_LOADER": "this.that.custom_credential_loader_function",
        },
    },
}
```

For a simple setup, you can use the `SERVICEBUS_USE_CONNECTION_STRING` option set to `True` and provide the `SERVICEBUS_CONNECTION_STRING`. This connection string can be obtained from the Azure portal.

If you don't wanna hardcode credentials, you must provide the `SERVICEBUS_NAMESPACE_FQDN` and provide `SERVICEBUS_CREDENTIAL_LOADER`. If you don't provide a custom credential loader, the default will use `DefaultAzureCredential` from the `azure-identity` package.

To use a custom credential class from a suite of Azure credential classes, set the `SERVICEBUS_CREDENTIAL_LOADER` option to a method of the following function signature:

```python
def custom_credential_loader() -> TokenCredential: ...
```

Mention it's full module path in the `SERVICEBUS_CREDENTIAL_LOADER` setting. The function must return an instance of a class that inherits from `azure.core.credentials.TokenCredential`. A function wrapper is required because some `TokenCredential` classes require parameters for initialization. To know more about the available credential classes, refer to the [Azure Identity](https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity?view=azure-python) documentation.

> [!IMPORTANT]
> `QUEUES` is a list of queue names that you want to use. Each queue name in the list corresponds to a queue that you have created in your Azure Service Bus namespace.

### Azure: Service Bus Topic

```python
TASKS = {
    "default": {
        "BACKEND": "django_cloud_tasks_azure.backends.service_bus.ServiceBusTopicBackend",
        "QUEUES": ["default"],
        "OPTIONS": {
            "SERVICEBUS_DEFAULT_TOPIC_NAME": "testing",
            "SERVICEBUS_USE_CONNECTION_STRING": True,
            "SERVICEBUS_CONNECTION_STRING": "",
            "SERVICEBUS_NAMESPACE_FQDN": "",
            "SERVICEBUS_CREDENTIAL_LOADER": "this.that.custom_credential_loader_function",
        },
    },
}
```

The configuration is similar to the Service Bus Queue backend. The main difference is that you need to provide the `SERVICEBUS_DEFAULT_TOPIC_NAME` instead of the queue name.

### Azure: Storage Account Queue

```python
TASKS = {
    "default": {
        "BACKEND": "django_cloud_tasks_azure.backends.storage_queue.StorageAccountQueueBackend",
        "QUEUES": ["default"],
        "OPTIONS": {
            "STORAGE_ACCOUNT_QUEUE_DEFAULT_QUEUE_NAME": "testing",
            "STORAGE_ACCOUNT_USE_CONNECTION_STRING": True,
            "STORAGE_ACCOUNT_CONNECTION_STRING": "",
            "STORAGE_ACCOUNT_NAME": "",
            "STORAGE_ACCOUNT_CREDENTIAL_LOADER": "this.that.custom_credential_loader_function",
        },
    },
}
```

The configuration is similar to the Service Bus Queue backend. The main difference is that you need to provide the `STORAGE_ACCOUNT_QUEUE_DEFAULT_QUEUE_NAME` instead of the queue name.

## Contributing

Contributions are welcome! Please read the [CONTRIBUTING.md](./CONTRIBUTING.md) file for more information on how to contribute to this project.
