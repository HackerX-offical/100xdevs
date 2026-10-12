from pathlib import Path


def test_findings_doc_exists():
    root = Path(__file__).resolve().parents[1]
    assert (root / "FINDINGS.md").is_file()
    assert (root / "scripts").is_dir()
