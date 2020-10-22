from typing import Tuple

TRACING_HOST = "xray"
TRACING_PORT = 2000

#: Determines if tracing should be enabled for this application.
TRACING_ENABLED: bool = True

#: Behavior when context is missing in X-Ray. Values can be :code:`LOG_ERROR` or :code:`RUNTIME_ERROR`.
TRACING_CONTEXT_MISSING_STRATEGY: str = "LOG_ERROR"  # or "RUNTIME_ERROR"

#: Modules to auto patch on initialization.
TRACING_PATCH_MODULES: Tuple[str] = ("aiobotocore",)

#: The default sampling value for fixed target.
DEFAULT_SAMPLING_FIXED_TARGET: int = 60 * 10

#: The default sampling rate.
DEFAULT_SAMPLING_RATE: float = 0.01

#: The local sampling rules for the recorder.
SAMPLING_RULES: dict = {
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
        "fixed_target": DEFAULT_SAMPLING_FIXED_TARGET,
        "rate": DEFAULT_SAMPLING_RATE,
    },
}
