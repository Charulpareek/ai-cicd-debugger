import json
from groq import Groq
from config import Config

client = Groq(api_key=Config.GROQ_API_KEY)


def analyze_with_ai(errors):
    prompt = f"""
You are a senior DevOps engineer.

Analyze the following CI/CD errors:
{errors}

Respond ONLY in valid JSON format:

{{
  "error_type": "",
  "root_cause": "",
  "explanation": "",
  "fix": ""
}}
"""

    response = client.chat.completions.create(
        model=Config.MODEL_NAME,
        messages=[{"role": "user", "content": prompt}]
    )

    content = response.choices[0].message.content.strip()

    try:
        # ✅ Clean markdown formatting if AI returns ```json
        content = content.replace("```json", "").replace("```", "").strip()

        result = json.loads(content)

        # ✅ Normalize error_type
        raw_error_type = result.get("error_type", "").lower()

        if "dependency" in raw_error_type:
            error_type = "dependency"
        elif "network" in raw_error_type:
            error_type = "network"
        elif "permission" in raw_error_type or "auth" in raw_error_type:
            error_type = "auth"
        elif "file" in raw_error_type or "not found" in raw_error_type:
            error_type = "file"
        else:
            error_type = "unknown"

        # ✅ Optional: trim long explanations
        explanation = result.get("explanation", "")
        if len(explanation) > 300:
            explanation = explanation[:300] + "..."

        return {
            "error_type": error_type,
            "root_cause": result.get("root_cause", ""),
            "explanation": explanation,
            "fix": result.get("fix") or result.get("Fix", ""),
            "confidence": "high"   # 🔥 added (product-style output)
        }

    except Exception:
        return {
            "error_type": "unknown",
            "root_cause": "AI parsing failed",
            "explanation": content,
            "fix": "Review logs manually",
            "confidence": "low"
        }