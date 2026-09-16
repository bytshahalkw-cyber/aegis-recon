import httpx

class HttpClient:
    def __init__(self, settings=None, timeout=10.0, rate_limit=5):
        self.settings = settings
        self.timeout = timeout
        self.rate_limit = rate_limit
        self.client = None

    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=self.timeout, follow_redirects=True)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()

    async def get(self, url: str, **kwargs):
        if not self.client:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                return await client.get(url, **kwargs)
        return await self.client.get(url, **kwargs)
