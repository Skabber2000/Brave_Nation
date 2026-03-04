"""
Nação Valente — Weekly Content Generator
=========================================
Generates LinkedIn + Instagram content batches for João Annes.
Sends formatted HTML email via Gmail SMTP.

Scheduled: Sundays 18:00 UTC via GitHub Actions.
Manual override: set CONTENT_THEME env var to bypass rotation.
"""

import os
import re
import sys
import logging
import smtplib
import html
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from anthropic import Anthropic

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("content_generator")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
THEMES = [
    "Lançamento e gratidão",
    "Framework 4P",
    "Eventos atuais e geopolítica",
    "Bastidores e motivação",
    "Reações dos leitores",
    "Futuro de Portugal",
]

MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 4096

# Brand colours (navy / gold)
NAVY = "#1B2A4A"
GOLD = "#C9A84C"
LIGHT_BG = "#F7F5F0"


# ---------------------------------------------------------------------------
# Theme selection
# ---------------------------------------------------------------------------
def select_theme() -> str:
    """Return the theme for this week.

    If CONTENT_THEME env var is set and non-empty, use it directly.
    Otherwise rotate through THEMES based on ISO week number.
    """
    override = os.environ.get("CONTENT_THEME", "").strip()
    if override:
        log.info("Theme override via CONTENT_THEME: %s", override)
        return override

    iso_week = datetime.utcnow().isocalendar()[1]
    index = iso_week % len(THEMES)
    theme = THEMES[index]
    log.info("Auto-selected theme (ISO week %d, index %d): %s", iso_week, index, theme)
    return theme


# ---------------------------------------------------------------------------
# Week date range for subject line
# ---------------------------------------------------------------------------
def week_date_range() -> str:
    """Return a string like '3-9 Mar 2026' for the current week (Mon-Sun)."""
    today = datetime.utcnow().date()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)

    if monday.month == sunday.month:
        return f"{monday.day}-{sunday.day} {monday.strftime('%b %Y')}"
    if monday.year == sunday.year:
        return f"{monday.day} {monday.strftime('%b')} - {sunday.day} {sunday.strftime('%b %Y')}"
    return f"{monday.strftime('%d %b %Y')} - {sunday.strftime('%d %b %Y')}"


# ---------------------------------------------------------------------------
# Claude API call
# ---------------------------------------------------------------------------
PROMPT_TEMPLATE = """\
You are a content strategist for João Annes, author of \
'Nação Valente — Decisões Soberanas para Portugal'. \
João is a cybersecurity & defense specialist (ex-CNCS, SEDES observatory). \
His book uses a 4P Framework: Prevenir, Proteger, Projetar, Prosperar.

This week's theme: {theme}

Generate the following content in Portuguese:

## LinkedIn Posts (3)
Write 3 LinkedIn thought-leadership posts (400-600 words each). \
Professional, authoritative tone. Include relevant hashtags. \
Each should have a compelling opening hook.

## Instagram Captions (3)
Write 3 Instagram captions (100-200 words each). Punchy, engaging. \
Include 10-15 hashtags from: #NacaoValente #JoaoAnnes \
#SoberaniaPortuguesa #Geopolitica #DefesaNacional #Ciberseguranca \
#Portugal #FuturoDePortugal #LiteraciaDemocratica #PensamentoEstrategico \
#PotenciaAtlantica #NATO #UniaoEuropeia

## Instagram Story Ideas (2)
Describe 2 story concepts with text overlay suggestions.

## Quote Card Text (2)
Write 2 short impactful quotes (1-2 sentences) suitable for \
graphic design overlay.

All content should feel authentic to a defense/security expert — \
not salesy. End each LinkedIn post with a question to drive engagement. \
Reference nacaovalente.com.pt where natural.\
"""


