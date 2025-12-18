import time
from dataclasses import dataclass
from functools import wraps
from typing import Callable, Deque, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


@dataclass
class RateLimitConfig:
    max_calls: int = 0  # 限流次数
    time_window: float = 0  # 限流时间窗口（秒）


def rate_limited(func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        self = args[0]
        config: RateLimitConfig | None = getattr(self, "rate_limit_config", None)
        call_timestamps: Deque[float] | None = getattr(self, "call_timestamps", None)
        if config and call_timestamps is not None:
            if config.max_calls <= 0 or config.time_window <= 0:
                return func(*args, **kwargs)
            """限流 + 处理用户请求"""
            while True:
                current_time = time.time()
                # 移除超出时间窗口的记录
                while call_timestamps and call_timestamps[0] < current_time - config.time_window:
                    call_timestamps.popleft()
                # 如果调用次数小于最大限制，立即执行
                if len(call_timestamps) < config.max_calls:
                    break  # 退出 while，执行请求
                # 计算下一个可用时间点
                next_available_time = call_timestamps[0] + config.time_window
                sleep_time = max(0, next_available_time - current_time) + 0.1
                print(f"Rate limit exceeded. Sleeping for {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)  # 阻塞线程，等待可用时间点
            # 记录当前调用时间
            call_timestamps.append(time.time())
        return func(*args, **kwargs)

    return wrapper
