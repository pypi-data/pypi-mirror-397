"""
JetTask - High Performance Distributed Task Queue System

轻量级导入:
    from jettask import TaskMessage  # 不会加载数据库依赖

完整导入:
    from jettask import Jettask  # 会加载所有依赖
"""

import logging
import inspect

from jettask.core.message import TaskMessage
from jettask.core.context import TaskContext
from jettask.utils.task_logger import (
    TaskContextFilter,
    ExtendedTextFormatter,
    LogContext
)

__version__ = "0.1.0"


def get_task_logger(name: str = None) -> logging.Logger:
    if name is None:
        frame = inspect.currentframe()
        if frame and frame.f_back:
            name = frame.f_back.f_globals.get('__name__', 'jettask')
        else:
            name = 'jettask'

    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(ExtendedTextFormatter(
            '%(asctime)s - %(levelname)s - [%(task_id)s] - %(name)s - %(message)s'
        ))
        handler.addFilter(TaskContextFilter())
        logger.addHandler(handler)
        logger.propagate = False

    return logger


_lazy_imports = {
    "Jettask": "jettask.core.app",
    "TaskRouter": "jettask.task.router",
    "Schedule": "jettask.scheduler.definition",
    "QPSLimit": "jettask.utils.rate_limit.config",
    "ConcurrencyLimit": "jettask.utils.rate_limit.config",
}


def __getattr__(name: str):
    if name in _lazy_imports:
        module_path = _lazy_imports[name]
        import importlib
        module = importlib.import_module(module_path)
        return getattr(module, name)

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "Jettask",
    "Schedule",
    "TaskRouter",
    "QPSLimit",
    "ConcurrencyLimit",
    "TaskMessage",
    "TaskContext",
    "get_task_logger",
    "LogContext",
]
