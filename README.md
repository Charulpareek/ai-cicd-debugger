# 🚀 AI CI/CD Debugger

An AI-powered system that analyzes CI/CD pipeline logs and automatically identifies root causes, provides explanations, and suggests fixes.

---

## 📌 Problem

Debugging CI/CD pipeline failures is time-consuming and requires manual log inspection. Engineers often struggle to quickly identify the root cause of failures.

---

## 💡 Solution

This project uses Large Language Models (LLMs) to:

- Parse CI/CD logs  
- Identify failure patterns  
- Classify error types (dependency, network, auth, file)  
- Generate root cause analysis  
- Suggest actionable fixes  

---

## 🏗️ Architecture

```
Input Logs → Parser → AI Analyzer → Response Formatter → API Output
```

---

## ⚙️ Features

- 🔍 Automated log parsing  
- 🤖 AI-powered root cause analysis  
- 🧠 Error classification system  
- 📊 Structured JSON API response  
- 📡 REST API using Flask  
- ⚡ Latency tracking  
- ❤️ Health check endpoint  

---

## 🚀 Getting Started

### 📋 Prerequisites

- Python 3.9+  
- pip  
- Groq API key  

---

### 1️⃣ Clone the repository

```bash
git clone https://github.com/Charulpareek/ai-cicd-debugger.git
cd ai-cicd-debugger
```

---

### 2️⃣ Create virtual environment

```bash
python -m venv venv
```

---

### 3️⃣ Activate virtual environment

Windows:

```bash
venv\Scripts\activate
```

Mac/Linux:

```bash
source venv/bin/activate
```

---

### 4️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

---

### 5️⃣ Configure environment variables

Create a `.env` file:

```
GROQ_API_KEY=your_api_key
MODEL_NAME=llama3-8b-8192
```

---

### 6️⃣ Run the server

```bash
python app.py
```

Server runs at:

```
http://127.0.0.1:5000
```

---

## 🧪 Testing the API

### 🔹 File upload

```bash
curl -X POST http://127.0.0.1:5000/analyze -F "file=@data/sample_logs.txt"
```

---

### 🔹 JSON input

```bash
curl -X POST http://127.0.0.1:5000/analyze -H "Content-Type: application/json" -d '{"logs": "npm ERR! code ERESOLVE\nBuild failed: exit code 1"}'
```

---

## 📊 API Response Format

```json
{
  "request_id": "...",
  "status": "success",
  "latency_ms": 500,
  "data": {
    "errors": [],
    "severity": "HIGH",
    "analysis": {
      "error_type": "",
      "root_cause": "",
      "explanation": "",
      "fix": ""
    }
  }
}
```

---

## 🧪 Example

### Input

```
ERROR: Could not open requirements file: [Errno 2] No such file or directory: 'requirements.txt'
Process completed with exit code 1
```

---

### Output

```json
{
  "error_type": "file",
  "root_cause": "requirements.txt file not found",
  "explanation": "CI/CD pipeline failed due to missing dependency file.",
  "fix": "Ensure requirements.txt exists or update file path.",
  "confidence": "high"
}
```

---

## 🧠 Tech Stack

- Python  
- Flask  
- Groq API (LLM)  
- REST APIs  
- GitHub Actions  

---

## 📈 Future Improvements

- Real-time log streaming  
- GitHub Actions API integration  
- Web dashboard  
- Error analytics  

---

## 👨‍💻 Author

**Charul Pareek**
