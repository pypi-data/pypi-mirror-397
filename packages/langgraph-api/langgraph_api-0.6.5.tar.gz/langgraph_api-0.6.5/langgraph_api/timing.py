from __future__ import annotations

import functools
import inspect
import logging
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Generic, ParamSpec, TypeVar, overload

import structlog

if TYPE_CHECKING:
    from collections.abc import Callable
    from contextlib import AbstractAsyncContextManager

logger = structlog.stdlib.get_logger(__name__)

P = ParamSpec("P")
R = TypeVar("R")
T = TypeVar("T", covariant=True)


def _pick_level_and_message(
    *,
    elapsed: float,
    message: str,
    warn_threshold_secs: float | None,
    warn_message: str | None,
    error_threshold_secs: float | None,
    error_message: str | None,
) -> tuple[int, str]:
    level = logging.INFO
    msg = message

    if warn_threshold_secs is not None and elapsed > warn_threshold_secs:
        level = logging.WARNING
        if warn_message is not None:
            msg = warn_message

    if error_threshold_secs is not None and elapsed > error_threshold_secs:
        level = logging.ERROR
        if error_message is not None:
            msg = error_message

    return level, msg


@dataclass(frozen=True)
class TimerConfig(Generic[P]):
    message: str = "Function timing"
    metadata_fn: Callable[P, dict[str, Any]] | None = None
    warn_threshold_secs: float | None = None
    warn_message: str | None = None
    error_threshold_secs: float | None = None
    error_message: str | None = None


def _log_timing(
    *,
    name: str,
    elapsed: float,
    cfg: TimerConfig[Any],
    args: tuple[Any, ...] = (),
    kwargs: dict[str, Any] | None = None,
    exc: BaseException | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    kwargs = kwargs or {}

    log_data: dict[str, Any] = {
        "name": name,
        "elapsed_seconds": elapsed,
    }

    if extra:
        log_data.update(extra)

    if cfg.metadata_fn is not None:
        try:
            md = cfg.metadata_fn(*args, **kwargs)  # type: ignore[misc]
            if not isinstance(md, dict):
                raise TypeError("metadata_fn must return a dict")
            log_data.update(md)
        except Exception as meta_exc:
            log_data["metadata_error"] = repr(meta_exc)

    if exc is not None:
        log_data["exception"] = repr(exc)

    level, msg = _pick_level_and_message(
        elapsed=elapsed,
        message=cfg.message,
        warn_threshold_secs=cfg.warn_threshold_secs,
        warn_message=cfg.warn_message,
        error_threshold_secs=cfg.error_threshold_secs,
        error_message=cfg.error_message,
    )

    # Allow {graph_id} etc.
    msg = msg.format(**log_data)
    logger.log(level, msg, **log_data)


@overload
def timer(_func: Callable[P, R], /, **kwargs) -> Callable[P, R]: ...
@overload
def timer(
    _func: None = None, /, **kwargs
) -> Callable[[Callable[P, R]], Callable[P, R]]: ...


def timer(
    _func: Callable[P, R] | None = None,
    /,
    message: str = "Function timing",
    metadata_fn: Callable[P, dict[str, Any]] | None = None,
    warn_threshold_secs: float | None = None,
    warn_message: str | None = None,
    error_threshold_secs: float | None = None,
    error_message: str | None = None,
):
    """
    Decorator for sync *and* async callables.
    """
    cfg = TimerConfig[P](
        message=message,
        metadata_fn=metadata_fn,
        warn_threshold_secs=warn_threshold_secs,
        warn_message=warn_message,
        error_threshold_secs=error_threshold_secs,
        error_message=error_message,
    )

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        if inspect.iscoroutinefunction(func):

            @functools.wraps(func)
            async def awrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                start = time.perf_counter()
                exc: BaseException | None = None
                try:
                    return await func(*args, **kwargs)  # type: ignore[misc]
                except BaseException as e:
                    exc = e
                    raise
                finally:
                    elapsed = time.perf_counter() - start
                    _log_timing(
                        name=func.__qualname__,
                        elapsed=elapsed,
                        cfg=cfg,  # type: ignore[arg-type]
                        args=args,
                        kwargs=kwargs,
                        exc=exc,
                    )

            return awrapper  # type: ignore[return-value]

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            start = time.perf_counter()
            exc: BaseException | None = None
            try:
                return func(*args, **kwargs)
            except BaseException as e:
                exc = e
                raise
            finally:
                elapsed = time.perf_counter() - start
                _log_timing(
                    name=func.__qualname__,
                    elapsed=elapsed,
                    cfg=cfg,  # type: ignore[arg-type]
                    args=args,
                    kwargs=kwargs,
                    exc=exc,
                )

        return wrapper

    return decorator(_func) if _func is not None else decorator


class aenter_timed(Generic[T]):
    """
    Wraps an async context manager and logs the time spent in *its __aenter__*.
    __aexit__ is delegated without additional timing.
    """

    def __init__(
        self,
        inner: AbstractAsyncContextManager[T],
        *,
        name: str,
        cfg: TimerConfig[Any],
        extra: dict[str, Any] | None = None,
    ) -> None:
        self._inner = inner
        self._name = name
        self._cfg = cfg
        self._extra = extra or {}

    async def __aenter__(self) -> T:
        start = time.perf_counter()
        exc: BaseException | None = None
        try:
            return await self._inner.__aenter__()
        except BaseException as e:
            exc = e
            raise
        finally:
            elapsed = time.perf_counter() - start
            _log_timing(
                name=self._name,
                elapsed=elapsed,
                cfg=self._cfg,
                exc=exc,
                extra=self._extra,
            )

    async def __aexit__(self, exc_type, exc, tb) -> bool | None:
        return await self._inner.__aexit__(exc_type, exc, tb)


def time_aenter(
    cm: AbstractAsyncContextManager[T],
    *,
    name: str,
    message: str,
    warn_threshold_secs: float | None = None,
    warn_message: str | None = None,
    error_threshold_secs: float | None = None,
    error_message: str | None = None,
    extra: dict[str, Any] | None = None,
) -> aenter_timed[T]:
    """
    Convenience helper to wrap any async CM and time only its __aenter__.
    """
    cfg = TimerConfig[Any](
        message=message,
        warn_threshold_secs=warn_threshold_secs,
        warn_message=warn_message,
        error_threshold_secs=error_threshold_secs,
        error_message=error_message,
        metadata_fn=None,
    )
    return aenter_timed(cm, name=name, cfg=cfg, extra=extra)


def wrap_lifespan_context_aenter(
    lifespan_ctx: Callable[[Any], AbstractAsyncContextManager[Any]],
    *,
    name: str = "user_router.lifespan",
    message: str = "Entered lifespan context",
    warn_threshold_secs: float | None = 10,
    warn_message: str | None = (
        "User lifespan startup exceeded expected time. "
        "Slow work done at entry time within lifespan context can delay readiness, "
        "reduce scale-out capacity, and may cause deployments to be marked unhealthy."
    ),
    error_threshold_secs: float | None = 30,
    error_message: str | None = None,
) -> Callable[[Any], AbstractAsyncContextManager[Any]]:
    @functools.wraps(lifespan_ctx)
    def wrapped(app: Any) -> AbstractAsyncContextManager[Any]:
        return time_aenter(
            lifespan_ctx(app),
            name=name,
            message=message,
            warn_threshold_secs=warn_threshold_secs,
            warn_message=warn_message,
            error_threshold_secs=error_threshold_secs,
            error_message=error_message,
        )

    return wrapped
