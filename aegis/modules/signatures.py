import yaml
import re
from pathlib import Path

class SignaturesModule:
    name = "signatures"

    def __init__(self, sig_file: str = "signatures.yaml"):
        self.sig_file = Path(sig_file)
        self.signatures = []
        if self.sig_file.exists():
            try:
                self.signatures = yaml.safe_load(self.sig_file.read_text(encoding="utf-8")) or []
            except Exception:
                self.signatures = []

    async def run(self, target: str, client) -> list[str]:
        findings = []
        if not self.signatures:
            return findings

        base_url = target.rstrip("/")

        for sig in self.signatures:
            sig_name = sig.get("name", "Custom Signature")
            paths = sig.get("paths", [])
            allowed_statuses = sig.get("match_status", [200])
            match_regex = sig.get("match_regex")
            severity = sig.get("severity", "MEDIUM")

            for path in paths:
                url = f"{base_url}{path}"
                try:
                    response = await client.get(url, follow_redirects=False, timeout=5.0)
                    if response.status_code in allowed_statuses:
                        matched = True
                        if match_regex:
                            if not re.search(match_regex, response.text):
                                matched = False

                        if matched:
                            findings.append(
                                f"[{severity}] Signature Matched: {sig_name} at {url} (Status: {response.status_code})"
                            )
                except Exception:
                    continue

        return findings
