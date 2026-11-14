import inspect

from serializer import deserialize_task, serialize_result


async def execute_task(task_data):
    """
    Deserialize and execute a received task.
    Return the result in serialized form.
    """

    try:
        func, args, kwargs = deserialize_task(task_data)

        result = func(*args, **kwargs)

        # Support asynchronous functions too
        if inspect.isawaitable(result):
            result = await result

        response = {
            "status": "success",
            "result": result
        }

    except Exception as error:
        response = {
            "status": "error",
            "error": str(error)
        }

    return serialize_result(response)