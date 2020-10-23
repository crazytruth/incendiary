import asyncio
import pytest

from incendiary.xray.factories import (
    tracing_task_factory,
    wrap_tracing_task_factory,
    current_task_method,
)

import aiotask_context


async def run1():
    loop = asyncio.get_event_loop()

    ct = current_task_method(loop)

    assert hasattr(ct, "context")
    ct.context["entities"] = ["a"]

    # await asyncio.ensure_future(run2())
    # await loop.create_task(run2())
    await asyncio.gather(run2(), run2())

    ct = current_task_method(loop)
    assert hasattr(ct, "context")
    assert "entities" in ct.context
    assert ct.context["entities"] == ["a"]


async def run2():
    loop = asyncio.get_event_loop()

    ct = current_task_method(loop)
    assert hasattr(ct, "context")
    ct.context["entities"].append("b")

    assert ct.context["entities"] == ["a", "b"]

    return 2


class TestTaskFactory:
    @pytest.fixture()
    async def set_default_task_factory(self):
        loop = asyncio.get_event_loop()
        loop.set_task_factory(tracing_task_factory)

    @pytest.fixture()
    async def wrap_task_factory(self):
        loop = asyncio.get_event_loop()
        loop.set_task_factory(
            wrap_tracing_task_factory(aiotask_context.chainmap_task_factory)
        )

    async def test_default_task_factory(self, set_default_task_factory):
        loop = asyncio.get_event_loop()

        current_task = current_task_method(loop=loop)
        current_task.context = {}

        await run1()

    async def test_wrapped_task_factory(self, wrap_task_factory):
        loop = asyncio.get_event_loop()
        current_task = current_task_method(loop=loop)
        current_task.context = {}

        await run1()
