import json
import sys
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from probe_api import Result, request  # noqa: E402


def test_result_to_dict():
    r = Result("GET", "/health", 200, '{"ok":true}')
    d = r.to_dict()
    assert d["method"] == "GET"
    assert d["status"] == 200


@patch("probe_api.urllib.request.urlopen")
def test_request_success(mock_urlopen):
    payload = b'{"status":"ok"}'
    mock_resp = mock_urlopen.return_value.__enter__.return_value
    mock_resp.status = 200
    mock_resp.read.return_value = payload

    result = request("GET", "/health", None)
    assert result.status == 200
    assert "ok" in result.snippet


@patch("probe_api.urllib.request.urlopen")
def test_request_http_error(mock_urlopen):
    from urllib.error import HTTPError

    err = HTTPError("http://x", 401, "Unauthorized", {}, BytesIO(b'{"error":"auth"}'))
    mock_urlopen.side_effect = err

    result = request("GET", "/auth/me", None)
    assert result.status == 401
