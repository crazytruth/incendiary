import socket
from typing import List

from insanic import Insanic
from insanic.monitor import MONITOR_ENDPOINTS
from sanic.config import Config

from incendiary.loggers import logger, error_logger
from incendiary.xray import config
from incendiary.xray.contexts import IncendiaryAsyncContext
from incendiary.xray.middlewares import before_request, after_request
from incendiary.xray.mixins import CaptureMixin
from incendiary.xray.sampling import IncendiaryDefaultSampler
from incendiary.xray.services import IncendiaryService
from incendiary.xray.utils import tracing_name

from aws_xray_sdk.core import patch, AsyncAWSXRayRecorder, xray_recorder
from aws_xray_sdk import global_sdk_config


class Incendiary(CaptureMixin):
    config_imported = False
    extra_recorder_configurations = {}
    app = None

    @classmethod
    def load_config(cls, settings_object: Config) -> None:
        if not cls.config_imported:
            for c in dir(config):
                if c.isupper():
                    if not hasattr(settings_object, c):
                        conf = getattr(config, c)
                        setattr(settings_object, c, conf)
            cls.config_imported = True

    @classmethod
    def _handle_error(cls, app: Insanic, messages: List[str]) -> None:
        error_message = (
            "[XRAY] Tracing was not initialized because: " + ", ".join(messages)
        )
        error_logger.critical(error_message)

    @classmethod
    def _check_prerequisites(cls, app: Insanic) -> List[str]:
        """
        Checks to see if xray daemon is accessible
        with :code:`INCENDIARY_XRAY_DAEMON_HOST` and :code:`INCENDIARY_XRAY_DAEMON_PORT`.

        :return: List of error messages while validating xray prerequisites.
        """
        messages = []
        tracing_host = app.config.INCENDIARY_XRAY_DAEMON_HOST
        tracing_port = app.config.INCENDIARY_XRAY_DAEMON_PORT

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:  # pragma: no cover
            socket.gethostbyname(tracing_host)
            sock.settimeout(1)
            if sock.connect_ex((tracing_host, int(tracing_port))) != 0:
                messages.append(
                    f"Could not connect to port on [{tracing_host}:{tracing_port}]."
                )
        except socket.gaierror:
            messages.append(f"Could not resolve host [{tracing_host}].")
        except socket.error as e:  # pragma: no cover
            messages.append(
                f"Could not connect to [{tracing_host}:{tracing_port}]: {str(e)}"
            )
        finally:
            sock.close()
        return messages

    @classmethod
    def init_app(
        cls, app: Insanic, recorder: AsyncAWSXRayRecorder = None
    ) -> None:
        """
        Initializes Insanic to use Incendiary.

        -   This loads all default Incendiary configs.
        -   Validates connection information to X-Ray Daemon.
        -   Configures X-Ray SDK Recorder
        -   Attaches middlewares to start stop segments
        -   Replaces :code:`Service` object with :code:`IncendiaryService`
            to trace interservice communications.
        -   Replaces asyncio task factory.
        -   Patches configured modules.

        :param app: Your Insanic application/
        :param recorder: If you want to use your own recorder.
        """
        # checks to see if tracing can be enabled
        cls.app = app
        cls.load_config(app.config)
        messages = cls._check_prerequisites(app)

        if len(messages) == 0:
            global_sdk_config.set_sdk_enabled(True)
            app.xray_recorder = recorder or xray_recorder

            cls.setup_middlewares(app)
            cls.setup_client(app)
            cls.setup_listeners(app)

            patch(app.config.INCENDIARY_XRAY_PATCH_MODULES, raise_errors=False)
            app.plugin_initialized("incendiary", cls)
        else:
            cls._handle_error(app, messages)
            app.config.INCENDIARY_XRAY_ENABLED = False
            global_sdk_config.set_sdk_enabled(False)

    @classmethod
    def setup_listeners(cls, app: Insanic) -> None:
        """
        -   Attaches before server start listener that configures
            the X-Ray Recorder.
        -   Attaches a before server start listener that
            replaces the default asyncio task factory that can
            hold context.
        """

        async def before_server_start_start_tracing(app, loop=None, **kwargs):
            app.xray_recorder.configure(**cls.xray_config(app))

        # need to configure xray as the first thing that happens so insert into 0
        if (
            before_server_start_start_tracing
            not in app.listeners["before_server_start"]
        ):

            # need to attach context after insanic's set task factory has been set
            for i, l in enumerate(app.listeners["before_server_start"]):
                if l.__name__ == "before_server_start_set_task_factory":
                    insert_index = i + 1
                    break
            else:
                insert_index = 0

            app.listeners["before_server_start"].insert(
                insert_index, before_server_start_start_tracing
            )

    @classmethod
    def setup_client(cls, app: Insanic) -> None:
        """
        Replaces the :code:`Service` class on the service registry
        with :code:`IncendiaryService`.
        """
        from insanic.services.registry import LazyServiceRegistry

        LazyServiceRegistry.service_class = IncendiaryService
        LazyServiceRegistry.service_class.xray_recorder = app.xray_recorder

    @classmethod
    def setup_middlewares(cls, app: Insanic) -> None:
        """
        Sets up request and response middlewares that starts a
        segment, or creates segment, and ends the segment on
        response.
        """
        logger.debug("[XRAY] Initializing xray middleware")

        @app.middleware("request")
        async def start_trace(request):
            for ep in MONITOR_ENDPOINTS:
                if request.path.endswith(ep):
                    break
            else:
                await before_request(request)

        @app.middleware("response")
        async def end_trace(request, response):
            for ep in MONITOR_ENDPOINTS:
                if request.path.endswith(ep):
                    break
            else:
                await after_request(request, response)

            return response

    @classmethod
    def xray_config(cls, app: Insanic) -> dict:
        """
        Class method that returns all the configurations for
        the X-Ray SDK Recoder.
        """
        xray_config = dict(
            service=tracing_name(app.config.SERVICE_NAME),
            context=IncendiaryAsyncContext(),
            sampling=True,
            sampler=IncendiaryDefaultSampler(app),
            # sampling_rules=app.sampler.sampling_rules,
            daemon_address=f"{app.config.INCENDIARY_XRAY_DAEMON_HOST}:{app.config.INCENDIARY_XRAY_DAEMON_PORT}",
            context_missing=app.config.INCENDIARY_XRAY_CONTEXT_MISSING_STRATEGY,
            streaming_threshold=10,
            plugins=("ECSPlugin",),
        )

        xray_config.update(cls.extra_recorder_configurations)

        return xray_config
