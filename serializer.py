import cloudpickle

def serialize_task(func, args, kwargs):
    task_data = {
        "function": func,
        "args": args,
        "kwargs": kwargs
    }
    return cloudpickle.dumps(task_data)


def deserialize_task(data):
    task_data = cloudpickle.loads(data)

    return (
        task_data["function"],
        task_data["args"],
        task_data["kwargs"]
    )


def serialize_result(result):
    return cloudpickle.dumps(result)


def deserialize_result(data):
    return cloudpickle.loads(data)