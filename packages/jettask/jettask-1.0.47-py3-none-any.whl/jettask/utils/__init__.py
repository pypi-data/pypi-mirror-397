from .helpers import get_hostname, gen_task_name, is_async_function
from .task_logger import get_task_logger

__all__ = [
    "get_hostname",
    "gen_task_name",
    "is_async_function",
    "get_task_logger",
]


def __getattr__(name: str):
    db_exports = {
        "get_sync_redis_pool",
        "get_async_redis_pool",
        "get_pg_engine_and_factory",
        "get_sync_redis_client",
        "get_async_redis_client",
        "get_dual_mode_async_redis_client",
        "DBConfig",
    }

    if name in db_exports:
        from jettask.db import connector
        return getattr(connector, name)

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")