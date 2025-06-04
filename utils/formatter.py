def format_issue(issue):
    return f"- [!] {issue['test_id']} - {issue['issue_text']} (Severity: {issue['issue_severity']})"
