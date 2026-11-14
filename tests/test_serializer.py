from serializer import serialize_task, deserialize_task
from serializer import serialize_result, deserialize_result


def multiply(a, b):
    return a * b


def test_task_serialization():
    data = serialize_task(multiply, (10, 20), {})
    func, args, kwargs = deserialize_task(data)

    result = func(*args, **kwargs)

    assert result == 200


def test_result_serialization():
    data = serialize_result(200)
    result = deserialize_result(data)

    assert result == 200