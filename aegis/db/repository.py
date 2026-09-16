from sqlalchemy.future import select
from aegis.db.models import Target, Scan, Finding as DBFinding, ScanStatus
from aegis.core.finding import Finding

class Repository:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def get_or_create_target(self, url: str, host: str, scope_status: str = "allowed") -> Target:
        async with self.session_factory() as session:
            async with session.begin():
                result = await session.execute(select(Target).where(Target.url == url))
                target = result.scalar_one_or_none()
                if not target:
                    target = Target(url=url, host=host, scope_status=scope_status)
                    session.add(target)
                    await session.commit()
                    await session.refresh(target)
                return target

    async def create_scan(self, target_id: int, module_name: str) -> Scan:
        async with self.session_factory() as session:
            async with session.begin():
                scan = Scan(target_id=target_id, module_name=module_name, status=ScanStatus.RUNNING)
                session.add(scan)
                await session.commit()
                await session.refresh(scan)
                return scan

    async def finish_scan(self, scan_id: int, status: ScanStatus, error: str = None):
        async with self.session_factory() as session:
            async with session.begin():
                result = await session.execute(select(Scan).where(Scan.id == scan_id))
                scan = result.scalar_one_or_none()
                if scan:
                    scan.status = status
                    scan.error = error
                    await session.commit()

    async def save_findings(self, scan_id: int, findings: list[Finding]):
        async with self.session_factory() as session:
            async with session.begin():
                for f in findings:
                    db_finding = DBFinding(
                        scan_id=scan_id,
                        title=f.title,
                        severity=f.severity,
                        description=f.description,
                        remediation=f.remediation,
                        cwe=f.cwe,
                        evidence=f.evidence
                    )
                    session.add(db_finding)
                await session.commit()
