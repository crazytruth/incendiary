import asyncio
import copy

from functools import wraps


def wrap_tracing_task_factory(task_factory):
    @wraps(task_factory)
    def wrapped(loop, coro):
        task = task_factory(loop, coro)
        current_task = asyncio.Task.current_task(loop=loop)

        if current_task is not None and hasattr(current_task, 'context'):
            context = copy.copy(current_task.context)
            context['entities'] = context['entities'].copy()
            setattr(task, 'context', context)
        return task

    return wrapped


@wrap_tracing_task_factory
def tracing_task_factory(loop, coro):
    """
    Task factory function

    Fuction closely mirrors the logic inside of
    asyncio.BaseEventLoop.create_task. Then if there is a current
    task and the current task has a context then share that context
    with the new task
    """
    task = asyncio.tasks.Task(coro, loop=loop)
    if task._source_traceback:  # flake8: noqa
        del task._source_traceback[-1]  # flake8: noqa

    return task
