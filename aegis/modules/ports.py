import asyncio
from urllib.parse import urlparse

class PortScannerModule:
    name = "ports"

    def __init__(self):
        # قائمة بالمنافذ الشائعة للفحص السريع
        self.common_ports = [21, 22, 80, 443, 3000, 5000, 8080]

    async def run(self, target: str, client) -> list[str]:
        findings = []
        parsed = urlparse(target)
        host = parsed.hostname or target.replace("https://", "").replace("http://", "").split("/")[0]

        for port in self.common_ports:
            try:
                # استخدام الاتصال غير المتزامن لفحص المنفذ بسرعة
                _, writer = await asyncio.wait_for(
                    asyncio.open_connection(host, port),
                    timeout=1.0
                )
                findings.append(f"Port {port} is OPEN")
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass

        return findings
