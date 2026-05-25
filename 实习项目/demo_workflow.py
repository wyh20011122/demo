import os
import re
import sys
import json
import time
from pathlib import Path
from datetime import datetime


# ============================================================
# 0. Project Paths
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

BACKEND_DIR = BASE_DIR / "backend"
OUTPUT_DIR = BASE_DIR / "output"
ISSUES_DIR = OUTPUT_DIR / "issues"

PRD_PATH = BASE_DIR / "PRD.md"
APP_PATH = BACKEND_DIR / "app.py"
REQUIREMENTS_TXT_PATH = BASE_DIR / "requirements.txt"

RULES_PATH = OUTPUT_DIR / "rules.json"
RULE_CATEGORIES_PATH = OUTPUT_DIR / "rule_categories.json"
REQUIREMENTS_PATH = OUTPUT_DIR / "requirements.json"
TEST_CASES_PATH = OUTPUT_DIR / "test_cases.json"
EXECUTION_RESULTS_PATH = OUTPUT_DIR / "execution_results.json"
BUGS_PATH = OUTPUT_DIR / "bugs.json"
REPORT_JSON_PATH = OUTPUT_DIR / "report.json"
REPORT_MD_PATH = OUTPUT_DIR / "test_report.md"
WORKFLOW_MD_PATH = OUTPUT_DIR / "workflow.md"

BACKEND_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
ISSUES_DIR.mkdir(exist_ok=True)


