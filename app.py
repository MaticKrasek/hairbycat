import os
import smtplib
import sqlite3
from email.message import EmailMessage
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for

from translations import TRANSLATIONS

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


def send_contact_email(name, email, message, lang):
    smtp_host = os.environ.get("SMTP_HOST")
    smtp_port = os.environ.get("SMTP_PORT")
    smtp_username = os.environ.get("SMTP_USERNAME")
    smtp_password = os.environ.get("SMTP_PASSWORD")

    if not all([smtp_host, smtp_port, smtp_username, smtp_password]):
        print("E-pošta ni bila poslana: manjkajo SMTP nastavitve v .env datoteki.", flush=True)
        return

    t = TRANSLATIONS[lang]["kontakt"]

    email_message = EmailMessage()
    email_message["Subject"] = t["email_subject"].format(name=name)
    email_message["From"] = smtp_username
    email_message["To"] = CONTACT_RECIPIENT
    email_message["Reply-To"] = email
    email_message.set_content(
        t["email_body"].format(name=name, email=email, message=message)
    )

    try:
        with smtplib.SMTP(smtp_host, int(smtp_port)) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(email_message)
    except Exception as e:
        print(f"E-pošte ni bilo mogoče poslati: {e}", flush=True)


def get_lang():
    return "en" if request.path.startswith("/en/") else "sl"


@app.route("/", endpoint="home_sl")
@app.route("/en/", endpoint="home_en")
def home():
    lang = get_lang()
    return render_template("index.html", lang=lang, page="home", t=TRANSLATIONS[lang])


@app.route("/o-meni", endpoint="o_meni_sl")
@app.route("/en/o-meni", endpoint="o_meni_en")
def o_meni():
    lang = get_lang()
    return render_template("o_meni.html", lang=lang, page="o_meni", t=TRANSLATIONS[lang])


@app.route("/lasni-podaljski", endpoint="lasni_podaljski_sl")
@app.route("/en/lasni-podaljski", endpoint="lasni_podaljski_en")
def lasni_podaljski():
    lang = get_lang()
    return render_template("lasni_podaljski.html", lang=lang, page="lasni_podaljski", t=TRANSLATIONS[lang])


@app.route("/nega", endpoint="nega_sl")
@app.route("/en/nega", endpoint="nega_en")
def nega():
    lang = get_lang()
    return render_template("nega.html", lang=lang, page="nega", t=TRANSLATIONS[lang])


@app.route("/cenik", endpoint="cenik_sl")
@app.route("/en/cenik", endpoint="cenik_en")
def cenik():
    lang = get_lang()
    return render_template("cenik.html", lang=lang, page="cenik", t=TRANSLATIONS[lang])


@app.route("/kontakt", endpoint="kontakt_sl")
@app.route("/en/kontakt", endpoint="kontakt_en")
def kontakt():
    lang = get_lang()
    return render_template("kontakt.html", lang=lang, page="kontakt", t=TRANSLATIONS[lang])


@app.route("/contact", endpoint="contact_sl", methods=["POST"])
@app.route("/en/contact", endpoint="contact_en", methods=["POST"])
def contact():
    lang = get_lang()
    t = TRANSLATIONS[lang]["kontakt"]
    kontakt_endpoint = "kontakt_en" if lang == "en" else "kontakt_sl"

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    message = request.form.get("message", "").strip()

    if not name or not email or not message:
        flash(t["error_missing_fields"], "error")
        return redirect(url_for(kontakt_endpoint))

    if "@" not in email or "." not in email.split("@")[-1]:
        flash(t["error_invalid_email"], "error")
        return redirect(url_for(kontakt_endpoint))

    conn = sqlite3.connect(DATABASE)
    conn.execute(
        "INSERT INTO messages (name, email, message) VALUES (?, ?, ?)",
        (name, email, message),
    )
    conn.commit()
    conn.close()

    send_contact_email(name, email, message, lang)

    flash(t["success"], "success")
    return redirect(url_for(kontakt_endpoint))


if __name__ == "__main__":
    app.run(debug=True, port=5050)
