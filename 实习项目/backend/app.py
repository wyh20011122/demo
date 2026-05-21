
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
