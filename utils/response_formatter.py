import uuid
from datetime import datetime


def format_response(errors, severity, analysis, latency_ms):
    return {
    "request_id": str(uuid.uuid4()),
    "timestamp": datetime.utcnow().isoformat(),
    "status": "success",
    "latency_ms": latency_ms,
    "data": {
        "errors": errors,
        "severity": severity,
        "analysis": analysis
    }
}