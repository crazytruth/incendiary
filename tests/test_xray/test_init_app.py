import pytest
import logging

from aws_xray_sdk.core import AsyncAWSXRayRecorder
from insanic.conf import settings

from insanic.exceptions import ImproperlyConfigured

from incendiary.xray.app import Incendiary
from incendiary.xray.services import IncendiaryService

logger = logging.getLogger(__name__)


class TestIncendiaryXRayInitialize:
    def test_init_but_errors(self, insanic_application, monkeypatch):
        def mock_check_prerequisites(*args, **kwargs):
            return ["FAILED"]

        monkeypatch.setattr(
            Incendiary, "_check_prerequisites", mock_check_prerequisites
        )

        Incendiary.init_app(insanic_application)

        assert insanic_application.config.INCENDIARY_XRAY_ENABLED is False

    def test_prerequisites_host_error(self, insanic_application, monkeypatch):
        monkeypatch.setattr(settings, "INCENDIARY_XRAY_DAEMON_HOST", "xray")

        errors = Incendiary._check_prerequisites(insanic_application)

        assert errors != []
        assert errors[0].startswith("Could not resolve host")

    @pytest.mark.parametrize(
        "soft_fail, required, expected",
        (
            (False, False, "LOG"),
            (True, False, "LOG"),
            (False, True, "LOG"),
            (True, True, "LOG"),
        ),
    )
    def test_handle_error(
        self,
        insanic_application,
        monkeypatch,
        soft_fail,
        required,
        expected,
        caplog,
    ):
        EXPECTED_ERROR_MESSAGE = (
            "[XRAY] Tracing was not initialized because: Hello"
        )

        if expected == "LOG":
            Incendiary._handle_error(insanic_application, ["Hello"])
            assert len(caplog.records) != 0
            assert caplog.records[-1].levelname == "CRITICAL"
            assert caplog.records[-1].message == EXPECTED_ERROR_MESSAGE
        elif expected == "EXCEPTION":
            with pytest.raises(ImproperlyConfigured) as e:
                Incendiary._handle_error(insanic_application, ["Hello"])
            assert str(e.value) == EXPECTED_ERROR_MESSAGE

    def test_setup_middlewares(self, insanic_application, monkeypatch):

        Incendiary.setup_middlewares(insanic_application)

        assert "start_trace" in [
            m.__name__ for m in insanic_application.request_middleware
        ]
        assert "end_trace" in [
            m.__name__ for m in insanic_application.response_middleware
        ]

    def test_setup_listeners(self, insanic_application):
        Incendiary.setup_listeners(insanic_application)

        assert (
            insanic_application.listeners["before_server_start"][1].__name__
            == "before_server_start_start_tracing"
        )

    def test_setup_client(self, insanic_application):
        insanic_application.xray_recorder = AsyncAWSXRayRecorder()

        Incendiary.setup_client(insanic_application)
        from insanic.services.registry import registry

        assert registry.service_class == IncendiaryService
        assert hasattr(registry.service_class, "xray_recorder")

    def test_init(self, insanic_application, monkeypatch):
        def mock_check_prerequisites(*args, **kwargs):
            return []

        monkeypatch.setattr(
            Incendiary, "_check_prerequisites", mock_check_prerequisites
        )

        Incendiary.init_app(insanic_application)

        assert "start_trace" in [
            m.__name__ for m in insanic_application.request_middleware
        ]
        assert "end_trace" in [
            m.__name__ for m in insanic_application.response_middleware
        ]

        from insanic.services.registry import registry

        assert registry.service_class == IncendiaryService
        assert hasattr(registry.service_class, "xray_recorder")
        assert (
            insanic_application.listeners["before_server_start"][1].__name__
            == "before_server_start_start_tracing"
        )
