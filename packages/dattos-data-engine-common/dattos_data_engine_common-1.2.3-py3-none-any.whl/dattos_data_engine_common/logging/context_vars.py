from contextvars import ContextVar

version_contextvar = ContextVar("version", default=None)
trace_id_contextvar = ContextVar("trace_id", default=None)
website_contextvar = ContextVar("website", default=None)
path_contextvar = ContextVar("path", default=None)
user_code_contextvar = ContextVar("user_code", default=None)
