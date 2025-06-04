import subprocess
from rich.console import Console
from utils.gpt_explainer import explain_issue
from utils.risk_scorer import calculate_risk_score

console = Console()

def analyze_php_file(file_path):
    console.print(f"🔍 Scanning [bold cyan]{file_path}[/] with [yellow]PHPStan[/]...", style="bold yellow")

    # ✅ Step 1: Syntax check
    syntax_check = subprocess.run(
        ["php", "-l", file_path],
        capture_output=True,
        text=True
    )

    if syntax_check.returncode != 0:
        console.print(f"❌ [red]PHP syntax error:[/]\n{syntax_check.stdout}", style="bold red")
        return {
            "tool": "PHP",
            "status": "syntax error",
            "raw_output": syntax_check.stdout.strip(),
            "ai_suggestion": "This PHP file has a syntax error and cannot be analyzed by PHPStan. Please fix it first.",
            "risk_score": 10
        }

    # ✅ Step 2: Static analysis via PHPStan
    result = subprocess.run(
        ["C:\\Users\\Berk\\AppData\\Roaming\\Composer\\vendor\\bin\\phpstan.bat", "analyze", file_path, "--error-format", "raw"],
        capture_output=True,
        text=True
    )

    output = result.stdout or ""
    error_output = result.stderr or ""

    if error_output.strip():
        console.print(f"❌ PHPStan error:\n{error_output}", style="bold red")
        return {
            "tool": "PHPStan",
            "status": "error",
            "raw_output": error_output.strip(),
            "ai_suggestion": "PHPStan encountered an error during analysis.",
            "risk_score": 10
        }

    if " [ERROR] " not in output:
        console.print("✅ [green]No issues found by PHPStan.[/]")
        return {
            "tool": "PHPStan",
            "status": "clean",
            "raw_output": "No issues found.",
            "ai_suggestion": "No security issues detected in this PHP file.",
            "risk_score": 0
        }

    console.print(f"❌ PHPStan found issues:\n{output}", style="bold red")
    explanation = explain_issue(output, "PHP security issues")
    score = calculate_risk_score(output, "PHPStan")

    console.print(f"🧠 [bold green]AI Suggestion:[/]\n{explanation}")

    return {
        "tool": "PHPStan",
        "status": "issues",
        "raw_output": output,
        "ai_suggestion": explanation,
        "risk_score": score
    }
