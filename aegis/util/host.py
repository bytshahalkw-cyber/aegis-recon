from urllib.parse import urlparse

def extract_host(target: str) -> str:
    if "://" not in target:
        target = "http://" + target
    parsed = urlparse(target)
    return parsed.hostname or target
