import asyncio
import time
import uuid
import random
import httpx

# ترويسات محاكاة المتصفحات لتجنب الحجب
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
]

async def check_path(client: httpx.AsyncClient, base_url: str, path: str, baseline_len: int, baseline_status: int, semaphore: asyncio.Semaphore):
    url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
    async with semaphore:
        start_time = time.time()
        try:
            headers = {"User-Agent": random.choice(USER_AGENTS)}
            response = await client.get(url, headers=headers, follow_redirects=True)
            elapsed = time.time() - start_time
            content_length = len(response.content)
            
            # كشف الـ Soft 404 بمقارنة خط الأساس
            is_soft_404 = (response.status_code == baseline_status and content_length == baseline_len)
            
            if is_soft_404:
                print(f"[-] [Soft 404] [Size: {content_length}b] {url} ({elapsed:.2f}s)")
            else:
                print(f"[+] [VALID?] [{response.status_code}] [Size: {content_length}b] {url} ({elapsed:.2f}s)")
                
            return {
                "path": url, 
                "status_code": response.status_code, 
                "content_length": content_length,
                "is_soft_404": is_soft_404,
                "elapsed": round(elapsed, 2)
            }
        except Exception as e:
            print(f"[-] Error scanning {url}: {e}")
            return {"path": url, "status_code": None, "error": str(e)}

async def run_scanner(base_url: str, paths: list, concurrency: int = 10):
    semaphore = asyncio.Semaphore(concurrency)
    limits = httpx.Limits(max_keepalive_connections=concurrency, max_connections=concurrency * 2)
    
    async with httpx.AsyncClient(limits=limits, timeout=10.0) as client:
        # 1. تأسيس خط الأساس (Baseline) عبر UUID عشوائي
        random_path = f"aegis_{uuid.uuid4().hex[:8]}"
        baseline_url = f"{base_url.rstrip('/')}/{random_path}"
        print(f"[*] Establishing baseline...")
        
        try:
            base_headers = {"User-Agent": random.choice(USER_AGENTS)}
            base_resp = await client.get(baseline_url, headers=base_headers, follow_redirects=True)
            baseline_len = len(base_resp.content)
            baseline_status = base_resp.status_code
            print(f"[*] Baseline established: Status [{baseline_status}], Size [{baseline_len}b]")
        except Exception:
            baseline_len = -1
            baseline_status = -1
            print("[-] Could not establish baseline, proceeding without Soft 404 filtering.")

        # 2. تشغيل الفحص المتزامن لجميع المسارات
        print(f"[*] Scanning {len(paths)} paths...")
        tasks = [check_path(client, base_url, p, baseline_len, baseline_status, semaphore) for p in paths]
        results = await asyncio.gather(*tasks)
        return results
