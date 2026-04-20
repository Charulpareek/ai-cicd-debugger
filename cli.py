import requests

log = input("Paste CI/CD logs:\n")

response = requests.post(
    "http://127.0.0.1:5000/analyze",
    json={"logs": log}
)

print("\n--- Analysis Result ---\n")
print(response.json())