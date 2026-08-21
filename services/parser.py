import re


ALLOWED_ERROR_TYPES = {
    "dependency",
    "network",
    "authentication",
    "file",
    "build",
    "test",
    "unknown",
}


def classify_error(log_text: str):
    """
    Lightweight parser fallback.

    The main classification is handled by ai_analyzer.py,
    but this provides a safe fallback if AI analysis fails.
    """

    text = str(log_text).lower()

    # Dependency/package context first.
    if any(pattern in text for pattern in [
        "dependency",
        "npm err",
        "npm install",
        "npm ci",
        "yarn",
        "pnpm",
        "pip install",
        "collecting ",
        "modulenotfounderror",
        "no module named",
        "gem install",
        "bundler",
        "composer",
        "gradle",
        "maven",
        "go mod",
        "apt-get",
        "unable to locate package",
        "unmet dependencies",
        "yum",
        "dnf",
        "mirrorlist",
        "failed to fetch",
        "failed to download",
        "failed to solve",
    ]):
        return "dependency"

    # Test failures.
    if any(pattern in text for pattern in [
        "eaddrinuse",
        "address already in use",
        "test failed",
        "tests failed",
        "assertionerror",
        "assertion failed",
    ]):
        return "test"

    # Authentication.
    if any(pattern in text for pattern in [
        "nocredentialserror",
        "unable to locate credentials",
        "unauthorized",
        "forbidden",
        "permission denied",
        "access denied",
        "invalid api key",
        "invalid token",
        "authentication failed",
        "401",
        "403",
    ]):
        return "authentication"

    # File.
    if any(pattern in text for pattern in [
        "file not found",
        "no such file",
        "enoent",
        "cannot find module",
    ]):
        return "file"

    # Build.
    if any(pattern in text for pattern in [
        "build failed",
        "failed to build",
        "build error",
        "compilation failed",
        "compile error",
        "syntaxerror",
        "out of memory",
        "exit code 137",
        "gradle build daemon",
        "lock file exists",
        "gpg error",
        "clock skew detected",
    ]):
        return "build"

    # Network.
    if any(pattern in text for pattern in [
        "network error",
        "connection refused",
        "connection reset",
        "connection timed out",
        "timeout",
        "timed out",
        "dns",
        "could not resolve host",
        "couldn't resolve host",
        "name resolution",
        "tls handshake",
        "connectionerror",
        "max retries exceeded",
        "econnrefused",
        "econnreset",
    ]):
        return "network"

    return "unknown"


def clean_log_line(line: str):
    line = line.strip()

    # GitHub Actions error prefix.
    if "##[error]" in line:
        line = line.split("##[error]")[-1].strip()

    # Basic ERROR prefix cleanup.
    if "ERROR:" in line:
        line = line.split("ERROR:", 1)[-1].strip()

    return line


def extract_errors(log_text: str):
    """
    Extract relevant error lines from a CI/CD log.
    """

    if not isinstance(log_text, str):
        log_text = str(log_text)

    lines = log_text.splitlines()

    error_lines = []

    keywords = [
        "error",
        "failed",
        "exception",
        "fatal",
        "traceback",
        "npm err",
        "eaddrinuse",
        "assertion",
        "unable to locate package",
        "no such file",
        "out of memory",
        "unauthorized",
        "forbidden",
        "connection refused",
        "timeout",
        "timed out",
    ]

    for line in lines:
        lower_line = line.lower()

        if any(
            keyword in lower_line
            for keyword in keywords
        ):
            clean_line = clean_log_line(line)

            if clean_line:
                error_lines.append(clean_line)

    # If no individual line matched but the entire log is non-empty,
    # preserve the original log so the analyzer still gets context.
    if not error_lines and log_text.strip():
        error_lines.append(log_text.strip())

    severity = (
        "HIGH"
        if any(
            keyword in log_text.lower()
            for keyword in [
                "failed",
                "fatal",
                "exit code 1",
                "exit code 137",
                "exception",
                "error",
            ]
        )
        else "MEDIUM"
    )

    error_type = classify_error(log_text)

    return {
        "errors": error_lines[:10],
        "severity": severity,
        "error_type": error_type,
    }