import asyncio
import pytest

from aws_xray_sdk.core import xray_recorder

from incendiary.xray import Incendiary
from incendiary.xray.contexts import IncendiaryAsyncContext


class TestCaptureAsync:
    @Incendiary.capture_async()
    async def async_function(self):
        self.counter += 1

    @Incendiary.capture_async("main")
    async def async_main(self):
        await self.async_function()

    @Incendiary.capture_async("main_gather")
    async def async_main_gather(self, func):
        cr = [func() for _ in range(10)]
        await asyncio.gather(*cr)

    @Incendiary.capture_async("super_gather")
    async def async_super_gather(self):
        await asyncio.gather(
            *[self.async_main_gather(self.async_function) for _ in range(10)]
        )

    @pytest.fixture()
    def factory_xray_context(self, loop):
        # context = AsyncIOContext()
        # context.set_task_factory(task_factory)
        context = IncendiaryAsyncContext(context_missing="LOG_ERROR", loop=loop)

        return context

    @pytest.fixture()
    def configured_xray_recorder(self, factory_xray_context):
        self.counter = 0
        xray_recorder.configure(
            service="test",
            sampling=False,
            context=factory_xray_context,
            # emitter=StubbedEmitter()
            daemon_address="localhost:2000",
        )
        return xray_recorder

    async def test_capture_async(self, configured_xray_recorder, loop):

        segment = configured_xray_recorder.begin_segment("test_capture_async")
        configured_xray_recorder.context.put_segment(segment)

        await self.async_main()

        assert len(segment.subsegments) == 1
        assert segment.subsegments[0].name == "main"
        configured_xray_recorder.end_segment()

    async def test_capture_async_gather(self, configured_xray_recorder, loop):

        segment = configured_xray_recorder.begin_segment(
            "test_capture_async_gather"
        )
        configured_xray_recorder.context.put_segment(segment)

        await asyncio.gather(*[self.async_function() for _ in range(10)])

        assert len(segment.subsegments) == 10
        for ss in segment.subsegments:
            assert ss.parent_segment is segment

        configured_xray_recorder.end_segment()

    async def test_capture_async_gather_nested(
        self, configured_xray_recorder, loop
    ):

        segment = configured_xray_recorder.begin_segment(
            "test_capture_async_gather_nested"
        )
        configured_xray_recorder.context.put_segment(segment)

        await asyncio.gather(
            *[self.async_main_gather(self.async_function) for _ in range(10)]
        )

        assert len(segment.subsegments) == 10

        assert self.counter == 100

        for ss in segment.subsegments:
            assert ss.name == "main_gather"
            assert ss.parent_segment is segment
            # assert len(ss.subsegments) == 10

            # for sss in ss.subsegments:
            #     assert sss.parent_segment is ss
        configured_xray_recorder.end_segment()

    async def test_capture_async_gather_triple_nested(
        self, configured_xray_recorder, loop
    ):

        segment = configured_xray_recorder.begin_segment(
            "test_capture_async_gather_triple_nested"
        )

        await asyncio.gather(*[self.async_super_gather() for _ in range(10)])

        assert len(segment.subsegments) == 10

        assert self.counter == 1000

        for ss in segment.subsegments:
            assert ss.name == "super_gather"
            assert ss.parent_segment is segment
            # assert len(ss.subsegments) == 10

            # for sss in ss.subsegments:
            #     assert sss.parent_segment is ss

        configured_xray_recorder.end_segment()

    async def test_capture_async_without_incendiary_initialize(self, caplog):
        from incendiary.loggers import error_logger
        from incendiary.xray.mixins import CAPTURE_WARNING

        error_logger.setLevel("DEBUG")

        @Incendiary.capture_async()
        async def capture_this():
            return "a"

        await capture_this()

        assert caplog.messages[1] == CAPTURE_WARNING.format(name="capture_this")

    def test_capture_without_incendiary_initialize(self, caplog):
        from incendiary.loggers import error_logger

        error_logger.setLevel("DEBUG")

        @Incendiary.capture()
        def capture_sync():
            return "capture_sync"

        capture_sync()
