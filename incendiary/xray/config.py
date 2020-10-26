from typing import Tuple

#: Determines if tracing should be enabled for this application.
INCENDIARY_XRAY_ENABLED: bool = True

#: The host of the running X-Ray Daemon
INCENDIARY_XRAY_DAEMON_HOST: str = "127.0.0.1"

#: The port of the running X-Ray Daemon
INCENDIARY_XRAY_DAEMON_PORT: int = 2000

#: Behavior when context is missing in X-Ray. Values can be :code:`LOG_ERROR` or :code:`RUNTIME_ERROR`.
INCENDIARY_XRAY_CONTEXT_MISSING_STRATEGY: str = "LOG_ERROR"  # or "RUNTIME_ERROR"

#: Modules to auto patch on initialization.
INCENDIARY_XRAY_PATCH_MODULES: Tuple[str] = ("aiobotocore",)

#: The default sampling value for fixed target.
INCENDIARY_XRAY_DEFAULT_SAMPLING_FIXED_TARGET: int = 60 * 10

#: The default sampling rate.
INCENDIARY_XRAY_DEFAULT_SAMPLING_RATE: float = 0.01

#: The local sampling rules for the recorder.
INCENDIARY_XRAY_SAMPLING_RULES: dict = {
    "version": 1,
    "rules": [
        # {
        #     "description": "Player moves.",
        #     "service_name": "*",
        #     "http_method": "*",
        #     "url_path": "/api/move/*",
        #     "fixed_target": 0,
        #     "rate": 0.05
        # }
    ],
    "default": {
        "fixed_target": INCENDIARY_XRAY_DEFAULT_SAMPLING_FIXED_TARGET,
        "rate": INCENDIARY_XRAY_DEFAULT_SAMPLING_RATE,
    },
}
