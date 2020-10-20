TRACING_HOST = "xray"
TRACING_PORT = 2000

# if true then tracing is enabled with this aplication
TRACING_ENABLED = True
TRACING_REQUIRED = True

# if true, even if xray is unable to be configured properly, application still runs
TRACING_SOFT_FAIL = True

TRACING_CONTEXT_MISSING_STRATEGY = "LOG_ERROR"  # or "RUNTIME_ERROR"

TRACING_PATCH_MODULES = ("aiobotocore", "pynamodb")

DEFAULT_SAMPLING_FIXED_TARGET = 60 * 10
DEFAULT_SAMPLING_RATE = 0.01

SAMPLING_RULES = {
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
