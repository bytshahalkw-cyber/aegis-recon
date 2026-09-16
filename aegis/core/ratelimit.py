import asyncio
import time

class RateLimiter:
    def __init__(self, rate_limit: float):
        self.rate_limit = rate_limit  # طلبات في الثانية
        self.interval = 1.0 / rate_limit if rate_limit > 0 else 0
        self.last_check = time.monotonic()
        self.lock = asyncio.Lock()

    async def acquire(self):
        if self.rate_limit <= 0:
            return
        async with self.lock:
            now = time.monotonic()
            elapsed = now - self.last_check
            wait_time = self.interval - elapsed
            if wait_time > 0:
                await asyncio.sleep(wait_time)
            self.last_check = time.monotonic()
