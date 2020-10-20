import aiohttp
import pytest
import logging
import traceback

from insanic.app import Insanic
from insanic.conf import settings

from insanic.exceptions import BadRequest
from insanic.loading import get_service
from insanic.views import InsanicView
from sanic.response import json

from incendiary.xray.app import Incendiary

logger = logging.getLogger(__name__)


def _mock_check_prerequisites(*args, **kwargs):
    return []


class TestTracing:
    @pytest.fixture()
    async def client_session(self):
        session = aiohttp.ClientSession()
        yield session
        await session.close()

    @pytest.fixture()
    def sanic_test_server(
        self, loop, test_server, sanic_test_server_2, monkeypatch
    ):
        sr = {
            "version": 1,
            "rules": [],
            "default": {"fixed_target": 1, "rate": 0},
        }
        monkeypatch.setattr(
            settings._wrapped, "SAMPLING_RULES", sr, raising=False
        )
        monkeypatch.setattr(
            settings._wrapped, "TRACING_ENABLED", True, raising=False
        )
        monkeypatch.setattr(
            Incendiary, "_check_prerequisites", _mock_check_prerequisites
        )
        incendiary_service = get_service("incendiary")

        monkeypatch.setattr(incendiary_service, "host", "127.0.0.1")
        monkeypatch.setattr(
            incendiary_service, "port", sanic_test_server_2.port
        )

        incendiary_exception_service = get_service("incendiary_exception")
        monkeypatch.setattr(incendiary_exception_service, "host", "127.0.0.2")
        monkeypatch.setattr(
            incendiary_exception_service, "port", sanic_test_server_2.port
        )

        from ..incendiary1.app import app

        return loop.run_until_complete(test_server(app, host="0.0.0.0"))

    @pytest.fixture()
    def sanic_test_server_2(self, loop, test_server, monkeypatch):
        sr = {
            "version": 1,
            "rules": [],
            "default": {"fixed_target": 0, "rate": 0},
        }
        monkeypatch.setattr(
            settings._wrapped, "SAMPLING_RULES", sr, raising=False
        )
        monkeypatch.setattr(
            settings._wrapped, "TRACING_ENABLED", False, raising=False
        )
        monkeypatch.setattr(
            settings._wrapped, "ALLOWED_HOSTS", [], raising=False
        )
        monkeypatch.setattr(
            settings._wrapped, "GRPC_SERVE", False, raising=False
        )
        monkeypatch.setattr(
            Incendiary, "_check_prerequisites", _mock_check_prerequisites
        )

        insanic_application = Insanic("incendiary")
        Incendiary.init_app(insanic_application)

        class MockView(InsanicView):
            authentication_classes = []
            permission_classes = []

            async def get(self, request, *args, **kwargs):
                segment = request.app.xray_recorder.current_segment()
                try:
                    assert segment.sampled is bool(
                        int(request.query_params.get("expected_sample"))
                    )
                    assert segment.in_progress is True
                except AssertionError:
                    traceback.print_exc()
                    raise

                return json({"i am": "service_2"}, status=201)

        class ErrorView(InsanicView):
            authentication_classes = []
            permission_classes = []

            async def get(self, request, *args, **kwargs):
                raise BadRequest("errors")

        insanic_application.add_route(MockView.as_view(), "/trace_2")
        insanic_application.add_route(ErrorView.as_view(), "/trace_error_2")

        return loop.run_until_complete(
            test_server(insanic_application, host="0.0.0.0")
        )

    async def test_tracing_enabled_false(
        self, sanic_test_server, monkeypatch, client_session
    ):
        monkeypatch.setattr(
            settings._wrapped, "TRACING_ENABLED", False, raising=False
        )
        monkeypatch.setattr(settings, "SERVICE_LIST", {}, raising=False)

        flag = 0
        for _ in range(10):
            url = f"http://127.0.0.1:{sanic_test_server.port}/trace?expected_sample={flag}"
            async with client_session.request("GET", url) as resp:
                await resp.read()
                # resp.raise_for_status()

                assert resp.status == 202, resp._body

    async def test_trace_middleware(
        self, sanic_test_server, monkeypatch, client_session
    ):
        """
        tests if subsequent requests are not sampled. A time sensitive test so may
        not work if debugging takes too long

        :param sanic_test_server:
        :param monkeypatch:
        :param client_session:
        :return:
        """
        monkeypatch.setattr(settings, "SERVICE_LIST", {}, raising=False)

        flag = 1
        for _ in range(10):
            url = f"http://127.0.0.1:{sanic_test_server.port}/trace?expected_sample={flag}"
            async with client_session.request("GET", url) as resp:
                await resp.read()

                assert resp.status == 202, resp._body

                if flag == 1:
                    flag = 0

    async def test_trace_middleware_interservice(
        self, sanic_test_server, monkeypatch, client_session
    ):
        monkeypatch.setattr(settings, "SERVICE_LIST", {}, raising=False)

        flag = 1
        for _ in range(10):
            url = f"http://127.0.0.1:{sanic_test_server.port}/trace_1?expected_sample={flag}"
            async with client_session.request("GET", url) as resp:
                await resp.read()
                # resp.raise_for_status()

                assert resp.status == 202, resp._body

                if flag == 1:
                    flag = 0

    async def test_trace_middleware_exception(
        self, sanic_test_server, monkeypatch, client_session
    ):

        monkeypatch.setattr(settings, "SERVICE_LIST", {}, raising=False)

        url = f"http://127.0.0.1:{sanic_test_server.port}/trace_exception"
        async with client_session.request("GET", url) as resp:
            await resp.read()

            assert resp.status == 204, resp._body

    async def test_trace_middleware_interservice_exception(
        self, sanic_test_server, monkeypatch, client_session
    ):

        monkeypatch.setattr(settings, "SERVICE_LIST", {}, raising=False)

        url = f"http://127.0.0.1:{sanic_test_server.port}/trace_error_1"
        async with client_session.request("GET", url) as resp:
            await resp.read()
            assert resp.status == 204, resp._body


# class TestInterserviceTracing(TestTracing):
#
#     def test_non_incendiary_to_incendiary(self, sanic_test_server, ):
