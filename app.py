import os
import json
from copy import deepcopy
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "database.json")

app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"))
CORS(app)
app.config["JSON_SORT_KEYS"] = False


def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def next_id(items):
    return max((int(item.get("id", 0)) for item in items), default=0) + 1


def get_json():
    return request.get_json(silent=True) or {}


def find_by_id(collection, item_id):
    return next((item for item in collection if int(item.get("id", -1)) == item_id), None)


def sprint_seed():
    # The two original sprints are retained so existing bug/test-case links still match.
    seeds = [
        {"id": 1, "sprint_code": "SPR-001", "name": "Sprint 14", "project": "E-Commerce Platform", "goal": "Checkout & Payment Improvements", "start_date": "2026-09-01", "end_date": "2026-09-14", "status": "Active", "sprint_lead": "Nishit Dubey", "team_members": ["Priya Nair", "Aditya Joshi"]},
        {"id": 2, "sprint_code": "SPR-002", "name": "Sprint 13", "project": "E-Commerce Platform", "goal": "Cart & Product Improvements", "start_date": "2026-08-18", "end_date": "2026-08-31", "status": "Completed", "sprint_lead": "Priya Nair", "team_members": ["Nishit Dubey", "Aditya Joshi"]},
    ]
    # Fill out a useful 15-sprint backlog. IDs and sprint codes remain stable.
    for number in range(1, 16):
        if number in (13, 14):
            continue
        sid = len(seeds) + 1
        start_month = max(1, min(12, 4 + number // 2))
        start_day = 1 if number % 2 else 15
        start = datetime(2026, start_month, start_day)
        end = start.replace(day=min(28, start.day + 13))
        status = "Completed" if number <= 10 else ("Active" if number == 15 else "Planned")
        seeds.append({
            "id": sid,
            "sprint_code": f"SPR-{sid:03d}",
            "name": f"Sprint {number}",
            "project": "E-Commerce Platform" if number % 3 else "Banking Mobile App",
            "goal": f"Sprint {number} delivery, QA validation, and defect resolution",
            "start_date": start.strftime("%Y-%m-%d"),
            "end_date": end.strftime("%Y-%m-%d"),
            "status": status,
            "sprint_lead": "Nishit Dubey" if number % 2 else "Priya Nair",
            "team_members": ["Priya Nair", "Aditya Joshi"] if number % 2 else ["Nishit Dubey", "Rahul Deshmukh"]
        })
    # Ensure names are unique and return exactly the initial 15 sprint records.
    seen = set()
    result = []
    for sprint in seeds:
        if sprint["name"] not in seen:
            result.append(sprint)
            seen.add(sprint["name"])
    # Add Sprint 11 and 12 explicitly if the generated list is missing them.
    for number in (11, 12):
        if f"Sprint {number}" not in seen:
            sid = max(s["id"] for s in result) + 1
            result.append({"id": sid, "sprint_code": f"SPR-{sid:03d}", "name": f"Sprint {number}", "project": "E-Commerce Platform", "goal": f"Sprint {number} regression and integration testing", "start_date": "2026-07-01", "end_date": "2026-07-14", "status": "Completed", "sprint_lead": "Priya Nair", "team_members": ["Nishit Dubey", "Aditya Joshi"]})
    # Return first 15 by name-number intent plus the legacy Sprint 13 and 14.
    by_name = {s["name"]: s for s in result}
    ordered = [by_name.get(f"Sprint {n}") for n in range(1, 13)] + [by_name.get("Sprint 13"), by_name.get("Sprint 14"), by_name.get("Sprint 15")]
    ordered = [s for s in ordered if s]
    return ordered[:15]


def default_db():
    return {
        "users": [
            {"id": 1, "username": "admin", "email": "admin@qanexus.com", "password": "admin", "role": "QA Head"},
            {"id": 2, "username": "nishit", "email": "nishit@qanexus.com", "password": "password123", "role": "QA Head"},
            {"id": 3, "username": "priya", "email": "priya@qanexus.com", "password": "password123", "role": "QA Tester"},
            {"id": 4, "username": "aditya", "email": "aditya@qanexus.com", "password": "password123", "role": "Developer"},
            {"id": 5, "username": "client", "email": "client@qanexus.com", "password": "password123", "role": "Client"},
        ],
        "projects": [
            {"id": 1, "name": "E-Commerce Platform", "code": "ECOMM", "status": "Ongoing", "progress": 75, "team_details": "Nishit Dubey (QA Head), Aditya Joshi (Developer)", "outcome": "A scalable online shopping cart with seamless payment gateway integration and real-time order tracking."},
            {"id": 2, "name": "Banking Mobile App", "code": "BANK", "status": "Done", "progress": 100, "team_details": "Priya Nair (QA Tester), Rahul Deshmukh (Developer)", "outcome": "Secure mobile banking portal with biometric authentication and zero high-severity defects."},
        ],
        "sprints": sprint_seed(),
        "bugs": [
            {"id": 1, "bug_code": "BUG-1001", "title": "Payment Gateway 504 Timeout Error", "project": "E-Commerce Platform", "sprint": "Sprint 14", "severity": "Critical", "priority": "High", "status": "Open", "description": "Checkout process fails on payment gateway redirection under peak loads.", "steps": "1. Add items to cart\n2. Proceed to checkout\n3. Select Credit Card payment\n4. Click Pay Now", "expected_result": "Payment confirmation page should load within 3 seconds.", "actual_result": "Server responds with 504 Gateway Timeout error screen.", "assigned_tester": "Priya Nair", "assigned_developer": "Aditya Joshi", "comments": [{"author": "Priya Nair", "text": "Issue reproduced during peak-load testing.", "time": "1 hour ago"}], "audit_history": [{"action": "Bug created", "user": "Priya Nair", "time": "Today"}, {"action": "Assigned to Aditya Joshi", "user": "Nishit Dubey", "time": "Today"}]},
            {"id": 2, "bug_code": "BUG-1002", "title": "Profile Avatar Upload Crop Bug", "project": "E-Commerce Platform", "sprint": "Sprint 14", "severity": "Medium", "priority": "Medium", "status": "In Progress", "description": "User profile avatar gets stretched when uploading non-square PNG images.", "steps": "1. Go to settings\n2. Upload rectangular avatar\n3. Click save", "expected_result": "Image should automatically crop to square aspect ratio.", "actual_result": "Image gets horizontally stretched.", "assigned_tester": "Nishit Dubey", "assigned_developer": "Rahul Deshmukh", "comments": [], "audit_history": [{"action": "Bug created", "user": "Nishit Dubey", "time": "Yesterday"}]},
        ],
        "test_cases": [
            {"id": 1, "test_code": "TC-1001", "title": "Verify Login with Valid Credentials", "module": "Authentication", "project": "E-Commerce Platform", "sprint": "Sprint 14", "priority": "High", "preconditions": "User account exists in system.", "steps": "1. Open login modal\n2. Enter valid email and password\n3. Click Login", "expected_result": "User should be logged in and redirected to dashboard.", "actual_result": "User successfully logged in with toast notification.", "assigned_tester": "Priya Nair", "test_result": "Passed"},
            {"id": 2, "test_code": "TC-1002", "title": "Verify Password Reset Token Expiry", "module": "Authentication", "project": "E-Commerce Platform", "sprint": "Sprint 14", "priority": "Medium", "preconditions": "Reset token generated.", "steps": "1. Request password reset\n2. Wait 15 minutes\n3. Click reset link", "expected_result": "Link should display 'Token Expired' message.", "actual_result": "Link allows password update even after expiry.", "assigned_tester": "Nishit Dubey", "test_result": "Failed"},
        ],
        "team": [
            {"id": 1, "name": "Nishit Dubey", "role": "QA Head", "department": "Tech / QA", "status": "Active", "assigned_projects": "E-Commerce Platform", "assigned_tasks": 4},
            {"id": 2, "name": "Priya Nair", "role": "QA Tester", "department": "Quality Assurance", "status": "Active", "assigned_projects": "E-Commerce Platform, Banking Mobile App", "assigned_tasks": 6},
            {"id": 3, "name": "Aditya Joshi", "role": "Developer", "department": "Backend Engineering", "status": "Away", "assigned_projects": "E-Commerce Platform", "assigned_tasks": 3},
            {"id": 4, "name": "Amitabh Banerjee", "role": "Client", "department": "Product Management", "status": "Active", "assigned_projects": "Banking Mobile App", "assigned_tasks": 0},
        ],
        "reports": [{"id": 1, "title": "Sprint 14 Defect Audit", "project": "E-Commerce Platform", "generated_by": "Nishit Dubey", "date": "2026-09-28", "summary": "Audited 12 defects logged during payment integration phase. Critical bugs isolated."}],
        "activity_logs": [
            {"id": 1, "user": "Nishit Dubey", "action": "assigned BUG-1001 to Aditya Joshi", "timestamp": "2 minutes ago", "created_at": now_text()},
            {"id": 2, "user": "Priya Nair", "action": "created Sprint 14", "timestamp": "1 hour ago", "created_at": now_text()},
        ],
    }


def load_db():
    defaults = default_db()
    if not os.path.exists(DB_FILE):
        return defaults
    try:
        with open(DB_FILE, "r", encoding="utf-8") as handle:
            loaded = json.load(handle)
        if not isinstance(loaded, dict):
            return defaults
        # Preserve saved collections but add any missing collection keys from defaults.
        for key, value in defaults.items():
            if key not in loaded or not isinstance(loaded[key], list):
                loaded[key] = deepcopy(value)
        # Upgrade older JSON files with missing sprint metadata and seed the missing sprint names.
        if len(loaded["sprints"]) < 15:
            existing_names = {str(s.get("name", "")).lower() for s in loaded["sprints"]}
            existing_codes = {str(s.get("sprint_code", "")).lower() for s in loaded["sprints"]}
            for seed in defaults["sprints"]:
                if len(loaded["sprints"]) >= 15:
                    break
                if str(seed["name"]).lower() not in existing_names:
                    item = deepcopy(seed)
                    item["id"] = next_id(loaded["sprints"])
                    code_num = next_id(loaded["sprints"])
                    item["sprint_code"] = f"SPR-{code_num:03d}"
                    while item["sprint_code"].lower() in existing_codes:
                        code_num += 1
                        item["sprint_code"] = f"SPR-{code_num:03d}"
                    loaded["sprints"].append(item)
                    existing_names.add(str(item["name"]).lower())
                    existing_codes.add(item["sprint_code"].lower())
        return loaded
    except (OSError, json.JSONDecodeError, TypeError):
        return defaults


def save_db():
    temp_file = DB_FILE + ".tmp"
    with open(temp_file, "w", encoding="utf-8") as handle:
        json.dump(db, handle, indent=2, ensure_ascii=False)
    os.replace(temp_file, DB_FILE)


db = load_db()
if not os.path.exists(DB_FILE):
    save_db()


def add_activity(user, action):
    db.setdefault("activity_logs", []).insert(0, {
        "id": next_id(db["activity_logs"]), "user": user or "QA Team", "action": action,
        "timestamp": "Just now", "created_at": now_text()
    })
    db["activity_logs"] = db["activity_logs"][:500]


def changed(user, action):
    add_activity(user, action)
    save_db()


def error(message, status=400, **extra):
    payload = {"error": message}
    payload.update(extra)
    return jsonify(payload), status


def sprint_summary(sprint):
    name = str(sprint.get("name", "")).casefold()
    project = str(sprint.get("project", "")).casefold()
    bugs = [b for b in db["bugs"] if str(b.get("sprint", "")).casefold() == name and str(b.get("project", "")).casefold() == project]
    tests = [t for t in db["test_cases"] if str(t.get("sprint", "")).casefold() == name and str(t.get("project", "")).casefold() == project]
    resolved = sum(str(b.get("status", "")).casefold() in ("resolved", "closed") for b in bugs)
    passed = sum(str(t.get("test_result", t.get("status", ""))).casefold() == "passed" for t in tests)
    total = len(bugs) + len(tests)
    done = resolved + passed
    progress = 100 if str(sprint.get("status", "")).casefold() == "completed" and total == 0 else (round(done * 100 / total) if total else 0)
    return {"total_bugs": len(bugs), "resolved_bugs": resolved, "open_bugs": len(bugs) - resolved, "total_test_cases": len(tests), "passed_tests": passed, "total_work_items": total, "completed_work_items": done, "progress": progress}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/auth/register", methods=["POST"])
def register():
    data = get_json()
    username = str(data.get("username", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))
    role = str(data.get("role", "QA Tester")).strip()
    if not username or not email or not password:
        return error("Username, email and password are required.")
    if any(u.get("username", "").lower() == username.lower() for u in db["users"]):
        return error("Username already exists!")
    if any(u.get("email", "").lower() == email for u in db["users"]):
        return error("Email already exists!")
    if role not in ["QA Tester", "Developer", "QA Head", "Client"]:
        role = "QA Tester"
    user = {"id": next_id(db["users"]), "username": username, "email": email, "password": password, "role": role}
    db["users"].append(user)
    changed(username, f"created a new {role} account")
    return jsonify({"message": "Registration successful!", "user": {k: v for k, v in user.items() if k != "password"}}), 201


@app.route("/api/auth/login", methods=["POST"])
def login():
    data = get_json() if request.is_json else request.form.to_dict()
    login_id = str(data.get("username") or data.get("email") or data.get("login") or "").strip().lower()
    password = str(data.get("password", ""))
    if not login_id or not password:
        return error("Username/email and password are required.")
    user = next((u for u in db["users"] if (u.get("username", "").lower() == login_id or u.get("email", "").lower() == login_id) and u.get("password") == password), None)
    if not user:
        return error("Invalid credentials!", 401)
    changed(user["username"], "logged into QA Core Nexus")
    return jsonify({"message": "Login successful!", "user": {k: v for k, v in user.items() if k != "password"}})


@app.route("/api/projects", methods=["GET", "POST"])
def handle_projects():
    if request.method == "GET":
        return jsonify(db["projects"])
    data = get_json(); name = str(data.get("name", "")).strip()
    if not name: return error("Project name is required.")
    pid = next_id(db["projects"])
    try: progress = max(0, min(100, int(data.get("progress", 0))))
    except (TypeError, ValueError): progress = 0
    project = {"id": pid, "name": name, "code": data.get("code", f"PRJ-{pid:03d}"), "status": data.get("status", "Ongoing"), "progress": progress, "team_details": data.get("team_details", "Unassigned"), "outcome": data.get("outcome", "No outcome specified yet.")}
    db["projects"].append(project); changed(data.get("created_by", "QA Team"), f"created project {name}")
    return jsonify(project), 201


@app.route("/api/projects/<int:pid>", methods=["GET", "PATCH", "PUT", "DELETE"])
def project_detail(pid):
    project = find_by_id(db["projects"], pid)
    if not project: return error("Project not found", 404)
    if request.method == "GET": return jsonify(project)
    if request.method == "DELETE":
        db["projects"].remove(project); changed("QA Team", f"deleted project {project['name']}"); return jsonify({"message": "Project deleted successfully"})
    data = get_json()
    for field in ("name", "code", "status", "team_details", "outcome"):
        if field in data: project[field] = data[field]
    if "progress" in data:
        try: project["progress"] = max(0, min(100, int(data["progress"])))
        except (TypeError, ValueError): pass
    changed(data.get("updated_by", "QA Team"), f"updated project {project['name']}")
    return jsonify(project)


@app.route("/api/sprints", methods=["GET", "POST"])
def handle_sprints():
    if request.method == "GET":
        return jsonify([{**s, "summary": sprint_summary(s)} for s in sorted(db["sprints"], key=lambda x: int(x.get("id", 0)))])
    data = get_json()
    name = str(data.get("name", "")).strip()
    project = str(data.get("project", "")).strip()
    start_date = str(data.get("start_date", "")).strip()
    end_date = str(data.get("end_date", "")).strip()
    if not name or not project or not start_date or not end_date:
        return error("Sprint name, project, start date, and end date are required.")
    if any(str(s.get("name", "")).casefold() == name.casefold() for s in db["sprints"]):
        return error("A sprint with this name already exists.", 409)
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date(); end = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        return error("Use valid YYYY-MM-DD sprint dates.")
    if end < start: return error("End date cannot be earlier than start date.")
    allowed = {"Planned", "Active", "On Hold", "Completed"}
    status = data.get("status", "Planned")
    if status not in allowed: return error("Invalid sprint status.", allowed_statuses=sorted(allowed))
    sid = next_id(db["sprints"])
    team_members = data.get("team_members", [])
    if isinstance(team_members, str): team_members = [x.strip() for x in team_members.split(",") if x.strip()]
    sprint = {"id": sid, "sprint_code": f"SPR-{sid:03d}", "name": name, "project": project, "goal": str(data.get("goal", "")).strip(), "start_date": start_date, "end_date": end_date, "status": status, "sprint_lead": str(data.get("sprint_lead", "QA Team")).strip() or "QA Team", "team_members": team_members if isinstance(team_members, list) else []}
    db["sprints"].append(sprint); changed(data.get("created_by", sprint["sprint_lead"]), f"created {name}")
    return jsonify({**sprint, "summary": sprint_summary(sprint)}), 201


@app.route("/api/sprints/<int:sid>", methods=["GET", "PATCH", "PUT", "DELETE"])
def sprint_detail(sid):
    sprint = find_by_id(db["sprints"], sid)
    if not sprint: return error("Sprint not found", 404)
    if request.method == "GET": return jsonify({**sprint, "summary": sprint_summary(sprint)})
    if request.method == "DELETE":
        name = sprint["name"]; db["sprints"].remove(sprint); changed("QA Team", f"deleted {name}"); return jsonify({"message": "Sprint deleted successfully"})
    data = get_json()
    updated = {**sprint}
    for field in ("name", "project", "goal", "start_date", "end_date", "status", "sprint_lead", "team_members"):
        if field in data: updated[field] = data[field]
    name = str(updated.get("name", "")).strip(); project = str(updated.get("project", "")).strip()
    if not name or not project or not updated.get("start_date") or not updated.get("end_date"):
        return error("Sprint name, project, start date, and end date are required.")
    if any(int(other.get("id", -1)) != sid and str(other.get("name", "")).casefold() == name.casefold() for other in db["sprints"]):
        return error("A sprint with this name already exists.", 409)
    try:
        start = datetime.strptime(str(updated["start_date"]), "%Y-%m-%d").date(); end = datetime.strptime(str(updated["end_date"]), "%Y-%m-%d").date()
    except ValueError: return error("Use valid YYYY-MM-DD sprint dates.")
    if end < start: return error("End date cannot be earlier than start date.")
    if updated.get("status") not in {"Planned", "Active", "On Hold", "Completed"}: return error("Invalid sprint status.", allowed_statuses=["Planned", "Active", "On Hold", "Completed"])
    if isinstance(updated.get("team_members"), str): updated["team_members"] = [x.strip() for x in updated["team_members"].split(",") if x.strip()]
    sprint.update(updated)
    changed(data.get("updated_by", "QA Team"), f"updated {sprint['name']}")
    return jsonify({**sprint, "summary": sprint_summary(sprint)})


@app.route("/api/sprints/<int:sid>/summary", methods=["GET"])
def sprint_summary_route(sid):
    sprint = find_by_id(db["sprints"], sid)
    if not sprint: return error("Sprint not found", 404)
    return jsonify({"sprint": sprint, "summary": sprint_summary(sprint)})


@app.route("/api/bugs", methods=["GET", "POST"])
def handle_bugs():
    if request.method == "GET": return jsonify(db["bugs"])
    data = get_json(); title = str(data.get("title", "")).strip()
    if not title: return error("Bug title is required.")
    bid = next_id(db["bugs"])
    bug = {"id": bid, "bug_code": f"BUG-{1000 + bid}", "title": title, "project": data.get("project", "E-Commerce Platform"), "sprint": data.get("sprint", "Sprint 14"), "severity": data.get("severity", "Medium"), "priority": data.get("priority", "Medium"), "status": data.get("status", "New"), "description": data.get("description", ""), "steps": data.get("steps", ""), "expected_result": data.get("expected_result", ""), "actual_result": data.get("actual_result", ""), "assigned_tester": data.get("assigned_tester", "Unassigned"), "assigned_developer": data.get("assigned_developer", "Unassigned"), "comments": [], "audit_history": [{"action": "Bug created", "user": data.get("created_by", "QA Team"), "time": "Just now"}]}
    db["bugs"].append(bug); changed(data.get("created_by", "QA Team"), f"created {bug['bug_code']} - {title}"); return jsonify(bug), 201


@app.route("/api/bugs/<int:bid>", methods=["GET", "PATCH", "PUT", "DELETE"])
def bug_detail(bid):
    bug = find_by_id(db["bugs"], bid)
    if not bug: return error("Bug not found", 404)
    if request.method == "GET": return jsonify(bug)
    if request.method == "DELETE":
        code = bug["bug_code"]; db["bugs"].remove(bug); changed("QA Team", f"deleted {code}"); return jsonify({"message": "Bug deleted successfully"})
    data = get_json(); editable = ["title", "project", "sprint", "severity", "priority", "status", "description", "steps", "expected_result", "actual_result", "assigned_tester", "assigned_developer"]
    changes = [field for field in editable if field in data and bug.get(field) != data[field]]
    for field in changes: bug[field] = data[field]
    if changes:
        user = data.get("updated_by", "QA Team"); bug.setdefault("audit_history", []).insert(0, {"action": "Updated: " + ", ".join(changes), "user": user, "time": "Just now"}); changed(user, f"updated {bug['bug_code']}")
    return jsonify(bug)


@app.route("/api/bugs/<int:bug_id>/status", methods=["POST", "PATCH"])
def update_bug_status(bug_id):
    bug = find_by_id(db["bugs"], bug_id)
    if not bug: return error("Bug not found", 404)
    data = get_json(); status = data.get("status"); allowed = ["New", "Open", "In Progress", "Resolved", "Retest", "Closed"]
    if status not in allowed: return error("Invalid bug status.", allowed_statuses=allowed)
    old = bug.get("status"); bug["status"] = status; user = data.get("updated_by", "QA Team")
    bug.setdefault("audit_history", []).insert(0, {"action": f"Status changed: {old} → {status}", "user": user, "time": "Just now"}); changed(user, f"changed {bug['bug_code']} status from {old} to {status}")
    return jsonify({"success": True, "status": status, "bug": bug})


@app.route("/api/bugs/<int:bug_id>/comments", methods=["GET", "POST"])
def post_bug_comment(bug_id):
    bug = find_by_id(db["bugs"], bug_id)
    if not bug: return error("Bug not found", 404)
    bug.setdefault("comments", [])
    if request.method == "GET": return jsonify(bug["comments"])
    data = get_json(); text = str(data.get("comment", "")).strip()
    if not text: return error("Comment cannot be empty.")
    author = data.get("author", "QA Team"); comment = {"author": author, "text": text, "time": "Just now"}; bug["comments"].append(comment)
    bug.setdefault("audit_history", []).insert(0, {"action": "Added a comment", "user": author, "time": "Just now"}); changed(author, f"commented on {bug['bug_code']}")
    return jsonify({"success": True, "comment": comment}), 201


@app.route("/api/test-cases", methods=["GET", "POST"])
def handle_test_cases():
    if request.method == "GET": return jsonify(db["test_cases"])
    data = get_json(); title = str(data.get("title", "")).strip()
    if not title: return error("Test case title is required.")
    tid = next_id(db["test_cases"])
    tc = {"id": tid, "test_code": f"TC-{1000 + tid}", "title": title, "module": data.get("module", "General"), "project": data.get("project", "E-Commerce Platform"), "sprint": data.get("sprint", "Sprint 14"), "priority": data.get("priority", "Medium"), "preconditions": data.get("preconditions", ""), "steps": data.get("steps", ""), "expected_result": data.get("expected_result", ""), "actual_result": data.get("actual_result", ""), "assigned_tester": data.get("assigned_tester", "Unassigned"), "test_result": data.get("test_result", "Not Run")}
    db["test_cases"].append(tc); changed(data.get("created_by", "QA Team"), f"created {tc['test_code']}"); return jsonify(tc), 201


@app.route("/api/test-cases/<int:tcid>", methods=["GET", "PATCH", "PUT", "DELETE"])
def tc_detail(tcid):
    tc = find_by_id(db["test_cases"], tcid)
    if not tc: return error("Test Case not found", 404)
    if request.method == "GET": return jsonify(tc)
    if request.method == "DELETE":
        code = tc["test_code"]; db["test_cases"].remove(tc); changed("QA Team", f"deleted {code}"); return jsonify({"message": "Test case deleted successfully"})
    data = get_json(); fields = ["title", "module", "project", "sprint", "priority", "preconditions", "steps", "expected_result", "actual_result", "assigned_tester", "test_result"]
    changed_fields = [f for f in fields if f in data and tc.get(f) != data[f]]
    for field in changed_fields: tc[field] = data[field]
    if changed_fields: changed(data.get("updated_by", "QA Team"), f"updated {tc['test_code']}")
    return jsonify(tc)


@app.route("/api/team", methods=["GET", "POST"])
def handle_team():
    if request.method == "GET": return jsonify(db["team"])
    data = get_json(); name = str(data.get("name", "")).strip(); role = str(data.get("role", "")).strip()
    if not name or not role: return error("Name and role are required.")
    mid = next_id(db["team"])
    try: tasks = max(0, int(data.get("assigned_tasks", 0)))
    except (TypeError, ValueError): tasks = 0
    member = {"id": mid, "name": name, "role": role, "department": data.get("department", "General"), "status": data.get("status", "Active"), "assigned_projects": data.get("assigned_projects", "None"), "assigned_tasks": tasks}
    db["team"].append(member); changed(data.get("created_by", "QA Team"), f"added team member {name}"); return jsonify(member), 201


@app.route("/api/team/<int:mid>", methods=["GET", "PATCH", "PUT", "DELETE"])
def team_member_detail(mid):
    member = find_by_id(db["team"], mid)
    if not member: return error("Team member not found", 404)
    if request.method == "GET": return jsonify(member)
    if request.method == "DELETE":
        name = member["name"]; db["team"].remove(member); changed("QA Team", f"removed team member {name}"); return jsonify({"message": "Team member deleted successfully"})
    data = get_json()
    for field in ("name", "role", "department", "status", "assigned_projects", "assigned_tasks"):
        if field in data:
            if field == "assigned_tasks":
                try: member[field] = max(0, int(data[field]))
                except (TypeError, ValueError): member[field] = 0
            else: member[field] = data[field]
    changed(data.get("updated_by", "QA Team"), f"updated team member {member['name']}"); return jsonify(member)


@app.route("/api/reports", methods=["GET", "POST"])
def handle_reports():
    if request.method == "GET": return jsonify(db["reports"])
    data = get_json(); title = str(data.get("title", "")).strip()
    if not title: return error("Report title is required.")
    rid = next_id(db["reports"]); report = {"id": rid, "title": title, "project": data.get("project", "E-Commerce Platform"), "generated_by": data.get("generated_by", "QA Lead"), "date": datetime.now().strftime("%Y-%m-%d"), "summary": data.get("summary", "")}
    db["reports"].append(report); changed(report["generated_by"], f"generated report {title}"); return jsonify(report), 201


@app.route("/api/reports/<int:rid>", methods=["GET", "PATCH", "PUT", "DELETE"])
def report_detail(rid):
    report = find_by_id(db["reports"], rid)
    if not report: return error("Report not found", 404)
    if request.method == "GET": return jsonify(report)
    if request.method == "DELETE":
        title = report["title"]; db["reports"].remove(report); changed("QA Team", f"deleted report {title}"); return jsonify({"message": "Report deleted successfully"})
    data = get_json()
    for field in ("title", "project", "generated_by", "summary"):
        if field in data: report[field] = data[field]
    changed(data.get("updated_by", "QA Team"), f"updated report {report['title']}"); return jsonify(report)


@app.route("/api/activity-logs", methods=["GET"])
def get_activity_logs():
    return jsonify(db["activity_logs"])


@app.route("/api/stats", methods=["GET"])
def get_stats_data():
    projects, bugs, tests = db["projects"], db["bugs"], db["test_cases"]
    resolved = sum(str(b.get("status", "")).casefold() in ("resolved", "closed") for b in bugs)
    return jsonify({"total_projects": len(projects), "total_bugs": len(bugs), "critical_bugs": sum(b.get("severity") == "Critical" for b in bugs), "high_bugs": sum(b.get("severity") == "High" for b in bugs), "medium_bugs": sum(b.get("severity") == "Medium" for b in bugs), "low_bugs": sum(b.get("severity") == "Low" for b in bugs), "pending_bugs": len(bugs) - resolved, "resolved_bugs": resolved, "total_test_cases": len(tests), "passed_test_cases": sum(t.get("test_result", t.get("status")) == "Passed" for t in tests), "overall_progress": round(resolved * 100 / len(bugs), 1) if bugs else 0})


@app.route("/api/dashboard", methods=["GET"])
def dashboard():
    projects, bugs, tests = db["projects"], db["bugs"], db["test_cases"]
    severity = {key: sum(b.get("severity", "Medium") == key for b in bugs) for key in ("Critical", "High", "Medium", "Low")}
    statuses = {key: sum(b.get("status", "New") == key for b in bugs) for key in ("New", "Open", "In Progress", "Resolved", "Retest", "Closed")}
    resolved = sum(b.get("status") in ("Resolved", "Closed") for b in bugs)
    pending = sum(b.get("status") in ("New", "Open", "In Progress", "Retest") for b in bugs)
    return jsonify({"total_projects": len(projects), "total_bugs": len(bugs), "critical_bugs": severity["Critical"], "pending_bugs": pending, "resolved_bugs": resolved, "total_test_cases": len(tests), "passed_test_cases": sum(t.get("test_result") == "Passed" for t in tests), "overall_progress": round(resolved * 100 / len(bugs)) if bugs else 0, "severity_summary": severity, "status_summary": statuses})


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "application": "QA Core Nexus", "backend": "Flask", "database": "JSON file", "projects": len(db["projects"]), "sprints": len(db["sprints"]), "bugs": len(db["bugs"]), "test_cases": len(db["test_cases"]), "team_members": len(db["team"])})


@app.errorhandler(404)
def not_found(exc):
    if request.path.startswith("/api/"): return jsonify({"error": "API endpoint not found", "path": request.path}), 404
    return exc


@app.errorhandler(500)
def internal_error(exc):
    if request.path.startswith("/api/"): return jsonify({"error": "Internal server error"}), 500
    return exc


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    print("\n" + "=" * 55 + "\n        QA CORE NEXUS - BACKEND\n" + "=" * 55)
    print(f"Server running on port: {port}\nLocal URL: http://127.0.0.1:{port}\nHealth:    http://127.0.0.1:{port}/api/health\n" + "=" * 55 + "\n")
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG", "0") == "1")
