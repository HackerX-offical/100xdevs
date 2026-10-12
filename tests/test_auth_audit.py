import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from auth_audit import Finding  # noqa: E402


def test_finding_dataclass_fields():
    f = Finding("auth-01", "Token scope", "medium", "GET /auth/me returned 200")
    assert f.id == "auth-01"
    assert f.severity == "medium"
    assert "auth/me" in f.evidence
