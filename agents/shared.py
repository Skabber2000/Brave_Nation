"""Shared utilities and book context for Nação Valente campaign agents."""

import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from openai import OpenAI

# ── Book Context ──────────────────────────────────────────────────────────

BOOK = {
    "title": "Nação Valente — Decisões Soberanas para Portugal",
    "author": "João Annes",
    "isbn": "978-989-693-214-5",
    "price": "€19.95",
    "publisher": "Edições 70",
    "website": "https://nacaovalente.com.pt",
    "instagram": "@nacaovalente",
    "synopsis": (
        "Nação Valente proposes a strategic framework for Portugal's sovereignty "
        "built on four pillars: Prevenir (prevent threats before they materialize), "
        "Proteger (protect critical infrastructure and citizens), Projetar (project "
        "influence and values internationally), and Prosperar (build sustainable "
        "economic resilience). Drawing on cybersecurity, defense policy, and national "
        "strategy, João Annes maps a pragmatic path for Portugal in an era of "
        "geopolitical uncertainty."
    ),
    "framework_4p": [
        "Prevenir — Anticipate and neutralize threats before they materialize",
        "Proteger — Safeguard critical infrastructure, institutions, and citizens",
        "Projetar — Project Portugal's influence, values, and interests globally",
        "Prosperar — Build economic resilience and sustainable national prosperity",
    ],
    "author_bio": (
        "João Annes is a cybersecurity and national defense strategist. Former "
        "board member of the Portuguese National Cybersecurity Centre (CNCS) and "
        "active member of SEDES. With decades of experience in critical "
        "infrastructure protection and strategic policy, he brings a unique "
        "practitioner's perspective to Portugal's sovereignty challenges."
    ),
    "target_audience": (
        "Portuguese professionals, policy makers, defense/cybersecurity experts, "
        "business leaders, IR/political science students, and engaged citizens "
        "interested in Portugal's strategic direction."
    ),
    "bookstores": {
        "Bertrand": "https://www.bertrand.pt/livro/nacao-valente-joao-annes/30364709",
        "Wook": "https://www.wook.pt/livro/nacao-valente-joao-annes/30364709",
        "FNAC": "https://www.fnac.pt/Nacao-Valente-Joao-Annes/a10948038",
        "Amazon": "https://www.amazon.co.uk/dp/9896932145",
    },
    "launch_event": (
        "Culturgest, Lisbon — February 2026. Panelists: Álvaro Beleza, "
        "João Massano, António Mendonça, C/A Gameiro Marques."
    ),
    "key_quotes": [
        "Portugal precisa de uma estratégia que não dependa de ciclos eleitorais.",
        "A soberania não se decreta — constrói-se com decisões consistentes.",
        "Num mundo de ameaças híbridas, a prevenção é a primeira linha de defesa.",
        "Projetar Portugal não é ambição — é necessidade estratégica.",
        "A prosperidade sustentável exige escolhas corajosas hoje.",
    ],
    "hashtags": [
        "#NaçãoValente", "#DecisõesSoberanas", "#Portugal", "#Soberania",
        "#EstratégiaNacional", "#Cibersegurança", "#DefesaNacional",
        "#PolíticaPortuguesa", "#JoãoAnnes",
    ],
}


def get_client():
    """Initialize OpenAI client."""
    return OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def call_llm(system_prompt, user_prompt, model="gpt-4o", max_tokens=4000, temperature=0.8):
    """Call OpenAI chat completion and return text."""
    client = get_client()
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return resp.choices[0].message.content


def send_email(subject, html_body):
    """Send HTML email via Gmail SMTP."""
    smtp_email = os.environ["SMTP_EMAIL"]
    smtp_pass = os.environ["SMTP_PASSWORD"]
    to_email = os.environ["NOTIFY_EMAIL"]
    cc_email = os.environ.get("CC_EMAIL", "")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"Nação Valente Bot <{smtp_email}>"
    msg["To"] = to_email
    if cc_email:
        msg["Cc"] = cc_email

    msg.attach(MIMEText(html_body, "html"))

    recipients = [to_email]
    if cc_email:
        recipients.append(cc_email)

    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx) as srv:
        srv.login(smtp_email, smtp_pass)
        srv.sendmail(smtp_email, recipients, msg.as_string())
    print(f"✅ Email sent: {subject}")


def today():
    """Return today as YYYY-MM-DD."""
    return datetime.utcnow().strftime("%Y-%m-%d")


def iso_week():
    """Return current ISO week number."""
    return datetime.utcnow().isocalendar()[1]


def book_context():
    """Formatted book context block for LLM prompts."""
    return f"""BOOK: {BOOK['title']}
AUTHOR: {BOOK['author']} | PUBLISHER: {BOOK['publisher']}
ISBN: {BOOK['isbn']} | PRICE: {BOOK['price']}
WEBSITE: {BOOK['website']} | INSTAGRAM: {BOOK['instagram']}

SYNOPSIS: {BOOK['synopsis']}

4P FRAMEWORK:
{chr(10).join(f'  • {p}' for p in BOOK['framework_4p'])}

AUTHOR BIO: {BOOK['author_bio']}

TARGET AUDIENCE: {BOOK['target_audience']}

LAUNCH EVENT: {BOOK['launch_event']}

KEY QUOTES (Portuguese):
{chr(10).join(f'  «{q}»' for q in BOOK['key_quotes'])}

BOOKSTORE LINKS:
{chr(10).join(f'  • {k}: {v}' for k, v in BOOK['bookstores'].items())}

HASHTAGS: {' '.join(BOOK['hashtags'])}"""


def email_wrap(title, body_html):
    """Wrap content in a styled HTML email template."""
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#f5f0e8;font-family:Georgia,serif;">
<div style="max-width:680px;margin:20px auto;background:#fff;border-radius:8px;
  box-shadow:0 2px 8px rgba(0,0,0,0.1);overflow:hidden;">
  <div style="background:#1a1a2e;padding:24px 32px;">
    <h1 style="color:#C5A55A;margin:0;font-size:22px;">{title}</h1>
    <p style="color:#aaa;margin:6px 0 0;font-size:13px;">
      Nação Valente Campaign · {today()}</p>
  </div>
  <div style="padding:28px 32px;color:#2c2c2c;line-height:1.7;font-size:15px;">
    {body_html}
  </div>
  <div style="background:#f9f6f0;padding:16px 32px;font-size:12px;color:#888;
    border-top:1px solid #eee;">
    Automated by Nação Valente Campaign Bot ·
    <a href="{BOOK['website']}" style="color:#C5A55A;">nacaovalente.com.pt</a>
  </div>
</div></body></html>"""
