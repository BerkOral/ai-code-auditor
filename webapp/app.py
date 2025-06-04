import os
import sys
import uuid
import json
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
migrate = Migrate(app, db)
from flask_login import (
    LoginManager, login_user, logout_user, login_required,
    UserMixin, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.risk_scorer import calculate_risk_score
from analyzer.dispatcher import dispatch_analysis

UPLOAD_DIR = os.path.expanduser("~/secodian/uploads")
RESULTS_BASE = os.path.expanduser("~/secodian/scan_results")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULTS_BASE, exist_ok=True)

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev_key")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "/"

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

with app.app_context():
    db.drop_all()
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", login_page=False, register_page=False)

@app.route("/scan", methods=["POST"])
@login_required
def scan():
    uploaded_file = request.files.get("file")
    code = request.form.get("code")
    filename = None
    results = None

    if uploaded_file and uploaded_file.filename:
        filename = f"{uuid.uuid4()}_{uploaded_file.filename}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        uploaded_file.save(filepath)
        results = dispatch_analysis(file_path=filepath)
    elif code:
        filename = "pasted_code"
        results = dispatch_analysis(code=code)
    else:
        return render_template("index.html", user=current_user, error="\u26a0\ufe0f Please upload a file or paste code.")

    if "risk_score" not in results:
        results["risk_score"] = calculate_risk_score(results["raw_output"], results.get("tool", "Unknown"))

    user_folder = os.path.join(RESULTS_BASE, current_user.username)
    os.makedirs(user_folder, exist_ok=True)

    scan_data = {
        "timestamp": datetime.now().isoformat(),
        "filename": filename,
        "tool": results.get("tool"),
        "risk_score": results.get("risk_score"),
        "status": results.get("status"),
        "raw_output": results.get("raw_output"),
        "ai_suggestion": results.get("ai_suggestion")
    }

    scan_filename = f"{uuid.uuid4().hex}_{filename}.json"
    with open(os.path.join(user_folder, scan_filename), "w") as f:
        json.dump(scan_data, f)

    return render_template(
        "index.html",
        user=current_user,
        results=results,
        filename=filename,
        login_page=False,
        register_page=False,
        error=None
    )

@app.route("/history")
@login_required
def history():
    scan_folder = os.path.join(RESULTS_BASE, current_user.username)
    scans = []

    if os.path.exists(scan_folder):
        for filename in os.listdir(scan_folder):
            scan_path = os.path.join(scan_folder, filename)
            with open(scan_path, "r") as f:
                data = json.load(f)
                timestamp = datetime.fromisoformat(data["timestamp"])
                scans.append({
                    "timestamp": timestamp,
                    "filename": data["filename"],
                    "tool": data["tool"],
                    "risk_score": data["risk_score"],
                    "status": data["status"],
                    "scan_file": filename
                })

    scans.sort(key=lambda x: x["timestamp"], reverse=True)
    return render_template("history.html", scans=scans)

@app.route("/history/<filename>")
@login_required
def view_scan(filename):
    user_folder = os.path.join(RESULTS_BASE, current_user.username)
    file_path = os.path.join(user_folder, filename)

    if not os.path.exists(file_path):
        return "Scan result not found", 404

    with open(file_path, "r") as f:
        data = json.load(f)

    if isinstance(data.get("timestamp"), str):
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])

    return render_template("scan_detail.html", scan=data)

@app.route("/login", methods=["GET"])
def login_page():
    return render_template("index.html", login_page=True, register_page=False, user=None)

@app.route("/register", methods=["GET"])
def register_page():
    return render_template("index.html", register_page=True, login_page=False, user=None)

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    remember = request.form.get("remember") == "on"

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        login_user(user, remember=remember)
        return redirect(url_for("index"))

    return render_template("index.html", error="\u274c Invalid username or password.", login_page=True, register_page=False, user=None)

@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    password = request.form["password"]

    if User.query.filter_by(username=username).first():
        return render_template("index.html", error="\u26a0\ufe0f Username already exists.", register_page=True, login_page=False, user=None)

    new_user = User(username=username)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    login_user(new_user)
    return redirect(url_for("index"))

@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/policies")
def policies():
    return render_template("policies.html")

@app.route("/contact")
def contact():
    return render_template("contactus.html")

@app.route("/advertise")
def advertise():
    return render_template("advertise.html")

if __name__ == "__main__":
    app.run(debug=True)
