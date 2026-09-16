from pathlib import Path
import yaml

class Scope:
    def __init__(self, allow=None, deny=None):
        self.allow = allow or []
        self.deny = deny or []

    @classmethod
    def load(cls, path: Path):
        if not path.exists():
            return cls()
        try:
            with open(path, "r") as f:
                data = yaml.safe_load(f) or {}
                return cls(
                    allow=data.get("allow", []),
                    deny=data.get("deny", [])
                )
        except Exception:
            return cls()

    def is_allowed(self, target: str) -> bool:
        # إذا وُجدت قائمة السماح ويطابقها الهدف
        if self.allow:
            matched_allow = any(domain in target for domain in self.allow)
            if not matched_allow:
                return False
        
        # إذا وُجدت قائمة الحظر ويطابقها الهدف
        if self.deny:
            matched_deny = any(domain in target for domain in self.deny)
            if matched_deny:
                return False

        return True
