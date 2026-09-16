from enum import Enum
from pydantic import BaseModel, Field

class Severity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Finding(BaseModel):
    title: str
    severity: Severity
    description: str = ""
    remediation: str = ""
    cwe: str | None = None
    evidence: dict = Field(default_factory=dict)
    references: list[str] = Field(default_factory=list)
