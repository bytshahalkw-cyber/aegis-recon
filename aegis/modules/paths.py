import asyncio

class PathDiscoveryModule:
    name = "paths"

    def __init__(self):
        # قائمة خفيفة للمسارات الشائعة للاختبار
        self.paths_to_check = [
            "robots.txt",
            "sitemap.xml",
            ".git/HEAD",
            ".env",
            "admin/",
            "api/",
            "config.json",
            "backup.zip"
        ]

    async def run(self, target: str, client) -> list[str]:
        findings = []
        base_url = target.rstrip("/")

        for path in self.paths_to_check:
            url = f"{base_url}/{path}"
            try:
                # إرسال طلب GET وفحص الحالة
                response = await client.get(url)
                if response.status_code in [200, 301, 302, 403]:
                    finding_msg = f"Found path: /{path} [Status: {response.status_code}]"
                    findings.append(finding_msg)
            except Exception:
                # تجاهل أخطاء الاتصال الفردية للمسارات
                pass
            
            # تأخير بسيط لتجنب الضغط أو الحظر
            await asyncio.sleep(0.2)

        return findings