def generate_content(theme: str) -> str:
    """Call Claude API and return the generated markdown content."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        log.error("ANTHROPIC_API_KEY is not set")
        sys.exit(1)

    client = Anthropic(api_key=api_key)
    log.info("Calling Claude API (model=%s) ...", MODEL)

    message = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[
            {
                "role": "user",
                "content": PROMPT_TEMPLATE.format(theme=theme),
            }
        ],
    )

    content = message.content[0].text
    log.info(
        "Received %d characters (stop_reason=%s, tokens_in=%d, tokens_out=%d)",
        len(content),
        message.stop_reason,
        message.usage.input_tokens,
        message.usage.output_tokens,
    )
    return content


# ---------------------------------------------------------------------------
# Markdown → HTML conversion (lightweight, no extra dependency)
# ---------------------------------------------------------------------------
def markdown_to_html(md: str) -> str:
    """Convert the Claude markdown output into styled HTML body content.

    Handles ## headings, bold (**), italic (*), numbered/bulleted lists,
    hashtags, and paragraphs. Intentionally simple to avoid extra deps.
    """
    lines = md.split("\n")
    html_parts: list[str] = []
    in_list = False

    for raw_line in lines:
        line = raw_line.rstrip()

        # Close open list if this line is not a list item
        if in_list and not (line.startswith("- ") or (len(line) > 2 and line[0].isdigit() and line[1] in ".)")):
            html_parts.append("</ul>")
            in_list = False

        # Headings
        if line.startswith("## "):
            heading_text = html.escape(line[3:].strip())
            html_parts.append(
                f'<h2 style="color:{NAVY};border-bottom:2px solid {GOLD};'
                f'padding-bottom:6px;margin-top:32px;">{heading_text}</h2>'
            )
            continue

        if line.startswith("# "):
            heading_text = html.escape(line[2:].strip())
            html_parts.append(
                f'<h1 style="color:{NAVY};margin-top:36px;">{heading_text}</h1>'
            )
            continue

        # Blank line
        if not line.strip():
            html_parts.append("<br>")
            continue

        # Inline formatting
        formatted = html.escape(line)
        # Bold **text**
        formatted = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", formatted)
        # Italic *text* (but not hashtags like *#tag*)
        formatted = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", formatted)
        # Hashtags — highlight in gold
        formatted = re.sub(
            r"(#\w+)",
            rf'<span style="color:{GOLD};font-weight:600;">\1</span>',
            formatted,
        )

        # List items
        if line.startswith("- "):
            if not in_list:
                html_parts.append('<ul style="margin-left:18px;">')
                in_list = True
            html_parts.append(f"<li>{formatted[2:].strip()}</li>")
            continue

        if len(line) > 2 and line[0].isdigit() and line[1] in ".)":
            if not in_list:
                html_parts.append('<ul style="margin-left:18px;list-style-type:decimal;">')
                in_list = True
            html_parts.append(f"<li>{formatted[2:].strip()}</li>")
            continue

        # Paragraph
        html_parts.append(f"<p>{formatted}</p>")

    if in_list:
        html_parts.append("</ul>")

    return "\n".join(html_parts)


# ---------------------------------------------------------------------------
# Full HTML email
# ---------------------------------------------------------------------------
def build_email_html(theme: str, content_md: str, week_range: str) -> str:
    """Wrap generated content in a branded HTML email template."""
    body_content = markdown_to_html(content_md)

    return f"""\
<!DOCTYPE html>
<html lang="pt">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Nação Valente — Conteúdo Semanal</title>
</head>
<body style="margin:0;padding:0;background:{LIGHT_BG};font-family:Georgia,'Times New Roman',serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:{LIGHT_BG};">
<tr><td align="center" style="padding:24px 12px;">

<!-- Container -->
<table width="640" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:8px;\
box-shadow:0 2px 12px rgba(0,0,0,0.08);">

<!-- Header -->
<tr>
<td style="background:{NAVY};color:#ffffff;padding:28px 32px;border-radius:8px 8px 0 0;">
  <h1 style="margin:0;font-size:22px;letter-spacing:0.5px;">
    Nação Valente
  </h1>
  <p style="margin:8px 0 0;font-size:14px;color:{GOLD};font-weight:600;">
    Conteúdo Semanal &mdash; {html.escape(week_range)}
  </p>
</td>
</tr>

<!-- Theme banner -->
<tr>
<td style="background:{GOLD};color:{NAVY};padding:12px 32px;font-weight:700;font-size:15px;">
  Tema da semana: {html.escape(theme)}
</td>
</tr>

<!-- Content -->
<tr>
<td style="padding:24px 32px;color:#222;font-size:15px;line-height:1.7;">
{body_content}
</td>
</tr>

<!-- Footer -->
<tr>
<td style="background:{NAVY};color:#aaa;padding:18px 32px;font-size:12px;\
border-radius:0 0 8px 8px;text-align:center;">
  Gerado automaticamente para
  <a href="https://nacaovalente.com.pt" style="color:{GOLD};text-decoration:none;">nacaovalente.com.pt</a>
  &bull; João Annes &copy; {datetime.utcnow().year}
</td>
</tr>

</table>
<!-- /Container -->

</td></tr>
</table>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Email delivery
# ---------------------------------------------------------------------------
def send_email(subject: str, html_body: str) -> None:
    """Send the content email via Gmail SMTP."""
    smtp_email = os.environ.get("SMTP_EMAIL")
    smtp_password = os.environ.get("SMTP_PASSWORD")
    notify_email = os.environ.get("NOTIFY_EMAIL")
    cc_email = os.environ.get("CC_EMAIL", "")

    if not all([smtp_email, smtp_password, notify_email]):
        log.error("Missing one or more email env vars (SMTP_EMAIL, SMTP_PASSWORD, NOTIFY_EMAIL)")
        sys.exit(1)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = smtp_email
    msg["To"] = notify_email
    if cc_email:
        msg["Cc"] = cc_email

    msg.attach(MIMEText(html_body, "html", "utf-8"))

    recipients = [notify_email]
    if cc_email:
        recipients.append(cc_email)

    log.info("Sending email to %s (CC: %s) ...", notify_email, cc_email or "none")

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(smtp_email, smtp_password)
            server.sendmail(smtp_email, recipients, msg.as_string())
        log.info("Email sent successfully.")
    except smtplib.SMTPException:
        log.exception("SMTP error while sending email")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    log.info("=== Nação Valente Content Generator ===")

    theme = select_theme()
    week_range = week_date_range()

    content_md = generate_content(theme)

    email_html = build_email_html(theme, content_md, week_range)

    subject = f"\U0001f4dd Nação Valente — Conteúdo Semanal {week_range}"

    send_email(subject, email_html)

    log.info("Done. Theme: '%s' | Week: %s", theme, week_range)


if __name__ == "__main__":
    main()
