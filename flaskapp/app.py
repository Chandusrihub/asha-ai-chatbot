from flask import Flask, render_template, request, jsonify, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # required for sessions

# ------------------ Chatbot Home Page ------------------
@app.route("/")
def index():
    if 'user' in session:
        return render_template("index.html", name=session['user'])
    return redirect("/login")

# ------------------ Chatbot Reply Logic ------------------
@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json["message"]

    if "fever" in user_msg.lower():
        reply = "You might have an infection. Please consult a doctor if it persists."
    elif "headache" in user_msg.lower():
        reply = "Drink plenty of water and rest. If it's severe, seek medical help."
    else:
        reply = "I'm still learning. Please ask something related to health."

    return jsonify({"reply": reply})

# ------------------ Signup Route ------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password)

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (name, email, phone, password) VALUES (?, ?, ?, ?)",
                           (name, email, phone, hashed_password))
            conn.commit()
        except sqlite3.IntegrityError:
            return "⚠️ Email already exists. Try logging in."
        finally:
            conn.close()

        return redirect("/login")
    return render_template("signup.html")

# ------------------ Login Route (Step 7) ------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[4], password):
            session['user'] = user[1]  # user[1] = name
            return redirect("/welcome")
        else:
            return "⚠️ Invalid credentials. Please try again."

    return render_template("login.html")

# ------------------ Welcome Route ------------------
@app.route("/welcome")
def welcome():
    if 'user' in session:
        return render_template("welcome.html", name=session['user'])
    return redirect("/login")

# ------------------ Logout Route (Optional) ------------------
@app.route("/logout")
def logout():
    session.pop('user', None)
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)
