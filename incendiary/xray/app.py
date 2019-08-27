import socket

from insanic.exceptions import ImproperlyConfigured
from insanic.monitor import MONITOR_ENDPOINTS
from insanic.services import Service

from incendiary.loggers import logger, error_logger
from incendiary.xray import config
from incendiary.xray.clients import aws_xray_trace_config
from incendiary.xray.contexts import IncendiaryAsyncContext
from incendiary.xray.middlewares import before_request, after_request
from incendiary.xray.mixins import CaptureMixin
from incendiary.xray.sampling import IncendiaryDefaultSampler
from incendiary.xray.utils import tracing_name

from aws_xray_sdk.core import patch, xray_recorder, AsyncAWSXRayRecorder
from aws_xray_sdk import global_sdk_config


class Incendiary(CaptureMixin):
    config_imported = False
    extra_recorder_configurations = {}
    app = None

    @classmethod
    def load_config(self, settings_object):
        if not self.config_imported:
            for c in dir(config):
                if c.isupper():
                    conf = getattr(config, c)
                    setattr(settings_object, c, conf)
            self.config_imported = True

    @classmethod
    def _handle_error(cls, app, messages):
        error_message = "[XRAY] Tracing was not initialized because: " + ', '.join(messages)
        error_logger.warning(error_message)

    @classmethod
    def _check_prerequisites(cls, app):
        """
        checks to see if xray is accessiable


        :param app: Insanic application
        :return: list of error messages while checking
        :rtype: list
        """
        messages = []
        tracing_host = app.config.TRACING_HOST
        tracing_port = app.config.TRACING_PORT

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:  # pragma: no cover
            socket.gethostbyname(tracing_host)
            sock.settimeout(1)
            if sock.connect_ex((tracing_host, int(tracing_port))) != 0:
                messages.append(
                    f"Could not connect to port on [{tracing_host}:{tracing_port}].")
        except socket.gaierror:
            messages.append(f"Could not resolve host [{tracing_host}].")
        except socket.error as e:  # pragma: no cover
            messages.append(f"Could not connect to [{tracing_host}:{tracing_port}]: {str(e)}")
        finally:
            sock.close()
        return messages

    @classmethod
    def init_app(cls, app):
        # checks to see if tracing can be enabled
        cls.app = app
        cls.load_config(app.config)
        messages = cls._check_prerequisites(app)

        if len(messages) == 0:
            global_sdk_config.set_sdk_enabled(True)
            # app.xray_recorder = AsyncAWSXRayRecorder()
            app.xray_recorder = xray_recorder

            cls.setup_middlewares(app)
            cls.setup_client(app)
            cls.setup_listeners(app)

            patch(app.config.TRACING_PATCH_MODULES, raise_errors=False)
            app.plugin_initialized('incendiary', cls)
        else:
            cls._handle_error(app, messages)
            app.config.TRACING_ENABLED = False
            global_sdk_config.set_sdk_enabled(False)

    @classmethod
    def setup_listeners(cls, app):
        async def before_server_start_start_tracing(app, loop=None, **kwargs):
            app.xray_recorder.configure(**cls.xray_config(app))

        # need to configure xray as the first thing that happens so insert into 0
        if before_server_start_start_tracing not in app.listeners['before_server_start']:
            app.listeners['before_server_start'].insert(0, before_server_start_start_tracing)

    @classmethod
    def setup_client(cls, app):
        Service.extra_session_configs = {'trace_configs': [aws_xray_trace_config(xray_recorder=app.xray_recorder)]}

    @classmethod
    def setup_middlewares(cls, app):
        logger.debug("[XRAY] Initializing xray middleware")

        @app.middleware('request')
        async def start_trace(request):
            for ep in MONITOR_ENDPOINTS:
                if request.path.endswith(ep):
                    break
            else:
                await before_request(request)

        @app.middleware('response')
        async def end_trace(request, response):
            for ep in MONITOR_ENDPOINTS:
                if request.path.endswith(ep):
                    break
            else:
                await after_request(request, response)

            return response

    @classmethod
    def xray_config(cls, app):
        config = dict(
            service=tracing_name(app.config.SERVICE_NAME),
            context=IncendiaryAsyncContext(),
            sampling=True,
            sampler=IncendiaryDefaultSampler(app),
            # sampling_rules=app.sampler.sampling_rules,
            daemon_address=f"{app.config.TRACING_HOST}:{app.config.TRACING_PORT}",
            context_missing=app.config.TRACING_CONTEXT_MISSING_STRATEGY,
            streaming_threshold=10,
            plugins=('ECSPlugin',),
        )

        config.update(cls.extra_recorder_configurations)

        return config
