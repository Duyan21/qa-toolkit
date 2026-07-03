import io
import responses as resp
from tools.api_checker.api_checker import check_api

BASE_URL = "http://test-api/endpoint"


@resp.activate
def test_2xx_healthy():
    resp.add(resp.GET, BASE_URL, json={"id": 1, "name": "Noah", "role": "admin"}, status=200)
    result = check_api(BASE_URL)
    assert result["status_code"] == 200
    assert result["status_icon"] == "✅"
    assert result["hint"] is None
    assert result["fields"] == 3


@resp.activate
def test_4xx_returns_error_icon_and_runbook():
    resp.add(resp.GET, BASE_URL, json={"error": "not found"}, status=404)
    result = check_api(BASE_URL)
    assert result["status_code"] == 404
    assert result["status_icon"] == "❌"
    assert result["hint"] == "-> Runbook: runbooks/debug-4xx.md"


@resp.activate
def test_5xx_returns_error_icon_and_runbook():
    resp.add(resp.GET, BASE_URL, json={"error": "internal server error"}, status=500)
    result = check_api(BASE_URL)
    assert result["status_code"] == 500
    assert result["status_icon"] == "❌"
    assert result["hint"] == "-> Runbook: runbooks/debug-5xx.md"


@resp.activate
def test_slow_response_returns_warning(monkeypatch):
    resp.add(resp.GET, BASE_URL, json={"id": 1}, status=200)
    # Force elapsed time above threshold by setting threshold_ms to 0
    result = check_api(BASE_URL, threshold_ms=0)
    assert result["status_icon"] == "⚠️"
    assert result["hint"] == "-> Runbook: runbooks/debug-slow-api.md"


@resp.activate
def test_non_json_response_fields_is_na():
    resp.add(resp.GET, BASE_URL, body="plain text response", status=200)
    result = check_api(BASE_URL)
    assert result["fields"] == "N/A"


@resp.activate
def test_json_array_response_fields_is_na():
    # Top-level array has no .keys() — should not crash
    resp.add(resp.GET, BASE_URL, json=[{"id": 1}, {"id": 2}], status=200)
    result = check_api(BASE_URL)
    assert result["fields"] == "N/A"


@resp.activate
def test_writes_to_log_file():
    resp.add(resp.GET, BASE_URL, json={"id": 1}, status=200)
    log = io.StringIO()
    check_api(BASE_URL, log_file=log)
    log_content = log.getvalue()
    assert BASE_URL in log_content
    assert "200" in log_content


@resp.activate
def test_no_log_file_does_not_crash():
    resp.add(resp.GET, BASE_URL, json={"id": 1}, status=200)
    result = check_api(BASE_URL)
    assert result["status_code"] == 200


@resp.activate
def test_result_contains_url():
    resp.add(resp.GET, BASE_URL, json={"id": 1}, status=200)
    result = check_api(BASE_URL)
    assert result["url"] == BASE_URL


@resp.activate
def test_5xx_takes_priority_over_slow_response():
    # Even if response is slow, 5xx icon should take priority over ⚠️
    resp.add(resp.GET, BASE_URL, json={"error": "crash"}, status=503)
    result = check_api(BASE_URL, threshold_ms=0)
    assert result["status_icon"] == "❌"
    assert result["hint"] == "-> Runbook: runbooks/debug-5xx.md"
