"""Log preprocessing to reduce token usage and improve analysis quality."""

from __future__ import annotations

import re

# Common log patterns to filter noise
NOISE_PATTERNS = [
    r"^\s*$",  # Empty lines
    r"^#.*$",  # Comments
    r"DEBUG.*",  # Debug messages (can be filtered)
]

# Important patterns to preserve
CRITICAL_PATTERNS = [
    r"(?i)(fatal|critical|error|exception|failed|failure|crash|timeout)",
    r"(?i)(panic|abort|segfault|oom|out of memory)",
    r"(?i)(connection.*refused|connection.*timeout|connection.*failed)",
    r"(?i)(database.*error|sql.*error|query.*failed)",
    r"(?i)(authentication.*failed|authorization.*denied|permission.*denied)",
]


def preprocess_logs(
    log_text: str,
    filter_debug: bool = True,
    filter_info: bool = False,
    min_severity: str = "WARN",
) -> str:
    """Preprocess logs to reduce noise and reduce token usage.

    Args:
        log_text: Raw log text.
        filter_debug: Filter DEBUG level messages.
        filter_info: Filter INFO level messages.
        min_severity: Minimum severity level to include (DEBUG, INFO, WARN, ERROR, FATAL).

    Returns:
        Preprocessed log text with noise removed.
    """
    lines = log_text.split("\n")
    filtered_lines: list[str] = []

    severity_order = {"DEBUG": 0, "INFO": 1, "WARN": 2, "ERROR": 3, "FATAL": 4}
    min_level = severity_order.get(min_severity.upper(), 1)

    for line in lines:
        # Skip empty lines
        if not line.strip():
            continue

        # Skip comment lines
        if line.strip().startswith("#"):
            continue

        # Filter by severity if specified
        if filter_debug and re.search(r"(?i)\bDEBUG\b", line):
            continue

        if filter_info and re.search(r"(?i)\bINFO\b", line) and not any(
            pattern in line.upper() for pattern in ["ERROR", "WARN", "FATAL", "EXCEPTION"]
        ):
            continue

        # Always include critical patterns
        if any(re.search(pattern, line, re.IGNORECASE) for pattern in CRITICAL_PATTERNS):
            filtered_lines.append(line)
            continue

        # Check severity level
        line_upper = line.upper()
        if "FATAL" in line_upper or "CRITICAL" in line_upper:
            if severity_order.get("FATAL", 4) >= min_level:
                filtered_lines.append(line)
        elif "ERROR" in line_upper or "EXCEPTION" in line_upper:
            if severity_order.get("ERROR", 3) >= min_level:
                filtered_lines.append(line)
        elif "WARN" in line_upper or "WARNING" in line_upper:
            if severity_order.get("WARN", 2) >= min_level:
                filtered_lines.append(line)
        elif "INFO" in line_upper:
            if not filter_info and severity_order.get("INFO", 1) >= min_level:
                filtered_lines.append(line)
        elif "DEBUG" in line_upper:
            if not filter_debug and severity_order.get("DEBUG", 0) >= min_level:
                filtered_lines.append(line)
        else:
            # Include lines that don't have explicit severity markers
            # (might be application-specific formats)
            filtered_lines.append(line)

    # If filtering removed too much, include more context
    if len(filtered_lines) < len(lines) * 0.1:  # Less than 10% remains
        # Include more context around errors
        return log_text

    return "\n".join(filtered_lines)


def detect_log_format(log_text: str) -> str:
    """Detect log format to provide context to the AI.

    Args:
        log_text: Log text to analyze.

    Returns:
        Detected log format (e.g., "standard", "json", "apache", "nginx").
    """
    lines = log_text.split("\n")[:50]  # Sample first 50 lines

    # Check for JSON logs
    json_count = sum(1 for line in lines if line.strip().startswith("{") and "}" in line)
    if json_count > len(lines) * 0.5:
        return "json"

    # Check for Apache/Nginx access logs
    if any(re.search(r'^\d+\.\d+\.\d+\.\d+.*\[.*\].*"', line) for line in lines):
        return "apache_nginx"

    # Check for syslog format
    if any(re.search(r'^\w{3}\s+\d+\s+\d{2}:\d{2}:\d{2}', line) for line in lines):
        return "syslog"

    # Check for structured logging (key=value pairs)
    if any(re.search(r'\w+=\w+', line) for line in lines[:10]):
        return "structured"

    return "standard"


def estimate_log_complexity(log_text: str) -> str:
    """Estimate log complexity to select appropriate prompt.

    Args:
        log_text: Log text to analyze.

    Returns:
        Complexity level: "simple", "moderate", or "complex".
    """
    lines = log_text.split("\n")
    error_count = sum(
        1
        for line in lines
        if any(pattern in line.upper() for pattern in ["ERROR", "FATAL", "EXCEPTION", "FAILED"])
    )
    unique_errors = len(set(line.strip() for line in lines if "ERROR" in line.upper()))

    if error_count == 0:
        return "simple"
    elif error_count < 10 and unique_errors < 5:
        return "moderate"
    else:
        return "complex"
