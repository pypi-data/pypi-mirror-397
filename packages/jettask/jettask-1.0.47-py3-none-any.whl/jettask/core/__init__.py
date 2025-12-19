_lazy_imports = {
    "Jettask": ".app",
    "Task": ".task",
    "Request": ".task",
    "ExecuteResponse": ".task",
    "EventPool": "jettask.messaging.event_pool",
}

__all__ = ["Jettask", "Task", "Request", "ExecuteResponse", "EventPool"]


def __getattr__(name: str):
    if name in _lazy_imports:
        module_path = _lazy_imports[name]
        import importlib
        if module_path.startswith("."):
            module = importlib.import_module(module_path, package=__name__)
        else:
            module = importlib.import_module(module_path)
        return getattr(module, name)

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
