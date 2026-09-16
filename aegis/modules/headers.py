class HeadersModule:
    name = "headers"

    async def run(self, target: str, client):
        findings = []
        try:
            response = await client.get(target)
            headers = response.headers
            
            # فحص وجود بعض الترويسات الأمنية المهمة
            security_headers = [
                "content-security-policy",
                "x-frame-options",
                "x-content-type-options",
                "strict-transport-security"
            ]
            
            for h in security_headers:
                if h not in headers:
                    findings.append(f"Missing security header: {h}")
        except Exception as e:
            findings.append(f"Error fetching headers: {e}")

        return findings
