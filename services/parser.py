def classify_error(log_text: str):
    log_text = log_text.lower()

    if "npm err" in log_text or "dependency" in log_text:
        return "dependency"
    elif "timeout" in log_text or "network" in log_text:
        return "network"
    elif "permission" in log_text or "unauthorized" in log_text:
        return "auth"
    elif "no such file" in log_text or "not found" in log_text:
        return "file"
    return "unknown"


def clean_log_line(line: str):
    line = line.strip()

    # Remove GitHub Actions error prefix
    if "##[error]" in line:
        line = line.split("##[error]")[-1].strip()

    # Remove timestamps (basic cleanup)
    if "ERROR:" in line:
        line = line.split("ERROR:")[-1].strip()

    return line


def extract_errors(log_text: str):
    lines = log_text.split("\n")
    error_lines = []

    keywords = ["error", "failed", "exception", "npm err"]

    for line in lines:
        if any(k in line.lower() for k in keywords):
            clean_line = clean_log_line(line)

            # Avoid empty lines after cleaning
            if clean_line:
                error_lines.append(clean_line)

    # ✅ Improved severity detection
    severity = "HIGH" if any(
        k in log_text.lower()
        for k in ["failed", "exit code 1", "error"]
    ) else "MEDIUM"

    error_type = classify_error(log_text)

    return {
        "errors": error_lines[:10],
        "severity": severity,
        "error_type": error_type
    }