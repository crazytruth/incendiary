from typing import Optional

from aws_xray_sdk import global_sdk_config
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core.async_recorder import AsyncSubsegmentContextManager
from aws_xray_sdk.core.models.dummy_entities import DummySegment
from aws_xray_sdk.core.models.subsegment import (
    SubsegmentContextManager,
    subsegment_decorator,
    is_already_recording,
)
from aws_xray_sdk.core.exceptions.exceptions import SegmentNotFoundException
from aws_xray_sdk.core.exceptions import exceptions

from incendiary.loggers import error_logger

CAPTURE_WARNING = (
    "[INCENDIARY] Incendiary has NOT been initialized for capture. "
    "Refer to README for more information: {name}"
)


class IncendiaryAsyncSubsegmentContextManager(AsyncSubsegmentContextManager):
    """
    A context manager that starts and ends a segment.
    """

    def __init__(self, instance, *args, **kwargs):

        self.instance = instance
        super(IncendiaryAsyncSubsegmentContextManager, self).__init__(
            *args, **kwargs
        )

    @subsegment_decorator
    async def __call__(self, wrapped, instance, args, kwargs):

        if is_already_recording(wrapped):
            # The wrapped function is already decorated, the subsegment will be created later,
            # just return the result
            return await wrapped(*args, **kwargs)

        func_name = self.name
        if not func_name:
            func_name = wrapped.__name__

        if not global_sdk_config.sdk_enabled() or self.instance.app is None:
            try:
                segment = self.recorder.current_segment()
            except SegmentNotFoundException:
                segment = DummySegment(func_name)
                self.recorder.context.put_segment(segment)
            finally:
                if segment is None:
                    error_logger.warning(CAPTURE_WARNING.format(name=func_name))
                elif (
                    hasattr(self.instance.app, "initialized_plugins")
                    and "incendiary"
                    not in self.instance.app.initialized_plugins
                ):
                    error_logger.warning(CAPTURE_WARNING.format(name=func_name))

        try:
            return await self.recorder.record_subsegment_async(
                wrapped,
                instance,
                args,
                kwargs,
                name=func_name,
                namespace="local",
                meta_processor=None,
            )
        except exceptions.AlreadyEndedException:
            return await wrapped(*args, **kwargs)


class CaptureMixin:
    @classmethod
    def capture_async(
        cls, name: Optional[str] = None
    ) -> IncendiaryAsyncSubsegmentContextManager:
        """
        A decorator that records enclosed function or method
        in a subsegment. It only works with asynchronous function

        :param name: The name of the subsegment. If not specified, the function name will be used.
        """
        return IncendiaryAsyncSubsegmentContextManager(
            cls, xray_recorder, name=name
        )

    @classmethod
    def capture(cls, name: Optional[str] = None) -> SubsegmentContextManager:
        """
        A decorator that records decorated callable in a subsegment.

        :param name: The name of the subsegment. If not specified the function name will be used.
        """
        return SubsegmentContextManager(xray_recorder, name=name)

    #
