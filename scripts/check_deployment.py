#!/usr/bin/env python3
"""Classify the health of the public Streamlit endpoint without credentials."""

from __future__ import annotations

import argparse
import http.client
import os
import socket
import ssl
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urljoin, urlsplit


REDIRECTS = {301, 302, 303, 307, 308}
AUTH_MARKERS = ("share.streamlit.io/-/auth/", "/-/login")


@dataclass(frozen=True)
class Result:
    category: str
    detail: str
    ok: bool
    redirects: tuple[str, ...] = ()


def request_status(url: str, timeout: float) -> tuple[int, str | None]:
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError(f"Unsupported deployment URL: {url}")
    connection_type = http.client.HTTPSConnection if parsed.scheme == "https" else http.client.HTTPConnection
    kwargs = {"timeout": timeout}
    if parsed.scheme == "https":
        kwargs["context"] = ssl.create_default_context()
    connection = connection_type(parsed.hostname, parsed.port, **kwargs)
    path = parsed.path or "/"
    if parsed.query:
        path += f"?{parsed.query}"
    try:
        connection.request("HEAD", path, headers={"User-Agent": "PortfolioLens-deployment-check/1.0"})
        response = connection.getresponse()
        response.read()
        return response.status, response.getheader("Location")
    finally:
        connection.close()


def check(url: str, timeout: float, max_redirects: int) -> Result:
    current = url
    redirects: list[str] = []
    try:
        for _ in range(max_redirects + 1):
            status, location = request_status(current, timeout)
            if 200 <= status < 300:
                return Result("successful response", f"HTTP {status} from {current}", True, tuple(redirects))
            if status in REDIRECTS and location:
                destination = urljoin(current, location)
                redirects.append(f"HTTP {status}: {current} → {destination}")
                if any(marker in destination for marker in AUTH_MARKERS):
                    return Result(
                        "authentication redirect",
                        "Streamlit returned its authentication flow; the host is reachable, but public rendering cannot be verified without credentials.",
                        True,
                        tuple(redirects),
                    )
                current = destination
                continue
            if status >= 500:
                return Result("server error", f"HTTP {status} from {current}", False, tuple(redirects))
            return Result("unexpected HTTP response", f"HTTP {status} from {current}", False, tuple(redirects))
        return Result("redirect limit", f"More than {max_redirects} redirects", False, tuple(redirects))
    except socket.gaierror as exc:
        return Result("DNS failure", str(exc), False, tuple(redirects))
    except (TimeoutError, socket.timeout) as exc:
        return Result("timeout", str(exc) or f"No response within {timeout:g} seconds", False, tuple(redirects))
    except (OSError, ssl.SSLError, http.client.HTTPException, ValueError) as exc:
        return Result("connection failure", f"{type(exc).__name__}: {exc}", False, tuple(redirects))


def render_summary(url: str, result: Result) -> str:
    icon = "✅" if result.ok else "❌"
    lines = [
        "## PortfolioLens deployment health",
        "",
        f"- **URL:** `{url}`",
        f"- **Result:** {icon} {result.category}",
        f"- **Diagnostic:** {result.detail}",
    ]
    if result.redirects:
        lines.extend(["", "### Redirect trace", ""] + [f"- {item}" for item in result.redirects])
    lines.extend([
        "",
        "> An authentication redirect proves that Streamlit answered but does not prove that the signed-out application UI rendered. DNS, timeout, and server failures fail this workflow while remaining operational evidence rather than proof of an application-code defect.",
    ])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("--timeout", type=float, default=15)
    parser.add_argument("--max-redirects", type=int, default=8)
    args = parser.parse_args()
    result = check(args.url, args.timeout, args.max_redirects)
    summary = render_summary(args.url, result)
    print(summary)
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with Path(summary_path).open("a", encoding="utf-8") as handle:
            handle.write(summary)
    return 0 if result.ok else 1


if __name__ == "__main__":
    sys.exit(main())