def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def write_text(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


# ============================================================
# 1. Create requirements.txt
# ============================================================

requirements_txt = """flask
flask-cors
"""

write_text(REQUIREMENTS_TXT_PATH, requirements_txt)


# ============================================================
# 2. Create PRD
# ============================================================

prd_content = """
# Login and Registration System PRD

## 1. Project Background

This project is a simple login and registration system used as the system under test.
The purpose is to verify whether an automated testing plugin can analyze PRD requirements,
generate test cases, execute tests, generate reports, and automatically create bugs.

## 2. Registration Requirements

1. Username cannot be empty.
2. Username length must be greater than 6 characters.
3. Username should not contain SQL injection patterns.
4. Username should not contain script tags.
5. Password cannot be empty.
6. Password length must be greater than 8 characters.
7. Email format must be valid.
8. Confirm password must be the same as password.
9. If the username already exists, registration should fail.
10. If all information is valid, registration should succeed.

## 3. Login Requirements

1. Username cannot be empty.
2. Password cannot be empty.
3. Users can log in only when username and password are correct.
4. If username or password is incorrect, login should fail.
5. If the user does not exist, login should fail.
6. After successful login, the system should return a welcome message.

## 4. Intentional Bug

The PRD requires username length to be greater than 6 characters.

However, the backend intentionally does not validate username length during registration.

This means usernames such as "abc" and "abcdef" can still be registered successfully.

This intentional bug is used to demonstrate automated PRD-based testing and bug generation.
"""

write_text(PRD_PATH, prd_content)

print("PRD.md created.")


# ============================================================
# 3. Create Flask Backend
# ============================================================

backend_code = """
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

users = {}


@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Backend is running"}), 200


@app.route("/register", methods=["POST"])
def register():
    data = request.json or {}

    username = data.get("username")
    password = data.get("password")
    email = data.get("email")
    confirm_password = data.get("confirm_password")

    if not username:
        return jsonify({"error": "Username is required"}), 400

    # Intentional Bug:
    # PRD requires username length > 6,
    # but this backend does NOT validate username length.

    # Intentional Security Weakness:
    # The backend also does not validate SQL injection or script tags in username.

    if not password:
        return jsonify({"error": "Password is required"}), 400

    if len(password) <= 8:
        return jsonify({"error": "Password must be longer than 8 characters"}), 400

    if email and "@" not in email:
        return jsonify({"error": "Invalid email format"}), 400

    if confirm_password is not None and confirm_password != password:
        return jsonify({"error": "Confirm password does not match"}), 400

    if username in users:
        return jsonify({"error": "Username already exists"}), 400

    users[username] = {
        "password": password,
        "email": email
    }

    return jsonify({"message": "Register success"}), 200


@app.route("/login", methods=["POST"])
def login():
    data = request.json or {}

    username = data.get("username")
    password = data.get("password")

    if not username:
        return jsonify({"error": "Username is required"}), 400

    if not password:
        return jsonify({"error": "Password is required"}), 400

    if username not in users:
        return jsonify({"error": "User does not exist"}), 400

    if users[username]["password"] != password:
        return jsonify({"error": "Incorrect password"}), 400

    return jsonify({
        "message": "Login success",
        "data": "Welcome! You have successfully logged in."
    }), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
"""

write_text(APP_PATH, backend_code)

print("Backend app.py created.")


# ============================================================
# 4. PRD Rule Extraction
# ============================================================

prd_text = PRD_PATH.read_text(encoding="utf-8")

rules = []

username_length_match = re.search(
    r"Username length must be greater than (\\d+) characters",
    prd_text,
    re.IGNORECASE
)

if username_length_match:
    rules.append({
        "rule_id": "RULE_001",
        "module": "register",
        "field": "username",
        "condition": "length_greater_than",
        "value": int(username_length_match.group(1)),
        "category": "validation",
        "expected_behavior": "Registration should fail when username length is not greater than 6."
    })

manual_rules = [
    {
        "rule_id": "RULE_002",
        "module": "register",
        "field": "username",
        "condition": "not_empty",
        "value": True,
        "category": "validation",
        "expected_behavior": "Registration should fail when username is empty."
    },
    {
        "rule_id": "RULE_003",
        "module": "register",
        "field": "username",
        "condition": "no_sql_injection",
        "value": True,
        "category": "security",
        "expected_behavior": "Registration should fail when username contains SQL injection patterns."
    },
    {
        "rule_id": "RULE_004",
        "module": "register",
        "field": "username",
        "condition": "no_script_tag",
        "value": True,
        "category": "security",
        "expected_behavior": "Registration should fail when username contains script tags."
    },
    {
        "rule_id": "RULE_005",
        "module": "register",
        "field": "password",
        "condition": "not_empty",
        "value": True,
        "category": "validation",
        "expected_behavior": "Registration should fail when password is empty."
    },
    {
        "rule_id": "RULE_006",
        "module": "register",
        "field": "password",
        "condition": "length_greater_than",
        "value": 8,
        "category": "validation",
        "expected_behavior": "Registration should fail when password length is not greater than 8."
    },
    {
        "rule_id": "RULE_007",
        "module": "register",
        "field": "email",
        "condition": "valid_format",
        "value": "contains @",
        "category": "format",
        "expected_behavior": "Registration should fail when email format is invalid."
    },
    {
        "rule_id": "RULE_008",
        "module": "register",
        "field": "confirm_password",
        "condition": "same_as_password",
        "value": True,
        "category": "validation",
        "expected_behavior": "Registration should fail when confirm password does not match password."
    },
    {
        "rule_id": "RULE_009",
        "module": "register",
        "field": "username",
        "condition": "unique",
        "value": True,
        "category": "business",
        "expected_behavior": "Registration should fail when username already exists."
    },
    {
        "rule_id": "RULE_010",
        "module": "login",
        "field": "username",
        "condition": "not_empty",
        "value": True,
        "category": "validation",
        "expected_behavior": "Login should fail when username is empty."
    },
    {
        "rule_id": "RULE_011",
        "module": "login",
        "field": "password",
        "condition": "not_empty",
        "value": True,
        "category": "validation",
        "expected_behavior": "Login should fail when password is empty."
    },
    {
        "rule_id": "RULE_012",
        "module": "login",
        "field": "credentials",
        "condition": "correct_username_password",
        "value": True,
        "category": "business",
        "expected_behavior": "Login should succeed only when username and password are correct."
    }
]

rules.extend(manual_rules)

write_json(RULES_PATH, rules)

print("rules.json created.")


# ============================================================
# 5. Rule Classification
# ============================================================

rule_categories = {
    "validation": [],
    "business": [],
    "format": [],
    "security": []
}

for rule in rules:
    category = rule.get("category", "validation")

    if category not in rule_categories:
        rule_categories[category] = []

    rule_categories[category].append(rule)

write_json(RULE_CATEGORIES_PATH, rule_categories)

print("rule_categories.json created.")


# ============================================================
# 6. Requirement Analysis
# ============================================================

requirements = []

for rule in rules:
    requirements.append({
        "requirement_id": "REQ_" + rule["rule_id"].split("_")[-1],
        "source_rule_id": rule["rule_id"],
        "module": rule["module"],
        "field": rule["field"],
        "type": rule["category"],
        "rule": f'{rule["field"]} {rule["condition"]} {rule["value"]}',
        "risk": "Requirement violation may lead to invalid behavior, security risk, or business inconsistency."
    })

write_json(REQUIREMENTS_PATH, requirements)

print("requirements.json created.")


# ============================================================
# 7. Test Case Generation
# ============================================================

test_cases = [
    {
        "case_id": "TC_REG_001",
        "module": "register",
        "case_type": "boundary",
        "description": "Username shorter than required length",
        "endpoint": "/register",
        "method": "POST",
        "related_rule_ids": ["RULE_001"],
        "input": {
            "username": "abc",
            "password": "123456789",
            "email": "test1@example.com",
            "confirm_password": "123456789"
        },
        "expected_status": 400
    },
    {
        "case_id": "TC_REG_002",
        "module": "register",
        "case_type": "boundary",
        "description": "Username equals boundary length",
        "endpoint": "/register",
        "method": "POST",
        "related_rule_ids": ["RULE_001"],
        "input": {
            "username": "abcdef",
            "password": "123456789",
            "email": "test2@example.com",
            "confirm_password": "123456789"
        },
        "expected_status": 400
    },
    {
        "case_id": "TC_REG_003",
        "module": "register",
        "case_type": "valid",
        "description": "Valid registration",
        "endpoint": "/register",
        "method": "POST",
        "related_rule_ids": ["RULE_001", "RULE_006", "RULE_007", "RULE_008"],
        "input": {
            "username": "abcdefg",
            "password": "123456789",
            "email": "valid@example.com",
            "confirm_password": "123456789"
        },
        "expected_status": 200
    },
    {
        "case_id": "TC_REG_004",
        "module": "register",
        "case_type": "negative",
        "description": "Username is empty",
        "endpoint": "/register",
        "method": "POST",
        "related_rule_ids": ["RULE_002"],
        "input": {
            "username": "",
            "password": "123456789",
            "email": "emptyuser@example.com",
            "confirm_password": "123456789"
        },
        "expected_status": 400
    },
    {
        "case_id": "TC_REG_005",
        "module": "register",
        "case_type": "negative",
        "description": "Password is empty",
        "endpoint": "/register",
        "method": "POST",
        "related_rule_ids": ["RULE_005"],
        "input": {
            "username": "validuser1",
            "password": "",
            "email": "test5@example.com",
            "confirm_password": ""
        },
        "expected_status": 400
    },
    {
        "case_id": "TC_REG_006",
        "module": "register",
        "case_type": "boundary",
        "description": "Password shorter than required length",
        "endpoint": "/register",
        "method": "POST",
        "related_rule_ids": ["RULE_006"],
        "input": {
            "username": "validuser2",
            "password": "12345678",
            "email": "test6@example.com",
            "confirm_password": "12345678"
        },
        "expected_status": 400
    },
    {
        "case_id": "TC_REG_007",
        "module": "register",
        "case_type": "format",
        "description": "Invalid email format",
        "endpoint": "/register",
        "method": "POST",
        "related_rule_ids": ["RULE_007"],
        "input": {
            "username": "validuser3",
            "password": "123456789",
            "email": "invalidemail",
            "confirm_password": "123456789"
        },
        "expected_status": 400
    },
    {
        "case_id": "TC_REG_008",
        "module": "register",
        "case_type": "negative",
        "description": "Confirm password does not match password",
        "endpoint": "/register",
        "method": "POST",
        "related_rule_ids": ["RULE_008"],
        "input": {
            "username": "validuser4",
            "password": "123456789",
            "email": "test8@example.com",
            "confirm_password": "987654321"
        },
        "expected_status": 400
    },
    {
        "case_id": "TC_REG_009",
        "module": "register",
        "case_type": "business",
        "description": "Duplicate username registration",
        "endpoint": "/register",
        "method": "POST",
        "related_rule_ids": ["RULE_009"],
        "input": {
            "username": "abcdefg",
            "password": "123456789",
            "email": "duplicate@example.com",
            "confirm_password": "123456789"
        },
        "expected_status": 400
    },
    {
        "case_id": "TC_REG_010",
        "module": "register",
        "case_type": "security",
        "description": "SQL injection pattern in username",
        "endpoint": "/register",
        "method": "POST",
        "related_rule_ids": ["RULE_003"],
        "input": {
            "username": "' OR 1=1 --",
            "password": "123456789",
            "email": "sql@example.com",
            "confirm_password": "123456789"
        },
        "expected_status": 400
    },
    {
        "case_id": "TC_REG_011",
        "module": "register",
        "case_type": "security",
        "description": "Script tag in username",
        "endpoint": "/register",
        "method": "POST",
        "related_rule_ids": ["RULE_004"],
        "input": {
            "username": "<script>alert(1)</script>",
            "password": "123456789",
            "email": "xss@example.com",
            "confirm_password": "123456789"
        },
        "expected_status": 400
    },
    {
        "case_id": "TC_LOGIN_001",
        "module": "login",
        "case_type": "valid",
        "description": "Login with correct username and password",
        "endpoint": "/login",
        "method": "POST",
        "related_rule_ids": ["RULE_012"],
        "input": {
            "username": "abcdefg",
            "password": "123456789"
        },
        "expected_status": 200
    },
    {
        "case_id": "TC_LOGIN_002",
        "module": "login",
        "case_type": "negative",
        "description": "Login with wrong password",
        "endpoint": "/login",
        "method": "POST",
        "related_rule_ids": ["RULE_012"],
        "input": {
            "username": "abcdefg",
            "password": "wrongpassword"
        },
        "expected_status": 400
    },
    {
        "case_id": "TC_LOGIN_003",
        "module": "login",
        "case_type": "negative",
        "description": "Login with empty username",
        "endpoint": "/login",
        "method": "POST",
        "related_rule_ids": ["RULE_010"],
        "input": {
            "username": "",
            "password": "123456789"
        },
        "expected_status": 400
    },
    {
        "case_id": "TC_LOGIN_004",
        "module": "login",
        "case_type": "negative",
        "description": "Login with non-existing user",
        "endpoint": "/login",
        "method": "POST",
        "related_rule_ids": ["RULE_012"],
        "input": {
            "username": "notexistuser",
            "password": "123456789"
        },
        "expected_status": 400
    }
]

write_json(TEST_CASES_PATH, test_cases)

print("test_cases.json created.")


# ============================================================
# 8. Execute Tests with Flask Test Client
# ============================================================

sys.path.insert(0, str(BACKEND_DIR))

from app import app

client = app.test_client()

execution_results = []

for case in test_cases:
    start_time = time.time()

    if case["method"] == "POST":
        response = client.post(
            case["endpoint"],
            json=case["input"]
        )
    else:
        continue

    end_time = time.time()
    execution_time = round(end_time - start_time, 4)

    actual_status = response.status_code
    actual_response = response.get_json()

    result = "PASS" if actual_status == case["expected_status"] else "FAIL"

    execution_results.append({
        "case_id": case["case_id"],
        "module": case["module"],
        "case_type": case["case_type"],
        "description": case["description"],
        "endpoint": case["endpoint"],
        "related_rule_ids": case["related_rule_ids"],
        "expected_status": case["expected_status"],
        "actual_status": actual_status,
        "actual_response": actual_response,
        "execution_time_seconds": execution_time,
        "result": result
    })

write_json(EXECUTION_RESULTS_PATH, execution_results)

print("execution_results.json created.")


# ============================================================
# 9. Bug Detection
# ============================================================

def classify_bug(result):
    if result["case_type"] == "security":
        return "CRITICAL", "P0"

    if result["expected_status"] == 400 and result["actual_status"] == 200:
        return "HIGH", "P1"

    if result["module"] == "login":
        return "MEDIUM", "P2"

    return "MEDIUM", "P2"


def generate_bug_title(result):
    desc = result["description"].lower()

    if "username shorter" in desc or "boundary length" in desc:
        return "Username length validation missing"

    if "sql injection" in desc:
        return "SQL injection input validation missing"

    if "script tag" in desc:
        return "XSS input validation missing"

    if "password" in desc:
        return "Password validation failed"

    if "email" in desc:
        return "Email format validation failed"

    return "Requirement validation failed"


raw_bugs = []

for result in execution_results:
    if result["result"] == "FAIL":
        severity, priority = classify_bug(result)

        raw_bugs.append({
            "title": generate_bug_title(result),
            "severity": severity,
            "priority": priority,
            "module": result["module"],
            "related_case": result["case_id"],
            "related_rule_ids": result["related_rule_ids"],
            "description": result["description"],
            "expected_result": result["expected_status"],
            "actual_result": result["actual_status"],
            "actual_response": result["actual_response"],
            "root_cause": "Backend implementation is inconsistent with PRD requirements.",
            "status": "OPEN",
            "created_by": "auto_test_plugin"
        })


# ============================================================
# 10. Bug Deduplication
# ============================================================

dedup_map = {}

for bug in raw_bugs:
    key = (
        bug["title"],
        bug["module"],
        bug["root_cause"]
    )

    if key not in dedup_map:
        dedup_map[key] = {
            "title": bug["title"],
            "severity": bug["severity"],
            "priority": bug["priority"],
            "module": bug["module"],
            "related_cases": [bug["related_case"]],
            "related_rule_ids": bug["related_rule_ids"],
            "descriptions": [bug["description"]],
            "expected_result": bug["expected_result"],
            "actual_result": bug["actual_result"],
            "actual_response": bug["actual_response"],
            "root_cause": bug["root_cause"],
            "status": bug["status"],
            "created_by": bug["created_by"]
        }
    else:
        dedup_map[key]["related_cases"].append(bug["related_case"])
        dedup_map[key]["related_rule_ids"].extend(bug["related_rule_ids"])
        dedup_map[key]["descriptions"].append(bug["description"])

bugs = []

for index, bug in enumerate(dedup_map.values(), start=1):
    bug["bug_id"] = f"BUG-{datetime.now().strftime('%Y%m%d')}-{index:03d}"
    bug["related_rule_ids"] = sorted(list(set(bug["related_rule_ids"])))
    bugs.append(bug)

write_json(BUGS_PATH, bugs)

print("bugs.json created.")


# ============================================================
# 11. Auto Create Bug Ticket Files
# ============================================================

for bug in bugs:
    actual_response_text = json.dumps(
        bug["actual_response"],
        indent=4,
        ensure_ascii=False
    )

    issue_content = (
        "# {bug_id}\n\n"
        "## Title\n\n"
        "{title}\n\n"
        "## Module\n\n"
        "{module}\n\n"
        "## Severity\n\n"
        "{severity}\n\n"
        "## Priority\n\n"
        "{priority}\n\n"
        "## Status\n\n"
        "{status}\n\n"
        "## Related Test Cases\n\n"
        "{related_cases}\n\n"
        "## Related PRD Rules\n\n"
        "{related_rules}\n\n"
        "## Description\n\n"
        "{description}\n\n"
        "## Expected Result\n\n"
        "{expected_result}\n\n"
        "## Actual Result\n\n"
        "{actual_result}\n\n"
        "## Actual Response\n\n"
        "```json\n"
        "{actual_response}\n"
        "```\n\n"
        "## Root Cause\n\n"
        "{root_cause}\n\n"
        "## Created By\n\n"
        "{created_by}\n"
    ).format(
        bug_id=bug["bug_id"],
        title=bug["title"],
        module=bug["module"],
        severity=bug["severity"],
        priority=bug["priority"],
        status=bug["status"],
        related_cases=", ".join(bug["related_cases"]),
        related_rules=", ".join(bug["related_rule_ids"]),
        description="; ".join(bug["descriptions"]),
        expected_result=bug["expected_result"],
        actual_result=bug["actual_result"],
        actual_response=actual_response_text,
        root_cause=bug["root_cause"],
        created_by=bug["created_by"]
    )

    issue_path = ISSUES_DIR / f"{bug['bug_id']}.md"
    write_text(issue_path, issue_content)

print("Bug ticket markdown files created.")