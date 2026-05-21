import os
import re
import json
from datetime import datetime

# =========================
# 1. Basic paths
# =========================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

BACKEND_DIR = os.path.join(BASE_DIR, "backend")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

PRD_PATH = os.path.join(BASE_DIR, "PRD.md")
APP_PATH = os.path.join(BACKEND_DIR, "app.py")

REQUIREMENTS_PATH = os.path.join(OUTPUT_DIR, "requirements.json")
RULES_PATH = os.path.join(OUTPUT_DIR, "rules.json")
TEST_CASES_PATH = os.path.join(OUTPUT_DIR, "test_cases.json")
BUGS_PATH = os.path.join(OUTPUT_DIR, "bugs.json")
REPORT_JSON_PATH = os.path.join(OUTPUT_DIR, "report.json")
REPORT_MD_PATH = os.path.join(OUTPUT_DIR, "test_report.md")

os.makedirs(BACKEND_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


# =========================
# 2. Create PRD
# =========================

prd_content = """
# Login and Registration System PRD

## Registration Requirements

1. Username cannot be empty.
2. Username length must be greater than 6 characters.
3. Password cannot be empty.
4. Password length must be greater than 8 characters.
5. Email format must be valid.
6. Confirm password must be the same as password.
7. If the username already exists, registration should fail.
8. If all information is valid, registration should succeed.

## Login Requirements

1. Username cannot be empty.
2. Password cannot be empty.
3. Users can log in only when username and password are correct.
4. If username or password is incorrect, login should fail.
5. After successful login, the system should return a welcome message.

## Intentional Bug

The PRD requires username length to be greater than 6 characters.
However, the backend intentionally does not validate username length.
"""

with open(PRD_PATH, "w", encoding="utf-8") as f:
    f.write(prd_content)

print("PRD.md created.")


# =========================
# 3. Create Flask backend with intentional bug
# =========================

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

with open(APP_PATH, "w", encoding="utf-8") as f:
    f.write(backend_code)

print("Backend app.py created.")


# =========================
# 4. PRD rule extraction
# =========================

with open(PRD_PATH, "r", encoding="utf-8") as f:
    prd_text = f.read()

rules = []

username_match = re.search(
    r"username length must be greater than (\\d+) characters",
    prd_text,
    re.IGNORECASE
)

if username_match:
    rules.append({
        "rule_id": "RULE_001",
        "module": "register",
        "field": "username",
        "condition": "length_greater_than",
        "value": int(username_match.group(1)),
        "expected_behavior": "Registration should fail when username length is not greater than 6."
    })

rules.extend([
    {
        "rule_id": "RULE_002",
        "module": "register",
        "field": "password",
        "condition": "length_greater_than",
        "value": 8,
        "expected_behavior": "Registration should fail when password length is not greater than 8."
    },
    {
        "rule_id": "RULE_003",
        "module": "register",
        "field": "email",
        "condition": "valid_format",
        "value": "contains @",
        "expected_behavior": "Registration should fail when email format is invalid."
    },
    {
        "rule_id": "RULE_004",
        "module": "register",
        "field": "confirm_password",
        "condition": "same_as_password",
        "value": True,
        "expected_behavior": "Registration should fail when confirm password does not match password."
    }
])

with open(RULES_PATH, "w", encoding="utf-8") as f:
    json.dump(rules, f, indent=4, ensure_ascii=False)

print("Rules extracted.")


# =========================
# 5. Requirement analysis
# =========================

requirements = []

for rule in rules:
    requirements.append({
        "requirement_id": "REQ_" + rule["rule_id"].split("_")[-1],
        "module": rule["module"],
        "field": rule["field"],
        "type": "validation",
        "rule": f'{rule["field"]} {rule["condition"]} {rule["value"]}',
        "risk": "Invalid input may be accepted if validation is missing."
    })

with open(REQUIREMENTS_PATH, "w", encoding="utf-8") as f:
    json.dump(requirements, f, indent=4, ensure_ascii=False)

print("requirements.json created.")


# =========================
# 6. Test case generation
# =========================

test_cases = [
    {
        "case_id": "TC_REG_001",
        "module": "register",
        "description": "Username shorter than required length",
        "endpoint": "/register",
        "method": "POST",
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
        "description": "Username equals boundary length",
        "endpoint": "/register",
        "method": "POST",
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
        "description": "Valid registration",
        "endpoint": "/register",
        "method": "POST",
        "input": {
            "username": "abcdefg",
            "password": "123456789",
            "email": "test3@example.com",
            "confirm_password": "123456789"
        },
        "expected_status": 200
    },
    {
        "case_id": "TC_REG_004",
        "module": "register",
        "description": "Password shorter than required length",
        "endpoint": "/register",
        "method": "POST",
        "input": {
            "username": "validuser1",
            "password": "123",
            "email": "test4@example.com",
            "confirm_password": "123"
        },
        "expected_status": 400
    },
    {
        "case_id": "TC_REG_005",
        "module": "register",
        "description": "Invalid email format",
        "endpoint": "/register",
        "method": "POST",
        "input": {
            "username": "validuser2",
            "password": "123456789",
            "email": "invalidemail",
            "confirm_password": "123456789"
        },
        "expected_status": 400
    },
    {
        "case_id": "TC_REG_006",
        "module": "register",
        "description": "Confirm password does not match password",
        "endpoint": "/register",
        "method": "POST",
        "input": {
            "username": "validuser3",
            "password": "123456789",
            "email": "test6@example.com",
            "confirm_password": "987654321"
        },
        "expected_status": 400
    },
    {
        "case_id": "TC_LOGIN_001",
        "module": "login",
        "description": "Login with correct username and password",
        "endpoint": "/login",
        "method": "POST",
        "input": {
            "username": "abcdefg",
            "password": "123456789"
        },
        "expected_status": 200
    },
    {
        "case_id": "TC_LOGIN_002",
        "module": "login",
        "description": "Login with wrong password",
        "endpoint": "/login",
        "method": "POST",
        "input": {
            "username": "abcdefg",
            "password": "wrongpassword"
        },
        "expected_status": 400
    }
]

with open(TEST_CASES_PATH, "w", encoding="utf-8") as f:
    json.dump(test_cases, f, indent=4, ensure_ascii=False)

print("test_cases.json created.")


# =========================
# 7. Execute tests using Flask test client
# =========================

import sys
sys.path.insert(0, BACKEND_DIR)

from app import app

client = app.test_client()

execution_results = []

for case in test_cases:
    if case["method"] == "POST":
        response = client.post(case["endpoint"], json=case["input"])
    else:
        continue

    actual_status = response.status_code
    actual_response = response.get_json()

    result = "PASS" if actual_status == case["expected_status"] else "FAIL"

    execution_results.append({
        "case_id": case["case_id"],
        "module": case["module"],
        "description": case["description"],
        "expected_status": case["expected_status"],
        "actual_status": actual_status,
        "actual_response": actual_response,
        "result": result
    })

print("Tests executed.")


# =========================
# 8. Auto bug detection
# =========================

bugs = []

for result in execution_results:
    if result["result"] == "FAIL":
        bugs.append({
            "bug_id": "BUG_" + result["case_id"],
            "title": "Requirement validation failed",
            "severity": "HIGH",
            "priority": "P1",
            "module": result["module"],
            "related_case": result["case_id"],
            "description": result["description"],
            "expected_result": result["expected_status"],
            "actual_result": result["actual_status"],
            "actual_response": result["actual_response"],
            "status": "OPEN",
            "created_by": "auto_test_plugin"
        })

with open(BUGS_PATH, "w", encoding="utf-8") as f:
    json.dump(bugs, f, indent=4, ensure_ascii=False)

print("bugs.json created.")


# =========================
# 9. Report generation
# =========================

total = len(execution_results)
passed = sum(1 for r in execution_results if r["result"] == "PASS")
failed = sum(1 for r in execution_results if r["result"] == "FAIL")

report_summary = {
    "generated_time": str(datetime.now()),
    "total_cases": total,
    "passed": passed,
    "failed": failed,
    "bug_count": len(bugs),
    "results": execution_results,
    "bugs": bugs
}

with open(REPORT_JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(report_summary, f, indent=4, ensure_ascii=False)

report_md = f"""
# Automated Test Report

Generated Time: {datetime.now()}

## Summary

- Total Cases: {total}
- Passed: {passed}
- Failed: {failed}
- Bugs: {len(bugs)}

## PRD Rules

"""

for rule in rules:
    report_md += f"- {rule['field']} {rule['condition']} {rule['value']}\\n"

report_md += """

## Test Results

"""

for result in execution_results:
    report_md += (
        f"### {result['case_id']} - {result['description']}\\n"
        f"- Expected Status: {result['expected_status']}\\n"
        f"- Actual Status: {result['actual_status']}\\n"
        f"- Result: {result['result']}\\n"
        f"- Response: {result['actual_response']}\\n\\n"
    )

report_md += """

## Auto Generated Bugs

"""

for bug in bugs:
    report_md += (
        f"### {bug['bug_id']}\\n"
        f"- Title: {bug['title']}\\n"
        f"- Severity: {bug['severity']}\\n"
        f"- Priority: {bug['priority']}\\n"
        f"- Related Case: {bug['related_case']}\\n"
        f"- Description: {bug['description']}\\n"
        f"- Expected: {bug['expected_result']}\\n"
        f"- Actual: {bug['actual_result']}\\n"
        f"- Status: {bug['status']}\\n\\n"
    )

with open(REPORT_MD_PATH, "w", encoding="utf-8") as f:
    f.write(report_md)

print("report.json created.")
print("test_report.md created.")

print("\n==============================")
print("Workflow Completed")
print("==============================")
print(f"Total Cases: {total}")
print(f"Passed: {passed}")
print(f"Failed: {failed}")
print(f"Bugs: {len(bugs)}")
print("==============================")