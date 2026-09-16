from urllib.parse import urlparse

class ScopeGuard:
    def __init__(self, allowed_domain: str):
        self.allowed_domain = allowed_domain.lower().strip()

    def is_allowed(self, target: str) -> bool:
        if not target.startswith("http"):
            target = f"http://{target}"
        parsed = urlparse(target)
        hostname = (parsed.hostname or "").lower()
        return hostname == self.allowed_domain or hostname.endswith(f".{self.allowed_domain}")
