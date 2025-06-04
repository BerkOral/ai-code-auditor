import subprocess
import json
from rich.console import Console
from utils.gpt_explainer import explain_issue
from utils.risk_scorer import calculate_risk_score

console = Console()

def analyze_python_file(file_path):
    console.print(f"🔍 Scanning [bold cyan]{file_path}[/] with [yellow]Bandit[/]...", style="bold yellow")
    result = subprocess.run(["bandit", "-r", file_path, "-f", "json"], capture_output=True, text=True)
    output = result.stdout

    try:
        data = json.loads(output)
        issues = data.get("results", [])
    except json.JSONDecodeError:
        console.print("[red]❌ Failed to parse Bandit output[/]")
        console.print(output)
        return {
            "tool": "Bandit",
            "status": "error",
            "error": "Failed to parse Bandit output"
        }

    if not issues:
        console.print("✅ [green]No issues found[/]")
        return {
            "tool": "Bandit",
            "status": "clean",
            "raw_output": "No issues found.",
            "ai_suggestion": "No security issues detected in this Python file.",
            "risk_score": 0
        }

    combined_output = ""
    suggestions = []
    for issue in issues:
        text = f"⚠️ {issue['issue_text']} (Severity: {issue['issue_severity']} at line {issue['line_number']})"
        console.print(f"[red]{text}[/]")
        explanation = explain_issue(issue['code'], issue['issue_text'])
        suggestions.append(explanation)
        combined_output += text + "\n"

    full_suggestion = "\n\n".join(suggestions)
    score = calculate_risk_score(issues, "Bandit")
    console.print(f"🧠 [bold green]AI Suggestion:[/]\n{full_suggestion}")

    return {
        "tool": "Bandit",
        "status": "issues",
        "raw_output": combined_output,
        "ai_suggestion": full_suggestion,
        "risk_score": score
    }
