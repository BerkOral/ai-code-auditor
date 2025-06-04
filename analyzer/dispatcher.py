import os
from analyzer.python_analyzer import analyze_python_file
from analyzer.js_analyzer import analyze_js_file
from analyzer.html_analyzer import analyze_html_file
from analyzer.sql_analyzer import analyze_sql_file
from analyzer.php_analyzer import analyze_php_file

# This is your original logic — unchanged
def run_scan(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".py":
        return analyze_python_file(file_path)
    elif ext == ".js":
        return analyze_js_file(file_path)
    elif ext in [".html", ".htm"]:
        return analyze_html_file(file_path)
    elif ext == ".sql":
        return analyze_sql_file(file_path)
    elif ext == ".php":
        return analyze_php_file(file_path)

    return {"error": "❌ Unsupported file type."}

# This is the expected function used by app.py
def dispatch_analysis(file_path=None, code=None):
    if file_path:
        return run_scan(file_path)
    elif code:
        # Fallback handler for pasted code: assume Python
        from analyzer.python_analyzer import analyze_python_code
        return analyze_python_code(code)
    else:
        return {"error": "⚠️ No file or code provided for analysis."}
