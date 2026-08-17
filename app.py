import sqlite3
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, url_for

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "hairbycat.db"

app = Flask(__name__)
app.secret_key = "replace-this-with-a-random-secret-key"


def init_db():
    conn = sqlite3.connect(DATABASE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


init_db()


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@app.route("/o-meni", methods=["GET"])
def o_meni():
    return render_template("o_meni.html")


@app.route("/lasni-podaljski", methods=["GET"])
def lasni_podaljski():
    return render_template("lasni_podaljski.html")


@app.route("/nega", methods=["GET"])
def nega():
    return render_template("nega.html")


@app.route("/cenik", methods=["GET"])
def cenik():
    return render_template("cenik.html")


@app.route("/kontakt", methods=["GET"])
def kontakt():
    return render_template("kontakt.html")


@app.route("/contact", methods=["POST"])
def contact():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    message = request.form.get("message", "").strip()

    if not name or not email or not message:
        flash("Prosimo, izpolnite vsa polja.", "error")
        return redirect(url_for("kontakt"))

    if "@" not in email or "." not in email.split("@")[-1]:
        flash("Vnesite veljaven e-poštni naslov.", "error")
        return redirect(url_for("kontakt"))

    conn = sqlite3.connect(DATABASE)
    conn.execute(
        "INSERT INTO messages (name, email, message) VALUES (?, ?, ?)",
        (name, email, message),
    )
    conn.commit()
    conn.close()

    flash("Sporočilo je bilo uspešno poslano. Kmalu vas kontaktiramo!", "success")
    return redirect(url_for("kontakt"))


if __name__ == "__main__":
    app.run(debug=True, port=5050)
