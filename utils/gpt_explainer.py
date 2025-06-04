import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_prompt_by_severity(severity_level):
    if severity_level in ['CRITICAL', 'HIGH', 'MEDIUM']:
        return """You are SENTINEL-X, an elite AI Security Auditor.
Provide:
- Corrected version of the code in a clean block (NO comments inside).
- A simple, line-by-line explanation UNDER the code block.
- A clear summary of WHY this fix matters in plain English.
Keep it professional yet accessible. Avoid technical jargon. Target audience is smart but not technical."""

    elif severity_level == 'LOW':
        return """You're an AI assistant helping improve basic security flaws.
Give the corrected code in a clean block and explain it simply underneath. Emphasize clarity and helpfulness."""

    else:
        return """You're an AI code assistant for style and best practices.
Suggest clean code fixes in a code block. Explain changes simply afterward, like you're teaching a beginner."""

def classify_severity(issue_summary):
    prompt = f"""Classify this code issue severity in ONE WORD (CRITICAL, HIGH, MEDIUM, LOW, INFO):\n\nIssue: {issue_summary}"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10,
            temperature=0
        )
        return response.choices[0].message.content.strip().upper()
    except:
        return "MEDIUM"

def explain_issue(code_snippet: str, issue_summary: str) -> str:
    severity = classify_severity(issue_summary)
    system_prompt = get_prompt_by_severity(severity)

    user_prompt = f"""
CODE:
```
{code_snippet}
```

ISSUE:
{issue_summary}

SEVERITY: {severity}

DELIVER:
1. 🛠️ How to Fix It (corrected code block only)
2. 📖 Explanation (line-by-line, underneath the code block)
3. 🔐 Why It Matters (real-world consequences in plain terms)
"""

    model = "gpt-4" if severity in ['CRITICAL', 'HIGH', 'MEDIUM'] else "gpt-3.5-turbo"
    max_tokens = 900 if severity in ['CRITICAL', 'HIGH'] else 600

    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.2
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"🚨 Analysis failed: {e}"
