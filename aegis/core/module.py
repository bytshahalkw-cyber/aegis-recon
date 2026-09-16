from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING
from aegis.core.finding import Finding

if TYPE_CHECKING:
    from aegis.core.http import HttpClient

@dataclass
class ModuleContext:
    target: str
    http: "HttpClient"

class Module(ABC):
    name: str
    description: str = ""

    @abstractmethod
    async def run(self, ctx: ModuleContext) -> list[Finding]: ...
