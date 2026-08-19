import os
import smtplib
import sqlite3
from email.message import EmailMessage
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "hairbycat.db"
CONTACT_RECIPIENT = "catrion92@live.co.uk"

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


def send_contact_email(name, email, message):
    smtp_host = os.environ.get("SMTP_HOST")
    smtp_port = os.environ.get("SMTP_PORT")
    smtp_username = os.environ.get("SMTP_USERNAME")
    smtp_password = os.environ.get("SMTP_PASSWORD")

    if not all([smtp_host, smtp_port, smtp_username, smtp_password]):
        print("E-pošta ni bila poslana: manjkajo SMTP nastavitve v .env datoteki.", flush=True)
        return

    email_message = EmailMessage()
    email_message["Subject"] = f"Novo sporočilo s spletne strani – {name}"
    email_message["From"] = smtp_username
    email_message["To"] = CONTACT_RECIPIENT
    email_message["Reply-To"] = email
    email_message.set_content(
        f"Ime in priimek: {name}\nE-pošta: {email}\n\nSporočilo:\n{message}"
    )

    try:
        with smtplib.SMTP(smtp_host, int(smtp_port)) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(email_message)
    except Exception as e:
        print(f"E-pošte ni bilo mogoče poslati: {e}", flush=True)


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

    send_contact_email(name, email, message)

    flash("Sporočilo je bilo uspešno poslano. Kmalu vas kontaktiramo!", "success")
    return redirect(url_for("kontakt"))


if __name__ == "__main__":
    app.run(debug=True, port=5050)
