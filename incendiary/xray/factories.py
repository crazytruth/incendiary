import asyncio
import copy
import sys

XRAY_CONTEXT_STORAGE = "entities"

if sys.hexversion >= 0x03070000:
    current_task_method = asyncio.current_task
else:
    current_task_method = asyncio.Task.current_task


def wrap_tracing_task_factory(task_factory):
    # @wraps(task_factory)
    def wrapped(loop, coro):
        task = task_factory(loop, coro)
        current_task = current_task_method(loop=loop)

        if current_task is not None and hasattr(current_task, "context"):
            context = copy.copy(current_task.context)
            if XRAY_CONTEXT_STORAGE in context:
                context[XRAY_CONTEXT_STORAGE] = context[
                    XRAY_CONTEXT_STORAGE
                ].copy()
            task.context = context
        return task

    return wrapped


@wrap_tracing_task_factory
def tracing_task_factory(loop, coro):
    """
    Task factory function

    Function closely mirrors the logic inside of
    asyncio.BaseEventLoop.create_task. Then if there is a current
    task and the current task has a context then share that context
    with the new task
    """
    task = asyncio.tasks.Task(coro, loop=loop)
    if task._source_traceback:  # flake8: noqa
        del task._source_traceback[-1]  # flake8: noqa

    return task
