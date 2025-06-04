import json

def calculate_risk_score(issues, tool_name):
    """
    Returns a risk score (0–10) based on issues.
    Each tool can have different weighting logic.
    """
    if not issues:
        return 0

    score = 0

    if tool_name == "Bandit":
        for issue in issues:
            severity = issue.get("issue_severity", "").lower()
            if severity == "high":
                score += 4
            elif severity == "medium":
                score += 2
            elif severity == "low":
                score += 1

    elif tool_name == "ESLint":
        try:
            parsed = json.loads(issues)
            if isinstance(parsed, list) and len(parsed) > 0:
                messages = parsed[0].get("messages", [])
                for msg in messages:
                    severity = msg.get("severity", 0)
                    if severity == 2:
                        score += 2
                    elif severity == 1:
                        score += 1
        except Exception:
            # fallback to string analysis if parsing fails
            for line in issues.split("\n"):
                if "error" in line.lower():
                    score += 2
                elif "warning" in line.lower():
                    score += 1

    elif tool_name == "SQL Checker":
        score += 2 * len(issues)

    elif tool_name == "HTMLHint":
        score += issues.lower().count("error") * 2
        score += issues.lower().count("warning")

    elif tool_name == "PHPStan":
        score += issues.lower().count("error") * 2
        score += issues.lower().count("warning")

    return min(10, score)
