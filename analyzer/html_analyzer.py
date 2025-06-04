from rich.console import Console
from utils.gpt_explainer import explain_issue
from utils.risk_scorer import calculate_risk_score

console = Console()

def analyze_html_file(file_path):
    console.print(f"🔍 Scanning [bold cyan]{file_path}[/] for [yellow]HTML security issues[/]...", style="bold yellow")

    issues = []
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for i, line in enumerate(lines, 1):
            if "<script>" in line.lower():
                issues.append(f"⚠️ Line {i}: Inline script tag found - {line.strip()}")
            if "onerror=" in line.lower() or "onclick=" in line.lower():
                issues.append(f"⚠️ Line {i}: Event handler detected - {line.strip()}")

    if not issues:
        console.print("✅ [green]No obvious HTML security risks found.[/]")
        return {
            "tool": "HTML Checker",
            "status": "clean",
            "raw_output": "No dangerous tags or handlers found.",
            "ai_suggestion": "No XSS-related vulnerabilities detected in this HTML file.",
            "risk_score": 0
        }

    raw_output = "\n".join(issues)
    explanation = explain_issue(raw_output, "HTML/XSS vulnerability")
    score = calculate_risk_score(issues, "HTML Checker")

    console.print(f"🧠 [bold green]AI Suggestion:[/]\n{explanation}")

    return {
        "tool": "HTML Checker",
        "status": "issues",
        "raw_output": raw_output,
        "ai_suggestion": explanation,
        "risk_score": score
    }
