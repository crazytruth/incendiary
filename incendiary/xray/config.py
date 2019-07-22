TRACING_HOST = 'xray'
TRACING_PORT = 2000

# if true then tracing is enabled with this aplication
TRACING_ENABLED = True
TRACING_REQUIRED = True

# if true, even if xray is unable to be configured properly, application still runs
TRACING_SOFT_FAIL = True

TRACING_CONTEXT_MISSING_STRATEGY = "LOG_ERROR"  # or "RUNTIME_ERROR"

TRACING_PATCH_MODULES = ("aiobotocore", "pynamodb")
