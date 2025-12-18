from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List


class ChangeType(str, Enum):
    REMOVED_FIELD = "removed_field"
    ADDED_FIELD = "added_field"
    TYPE_CHANGE = "type_change"
    REQUIRED_CHANGE = "required_change"


class ChangeSeverity(str, Enum):
    BREAKING = "breaking"
    NON_BREAKING = "non_breaking"


@dataclass(frozen=True)
class Change:
    """
    Represents a single detected change between two schemas.
    """

    change_type: ChangeType
    severity: ChangeSeverity
    path: str

    old_type: Optional[str] = None
    new_type: Optional[str] = None
    message: Optional[str] = None


@dataclass
class DiffResult:
    """
    Full diff result between two schemas.
    """

    breaking: List[Change] = field(default_factory=list)
    non_breaking: List[Change] = field(default_factory=list)

    def has_breaking_changes(self) -> bool:
        return bool(self.breaking)

    def exit_code(self) -> int:
        """
        Exit code for CLI / CI usage.
        """
        return 1 if self.has_breaking_changes() else 0

    def to_dict(self) -> dict:
        """
        Machine-readable representation (JSON output).
        """
        return {
            "breaking": [self._change_to_dict(c) for c in self.breaking],
            "non_breaking": [self._change_to_dict(c) for c in self.non_breaking],
        }

    @staticmethod
    def _change_to_dict(change: Change) -> dict:
        return {
            "type": change.change_type.value,
            "severity": change.severity.value,
            "path": change.path,
            "old_type": change.old_type,
            "new_type": change.new_type,
            "message": change.message,
        }
