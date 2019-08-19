import pytest
import logging

from aiohttp.tracing import TraceConfig
from aws_xray_sdk.core import AsyncAWSXRayRecorder

from insanic.exceptions import ImproperlyConfigured
from insanic.services import Service

from incendiary.xray.app import Incendiary

logger = logging.getLogger(__name__)


class TestIncendiaryXRayInitialize():

    def test_init_but_errors(self, insanic_application, monkeypatch):
        def mock_check_prerequisites(*args, **kwargs):
            return ["FAILED"]

        monkeypatch.setattr(Incendiary, '_check_prerequisites', mock_check_prerequisites)

        with pytest.raises(ImproperlyConfigured):
            Incendiary.init_app(insanic_application)

        assert insanic_application.config.TRACING_ENABLED == False

    def test_prerequisites_host_error(self, insanic_application):
        errors = Incendiary._check_prerequisites(insanic_application)

        assert errors != []
        assert errors[0].startswith('Could not resolve host')

    @pytest.mark.parametrize(
        'soft_fail, required, expected',
        (
                (False, False, "EXCEPTION"),
                (True, False, "LOG"),
                (False, True, "EXCEPTION"),
                (True, True, "EXCEPTION")
        )
    )
    def test_handle_error(self, insanic_application, monkeypatch, soft_fail, required, expected, caplog):
        EXPECTED_ERROR_MESSAGE = '[XRAY] Tracing was not initialized because: Hello'

        monkeypatch.setattr(insanic_application.config, 'TRACING_SOFT_FAIL', soft_fail)
        monkeypatch.setattr(insanic_application.config, 'TRACING_REQUIRED', required)

        if expected == "LOG":
            Incendiary._handle_error(insanic_application, ["Hello"])
            assert len(caplog.records) != 0
            assert caplog.records[-1].levelname == "WARNING"
            assert caplog.records[-1].message == EXPECTED_ERROR_MESSAGE
        elif expected == "EXCEPTION":
            with pytest.raises(ImproperlyConfigured) as e:
                Incendiary._handle_error(insanic_application, ['Hello'])
            assert str(e.value) == EXPECTED_ERROR_MESSAGE

    def test_setup_middlewares(self, insanic_application, monkeypatch):

        Incendiary.setup_middlewares(insanic_application)

        assert "start_trace" in [m.__name__ for m in insanic_application.request_middleware]
        assert "end_trace" in [m.__name__ for m in insanic_application.response_middleware]

    def test_setup_listeners(self, insanic_application):
        Incendiary.setup_listeners(insanic_application)

        assert insanic_application.listeners['before_server_start'][0].__name__ == "before_server_start_start_tracing"

    def test_setup_client(self, insanic_application):
        insanic_application.xray_recorder = AsyncAWSXRayRecorder()

        Incendiary.setup_client(insanic_application)

        assert "trace_configs" in Service.extra_session_configs
        assert isinstance(Service.extra_session_configs['trace_configs'][0], TraceConfig)

    def test_init(self, insanic_application, monkeypatch):
        def mock_check_prerequisites(*args, **kwargs):
            return []

        monkeypatch.setattr(Incendiary, '_check_prerequisites', mock_check_prerequisites)

        Incendiary.init_app(insanic_application)

        assert "start_trace" in [m.__name__ for m in insanic_application.request_middleware]
        assert "end_trace" in [m.__name__ for m in insanic_application.response_middleware]

        assert "trace_configs" in Service.extra_session_configs
        assert isinstance(Service.extra_session_configs['trace_configs'][0], TraceConfig)
        assert insanic_application.listeners['before_server_start'][0].__name__ == "before_server_start_start_tracing"
