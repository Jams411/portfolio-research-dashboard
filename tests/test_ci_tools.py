"""Deterministic tests for repository verification helpers."""

import socket

from scripts import check_deployment


def test_deployment_check_follows_redirect_to_success(monkeypatch):
    responses = iter([(303, "/ready"), (200, None)])
    monkeypatch.setattr(check_deployment, "request_status", lambda url, timeout: next(responses))
    result = check_deployment.check("https://example.test", 5, 3)
    assert result.ok
    assert result.category == "successful response"
    assert len(result.redirects) == 1


def test_deployment_check_recognizes_streamlit_authentication(monkeypatch):
    monkeypatch.setattr(
        check_deployment,
        "request_status",
        lambda url, timeout: (303, "https://share.streamlit.io/-/auth/app?redirect_uri=x"),
    )
    result = check_deployment.check("https://example.test", 5, 3)
    assert result.ok
    assert result.category == "authentication redirect"


def test_deployment_check_distinguishes_dns_and_server_failures(monkeypatch):
    def dns_failure(url, timeout):
        raise socket.gaierror("unresolvable")

    monkeypatch.setattr(check_deployment, "request_status", dns_failure)
    assert check_deployment.check("https://example.test", 5, 3).category == "DNS failure"

    monkeypatch.setattr(check_deployment, "request_status", lambda url, timeout: (503, None))
    result = check_deployment.check("https://example.test", 5, 3)
    assert not result.ok
    assert result.category == "server error"
