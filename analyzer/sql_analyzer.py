from rich.console import Console
from utils.gpt_explainer import explain_issue
from utils.risk_scorer import calculate_risk_score

console = Console()

def analyze_sql_file(file_path):
    console.print(f"🔍 Scanning [bold cyan]{file_path}[/] for [yellow]SQL risks[/]...", style="bold yellow")

    dangerous_patterns = {
        "SELECT *": "Avoid using SELECT * as it can expose more data than necessary.",
        "DROP TABLE": "Potentially dangerous command to remove entire tables.",
        " OR 1=1": "Common SQL injection pattern allowing bypass of authentication."
    }

    issues = []
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for idx, line in enumerate(lines, start=1):
            for pattern, message in dangerous_patterns.items():
                if pattern.lower() in line.lower():
                    issues.append(f"⚠️ Line {idx} - {pattern}: {line.strip()}")

    if not issues:
        console.print("✅ [green]No dangerous SQL patterns found.[/]")
        return {
            "tool": "SQL Checker",
            "status": "clean",
            "raw_output": "No dangerous SQL patterns found.",
            "ai_suggestion": "No SQL injection risks or dangerous commands detected.",
            "risk_score": 0
        }

    raw_output = "\n".join(issues)
    explanation = explain_issue(raw_output, "SQL vulnerabilities")
    score = calculate_risk_score(issues, "SQL Checker")

    console.print(f"🧠 [bold green]AI Suggestion:[/]\n{explanation}")

    return {
        "tool": "SQL Checker",
        "status": "issues",
        "raw_output": raw_output,
        "ai_suggestion": explanation,
        "risk_score": score
    }
