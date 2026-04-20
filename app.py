from flask import Flask, request, jsonify
from services.parser import extract_errors
from services.ai_analyzer import analyze_with_ai
from utils.response_formatter import format_response
import time
import logging

app = Flask(__name__)

# ✅ Basic logging (important for observability)
logging.basicConfig(level=logging.INFO)


@app.route("/analyze", methods=["POST"])
def analyze():
    start_time = time.time()

    try:
        log_data = None

        # ✅ Handle file upload
        if "file" in request.files:
            file = request.files["file"]
            log_data = file.read().decode("utf-8")

        # ✅ Handle JSON input safely
        elif request.is_json:
            data = request.get_json()
            log_data = data.get("logs")

        else:
            return jsonify({
                "status": "error",
                "message": "Invalid input. Provide file or JSON with 'logs'."
            }), 400

        # ✅ Validate input
        if not log_data or not log_data.strip():
            return jsonify({
                "status": "error",
                "message": "No logs provided"
            }), 400

        logging.info(f"Received logs (first 100 chars): {log_data[:100]}")

        # ✅ Parse logs
        parsed = extract_errors(log_data)
        errors = parsed["errors"]
        severity = parsed["severity"]
        parser_error_type = parsed.get("error_type")

        logging.info(f"Parsed errors: {errors}")

        # ✅ If no errors found
        if not errors:
            latency = round((time.time() - start_time) * 1000, 2)

            return jsonify(format_response(
                [],
                "LOW",
                {
                    "error_type": "none",
                    "root_cause": "No errors detected",
                    "explanation": "Logs do not contain failure patterns",
                    "fix": "Provide valid CI/CD failure logs"
                },
                latency
            ))

        # ✅ AI Analysis
        ai_result = analyze_with_ai(errors)

        # ✅ Fallback to parser classification if AI fails
        if not ai_result.get("error_type") or ai_result["error_type"] == "unknown":
            ai_result["error_type"] = parser_error_type

        latency = round((time.time() - start_time) * 1000, 2)

        logging.info(f"Latency: {latency} ms")

        response = format_response(errors, severity, ai_result, latency)

        return jsonify(response)

    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")

        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500


# ✅ Health check endpoint (very important)
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "service": "AI CI/CD Debugger"
    })


if __name__ == "__main__":
    app.run(debug=True)