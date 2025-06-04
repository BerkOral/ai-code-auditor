import subprocess
import os
import json
from rich.console import Console
from utils.gpt_explainer import explain_issue
from utils.risk_scorer import calculate_risk_score

console = Console()

def analyze_js_file(file_path):
    console.print(f"🔍 Scanning [bold cyan]{file_path}[/] with [yellow]ESLint[/]...", style="bold yellow")

    eslint_cmd = "eslint.cmd" if os.name == "nt" else "eslint"

    try:
        result = subprocess.run(
            [eslint_cmd, file_path, "--format", "json"],
            capture_output=True,
            text=True,
            check=False
        )
    except FileNotFoundError:
        console.print("❌ [red]ESLint is not installed or not in PATH.[/]")
        return {
            "tool": "ESLint",
            "status": "error",
            "raw_output": "ESLint is not installed or not found in system PATH.",
            "ai_suggestion": "Please install ESLint globally using `npm install -g eslint` or ensure it's accessible in your PATH.",
            "risk_score": 0
        }

    if not result.stdout.strip():
        console.print("⚠️ [yellow]No output from ESLint. Possibly misconfigured or empty file.[/]")
        return {
            "tool": "ESLint",
            "status": "error",
            "raw_output": "No output from ESLint.",
            "ai_suggestion": "Check if your file is empty or if ESLint is misconfigured.",
            "risk_score": 0
        }

    try:
        parsed_output = json.loads(result.stdout)
    except json.JSONDecodeError:
        console.print("❌ [red]Could not parse ESLint output. Try running ESLint manually to debug.[/]")
        return {
            "tool": "ESLint",
            "status": "error",
            "raw_output": result.stdout,
            "ai_suggestion": "ESLint output could not be parsed. Try running ESLint manually to see the issue.",
            "risk_score": 0
        }

    messages = parsed_output[0].get("messages", [])
    if not messages:
        console.print("✅ [green]No issues found by ESLint.[/]")
        return {
            "tool": "ESLint",
            "status": "clean",
            "raw_output": "No issues found.",
            "ai_suggestion": "No security issues detected in this JavaScript file.",
            "risk_score": 0
        }

    raw_output = json.dumps(messages, indent=2)
    console.print(f"❌ ESLint found issues:\n{raw_output}", style="bold red")

    explanation = explain_issue(raw_output, "JavaScript security or best-practice issues")
    score = calculate_risk_score(raw_output, "ESLint")

    console.print(f"🧠 [bold green]AI Suggestion:[/]\n{explanation}")

    return {
        "tool": "ESLint",
        "status": "issues",
        "raw_output": raw_output,
        "ai_suggestion": explanation,
        "risk_score": score
    }
