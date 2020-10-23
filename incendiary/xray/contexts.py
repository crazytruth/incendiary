from aws_xray_sdk.core.async_context import AsyncContext as _AsyncContext

from incendiary.xray.factories import (
    tracing_task_factory,
    wrap_tracing_task_factory,
)


class IncendiaryAsyncContext(_AsyncContext):
    def __init__(self, *args, loop=None, use_task_factory=True, **kwargs):

        super().__init__(*args, loop=loop, use_task_factory=False, **kwargs)

        if use_task_factory:
            current_task_factory = self._loop.get_task_factory()
            if current_task_factory:
                self._loop.set_task_factory(
                    wrap_tracing_task_factory(current_task_factory)
                )
            else:
                self._loop.set_task_factory(tracing_task_factory)
