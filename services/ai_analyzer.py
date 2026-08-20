import json

from groq import Groq

from config import Config


client = Groq(api_key=Config.GROQ_API_KEY)


ALLOWED_ERROR_TYPES = [
    "dependency",
    "network",
    "authentication",
    "file",
    "build",
    "test",
    "unknown",
]


def analyze_with_ai(errors):
    prompt = f"""
You are a senior DevOps engineer analyzing CI/CD failure logs.

Classify the failure into exactly ONE of these categories:

- dependency: package/version/dependency resolution conflicts
- network: DNS, connection, timeout, registry/network connectivity failures
- authentication: invalid credentials, unauthorized, forbidden, access denied
- file: missing files, missing artifacts, missing configuration files or paths
- build: compilation, bundling, syntax, loader, or build pipeline failures
- test: unit/integration/e2e test failures or assertion failures
- unknown: use only when the failure cannot reasonably be classified

Analyze these CI/CD logs:

{errors}

Return:
- error_type: exactly one allowed category
- root_cause: concise technical root cause
- explanation: concise explanation for a developer
- fix: practical remediation steps
"""


    response = client.chat.completions.create(
        model=Config.MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "cicd_error_analysis",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "error_type": {
                            "type": "string",
                            "enum": ALLOWED_ERROR_TYPES,
                        },
                        "root_cause": {
                            "type": "string",
                        },
                        "explanation": {
                            "type": "string",
                        },
                        "fix": {
                            "type": "string",
                        },
                    },
                    "required": [
                        "error_type",
                        "root_cause",
                        "explanation",
                        "fix",
                    ],
                    "additionalProperties": False,
                },
            },
        },
        include_reasoning=False,
        max_completion_tokens=1000,
    )

    content = response.choices[0].message.content

    result = json.loads(content)

    explanation = result.get("explanation", "")

    if len(explanation) > 500:
        explanation = explanation[:500] + "..."

    error_type = result.get("error_type", "unknown")

    if error_type not in ALLOWED_ERROR_TYPES:
        error_type = "unknown"

    return {
        "error_type": error_type,
        "root_cause": result.get("root_cause", ""),
        "explanation": explanation,
        "fix": result.get("fix", ""),
    }