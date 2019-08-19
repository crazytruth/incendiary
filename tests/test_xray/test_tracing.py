import aiohttp
import pytest
import logging
import traceback

from insanic.app import Insanic
from insanic.conf import settings

from insanic.exceptions import BadRequest, ResponseTimeoutError
from insanic.responses import json_response
from insanic.services import Service
from insanic.views import InsanicView

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
    def sanic_test_server(self, loop, test_server, sanic_test_server_2, monkeypatch):
        sr = {
            "version": 1,
            "rules": [],
            "default": {
                "fixed_target": 1,
                "rate": 0
            }
        }
        monkeypatch.setattr(settings._wrapped, 'SAMPLING_RULES', sr, raising=False)
        monkeypatch.setattr(settings._wrapped, 'TRACING_ENABLED', True, raising=False)
        monkeypatch.setattr(settings._wrapped, "ALLOWED_HOSTS", [], raising=False)
        monkeypatch.setattr(settings._wrapped, "GRPC_SERVE", False, raising=False)
        monkeypatch.setattr(Incendiary, "_check_prerequisites", _mock_check_prerequisites)

        insanic_application = Insanic('incendiary1')
        Incendiary.init_app(insanic_application)

        class MockView(InsanicView):
            authentication_classes = []
            permission_classes = []

            async def get(self, request, *args, **kwargs):
                segment = request.app.xray_recorder.current_segment()
                try:
                    assert segment.sampled is bool(int(request.query_params.get('expected_sample')))
                    assert segment.in_progress is True
                except AssertionError:

                    traceback.print_exc()
                    raise

                return json_response({}, status=202)

        class MockErrorView(InsanicView):
            authentication_classes = []
            permission_classes = []

            async def get(self, request, *args, **kwargs):
                # segment = request.app.xray_recorder.current_segment()
                raise BadRequest("trace error!")

        class MockInterServiceError(InsanicView):
            authentication_classes = []
            permission_classes = []

            async def get(self, request, *args, **kwargs):
                try:
                    service = Service('incendiary')
                    monkeypatch.setattr(service, "host", "127.0.0.1")
                    monkeypatch.setattr(service, "port", sanic_test_server_2.port)

                    resp, status = await service.http_dispatch('GET', f'/trace_error_2',
                                                               include_status_code=True)

                    segment = request.app.xray_recorder.current_segment()
                    subsegment = segment.subsegments[0]

                    try:

                        assert subsegment.trace_id == segment.trace_id
                        assert subsegment.error is True

                        assert subsegment.http['response']['status'] == 400 == status
                    except AssertionError:
                        traceback.print_exc()
                        raise
                except Exception:
                    traceback.print_exc()
                    raise
                return json_response({}, status=204)

        class ExceptionView(InsanicView):
            authentication_classes = []
            permission_classes = []

            async def get(self, request, *args, **kwargs):
                try:
                    service = Service('incendiary')
                    monkeypatch.setattr(service, "host", "127.0.0.2")
                    monkeypatch.setattr(service, "port", sanic_test_server_2.port)

                    try:
                        resp, status = await service.http_dispatch('GET', f'/trace_error_2',
                                                                   include_status_code=True)
                    except ResponseTimeoutError:

                        segment = request.app.xray_recorder.current_segment()
                        subsegment = segment.subsegments[0]

                        try:
                            assert subsegment.trace_id == segment.trace_id
                            assert subsegment.fault is True

                            assert len(subsegment.cause['exceptions']) > 0
                        except AssertionError:
                            traceback.print_exc()
                            raise
                except Exception:
                    traceback.print_exc()
                    raise
                return json_response({}, status=204)



        class MockInterServiceView(InsanicView):
            authentication_classes = []
            permission_classes = []

            async def get(self, request, *args, **kwargs):
                segment = request.app.xray_recorder.current_segment()
                try:
                    expected_sample = bool(int(request.query_params.get('expected_sample')))
                    try:
                        assert segment.sampled is expected_sample
                        assert segment.in_progress is True
                    except AssertionError as e:
                        traceback.print_exc()
                        raise

                    service = Service('incendiary')
                    monkeypatch.setattr(service, "host", "127.0.0.1")
                    monkeypatch.setattr(service, "port", sanic_test_server_2.port)

                    resp, status = await service.http_dispatch('GET', f'/trace_2',
                                                               query_params={"expected_sample": int(expected_sample)},
                                                               include_status_code=True)
                    try:
                        assert status == 201
                        assert resp == {"i am": "service_2"}, resp
                    except AssertionError:
                        traceback.print_exc()
                        raise
                except Exception:
                    traceback.print_exc()
                    raise

                return json_response({}, status=202)

        insanic_application.add_route(MockErrorView.as_view(), '/trace_error')
        insanic_application.add_route(ExceptionView.as_view(), '/trace_exception')
        insanic_application.add_route(MockInterServiceError.as_view(), '/trace_error_1')
        insanic_application.add_route(MockView.as_view(), '/trace')
        insanic_application.add_route(MockInterServiceView.as_view(), '/trace_1')

        return loop.run_until_complete(test_server(insanic_application, host='0.0.0.0'))

    @pytest.fixture()
    def sanic_test_server_2(self, loop, test_server, monkeypatch):
        sr = {
            "version": 1,
            "rules": [],
            "default": {
                "fixed_target": 0,
                "rate": 0
            }
        }
        monkeypatch.setattr(settings._wrapped, 'SAMPLING_RULES', sr, raising=False)
        monkeypatch.setattr(settings._wrapped, 'TRACING_ENABLED', False, raising=False)
        monkeypatch.setattr(settings._wrapped, "ALLOWED_HOSTS", [], raising=False)
        monkeypatch.setattr(settings._wrapped, "GRPC_SERVE", False, raising=False)
        monkeypatch.setattr(Incendiary, "_check_prerequisites", _mock_check_prerequisites)

        insanic_application = Insanic('incendiary')
        Incendiary.init_app(insanic_application)

        class MockView(InsanicView):
            authentication_classes = []
            permission_classes = []

            async def get(self, request, *args, **kwargs):
                segment = request.app.xray_recorder.current_segment()
                try:
                    assert segment.sampled is bool(int(request.query_params.get('expected_sample')))
                    assert segment.in_progress is True
                except AssertionError:
                    traceback.print_exc()
                    raise

                return json_response({"i am": "service_2"}, status=201)

        class ErrorView(InsanicView):
            authentication_classes = []
            permission_classes = []

            async def get(self, request, *args, **kwargs):
                raise BadRequest("errors")

        insanic_application.add_route(MockView.as_view(), '/trace_2')
        insanic_application.add_route(ErrorView.as_view(), '/trace_error_2')

        return loop.run_until_complete(test_server(insanic_application, host='0.0.0.0'))

    async def test_tracing_enabled_false(self, sanic_test_server, monkeypatch, client_session):
        monkeypatch.setattr(settings._wrapped, 'TRACING_ENABLED', False, raising=False)
        monkeypatch.setattr(settings, "SERVICE_LIST", {}, raising=False)

        flag = 0
        for i in range(10):
            url = f"http://127.0.0.1:{sanic_test_server.port}/trace?expected_sample={flag}"
            async with client_session.request('GET', url) as resp:
                await resp.read()
                # resp.raise_for_status()

                assert resp.status == 202, resp._body

    async def test_trace_middleware(self, sanic_test_server, monkeypatch, client_session):
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
        for i in range(10):
            url = f"http://127.0.0.1:{sanic_test_server.port}/trace?expected_sample={flag}"
            async with client_session.request('GET', url) as resp:
                await resp.read()

                assert resp.status == 202, resp._body

                if flag is 1:
                    flag = 0

    async def test_trace_middleware_interservice(self, sanic_test_server, monkeypatch, client_session):
        monkeypatch.setattr(settings, "SERVICE_LIST", {}, raising=False)

        flag = 1
        for i in range(10):
            url = f"http://127.0.0.1:{sanic_test_server.port}/trace_1?expected_sample={flag}"
            async with client_session.request('GET', url) as resp:
                await resp.read()
                # resp.raise_for_status()

                assert resp.status == 202, resp._body

                if flag is 1:
                    flag = 0

    async def test_trace_middleware_exception(self, sanic_test_server, monkeypatch, client_session):

        monkeypatch.setattr(settings, 'SERVICE_LIST', {}, raising=False)

        url = f"http://127.0.0.1:{sanic_test_server.port}/trace_exception"
        async with client_session.request("GET", url) as resp:
            await resp.read()

            assert resp.status == 204, resp._body

    async def test_trace_middleware_interservice_exception(self, sanic_test_server, monkeypatch, client_session):

        monkeypatch.setattr(settings, 'SERVICE_LIST', {}, raising=False)

        url = f"http://127.0.0.1:{sanic_test_server.port}/trace_error_1"
        async with client_session.request("GET", url) as resp:
            await resp.read()
            assert resp.status == 204, resp._body

# class TestInterserviceTracing(TestTracing):
#
#     def test_non_incendiary_to_incendiary(self, sanic_test_server, ):
