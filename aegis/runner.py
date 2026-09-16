import asyncio
from enum import Enum
from dataclasses import dataclass, field
from aegis.db.models import ScanModel, FindingModel

class Status(Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"

@dataclass
class ModuleResult:
    module_name: str
    status: Status
    findings_count: int = 0
    error: str | None = None
    findings_list: list = field(default_factory=list)

@dataclass
class ScanResult:
    target_url: str
    modules: list[ModuleResult] = field(default_factory=list)

class ModuleRunner:
    def __init__(self, db, client):
        self.db = db
        self.client = client

    async def run(self, target: str, modules: list) -> ScanResult:
        scan_result = ScanResult(target_url=target)
        
        # فتح جلسة قاعدة بيانات وحفظ السجل الرئيسي للفحص
        async with self.db.get_session() as session:
            db_scan = ScanModel(target_url=target, status="RUNNING")
            session.add(db_scan)
            await session.commit()
            await session.refresh(db_scan)
            scan_id = db_scan.id

            for mod in modules:
                name = getattr(mod, "name", mod.__class__.__name__)
                try:
                    if hasattr(mod, "run"):
                        findings = await mod.run(target, self.client)
                    else:
                        findings = []

                    findings_count = len(findings) if isinstance(findings, list) else 0
                    
                    # حفظ الاكتشافات في جدول Findings
                    if isinstance(findings, list):
                        for finding_text in findings:
                            db_finding = FindingModel(
                                scan_id=scan_id,
                                module_name=name,
                                description=str(finding_text),
                                severity="MEDIUM"
                            )
                            session.add(db_finding)

                    scan_result.modules.append(
                        ModuleResult(
                            module_name=name,
                            status=Status.SUCCESS,
                            findings_count=findings_count,
                            findings_list=findings if isinstance(findings, list) else []
                        )
                    )
                except Exception as e:
                    scan_result.modules.append(
                        ModuleResult(
                            module_name=name,
                            status=Status.FAILED,
                            findings_count=0,
                            error=str(e)
                        )
                    )
            
            db_scan.status = "SUCCESS"
            await session.commit()

        return scan_result
