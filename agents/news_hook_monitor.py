"""
News Hook Monitor — Nação Valente
==================================
Scans Portuguese news RSS feeds daily and identifies commentary
opportunities for João Annes tied to his book
"Nação Valente — Decisões Soberanas para Portugal".

Uses OpenAI API to analyze headlines and draft LinkedIn / Instagram posts.
Sends results via Gmail SMTP.

Required env vars:
    OPENAI_API_KEY, SMTP_EMAIL, SMTP_PASSWORD, NOTIFY_EMAIL, CC_EMAIL
"""

import logging
import os
import smtplib
import sys
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from html import escape

import feedparser
from openai import OpenAI

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("news_hook_monitor")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
RSS_FEEDS: dict[str, str] = {
    "Observador": "https://observador.pt/feed/",
    "Expresso": "https://expresso.pt/rss",
    "Público": "https://feeds.feedburner.com/PublicoRSS",
    "DN": "https://www.dn.pt/rss.xml",
    "Lusa": "https://www.lusa.pt/rss",
    "RTP": "https://www.rtp.pt/noticias/rss",
}

OPENAI_MODEL = "gpt-4o"

SYSTEM_PROMPT = (
    "You are a media advisor for João Annes, author of "
    "'Nação Valente — Decisões Soberanas para Portugal'. "
    "The book covers Portuguese sovereignty, cybersecurity, defense, "
    "NATO, EU reform, migration, and democratic literacy using a 4P "
    "framework (Prevenir, Proteger, Projetar, Prosperar).\n\n"
    "Review these news headlines and identify the top 3-5 that João "
    "could comment on to promote his book. For each, provide:\n"
    "1. The headline and source\n"
    "2. Which book chapter/pillar it connects to\n"
    "3. A suggested LinkedIn post draft (200-400 words, in Portuguese, "
    "authoritative tone)\n"
    "4. A suggested Instagram caption (shorter, with hashtags)\n\n"
    "If no headlines are relevant today, say so clearly."
)

CUTOFF_HOURS = 24

# ---------------------------------------------------------------------------
# RSS fetching
# ---------------------------------------------------------------------------

def fetch_recent_articles() -> list[dict]:
    """Return articles published within the last CUTOFF_HOURS across all feeds."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=CUTOFF_HOURS)
    articles: list[dict] = []

    for source, url in RSS_FEEDS.items():
        try:
            log.info("Fetching RSS: %s (%s)", source, url)
            feed = feedparser.parse(url)

            if feed.bozo and not feed.entries:
                log.warning("Feed %s returned bozo error: %s", source, feed.bozo_exception)
                continue

            count_before = len(articles)
            for entry in feed.entries:
                published = None

                # feedparser normalises dates into *_parsed (time.struct_time)
                for date_field in ("published_parsed", "updated_parsed"):
                    parsed = getattr(entry, date_field, None)
                    if parsed:
                        published = datetime(*parsed[:6], tzinfo=timezone.utc)
                        break

                # Skip articles without a parseable date or older than cutoff
                if published is None or published < cutoff:
                    continue

                summary = ""
                if hasattr(entry, "summary"):
                    summary = entry.summary
                elif hasattr(entry, "description"):
                    summary = entry.description

                articles.append(
                    {
                        "source": source,
                        "title": getattr(entry, "title", "(sem título)"),
                        "link": getattr(entry, "link", ""),
                        "published": published.isoformat(),
                        "summary": summary[:500],  # trim to avoid huge payloads
                    }
                )

            log.info(
                "  %s: %d recent articles (of %d total entries)",
                source,
                len(articles) - count_before,
                len(feed.entries),
            )

        except Exception:
            log.exception("Failed to fetch/parse feed %s — skipping", source)

    log.info("Total recent articles collected: %d", len(articles))
    return articles


# ---------------------------------------------------------------------------
# Claude analysis
# ---------------------------------------------------------------------------

def analyse_with_openai(articles: list[dict]) -> str:
    """Send article data to OpenAI and return the analysis text."""
    client = OpenAI()

    # Build the user message with all headlines
    lines: list[str] = []
    for i, art in enumerate(articles, 1):
        lines.append(
            f"{i}. [{art['source']}] {art['title']}\n"
            f"   Link: {art['link']}\n"
            f"   Published: {art['published']}\n"
            f"   Summary: {art['summary']}\n"
        )

    user_text = (
        f"Today is {datetime.now(timezone.utc).strftime('%Y-%m-%d')}.\n\n"
        f"Here are {len(articles)} recent Portuguese news articles:\n\n"
        + "\n".join(lines)
    )

    log.info("Sending %d articles to OpenAI (%s) for analysis...", len(articles), OPENAI_MODEL)

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        max_tokens=4096,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text},
        ],
    )

    result_text = response.choices[0].message.content or ""
    log.info("OpenAI response received (%d chars).", len(result_text))
    return result_text


# ---------------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------------

def build_html_email(analysis: str, article_count: int, today: str) -> str:
    """Wrap the Claude analysis in a clean HTML email body."""
    # Convert markdown-ish text to basic HTML:
    # - preserve line breaks
    # - escape HTML entities
    safe = escape(analysis)
    # Turn blank lines into paragraph breaks
    paragraphs = safe.split("\n\n")
    body_html = "".join(f"<p>{p.replace(chr(10), '<br>')}</p>" for p in paragraphs)

    return f"""\
<!DOCTYPE html>
<html lang="pt">
<head><meta charset="utf-8"></head>
<body style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 720px;
             margin: 0 auto; padding: 24px; color: #1a1a2e;">
  <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 24px;">
    <tr>
      <td>
        <h1 style="margin: 0; font-size: 22px; color: #1a1a2e;">
          Nação Valente — Oportunidades de Media
        </h1>
        <p style="margin: 4px 0 0; font-size: 14px; color: #666;">{today} &middot; {article_count} artigos analisados</p>
      </td>
    </tr>
  </table>
  <hr style="border: none; border-top: 2px solid #E8611A; margin-bottom: 24px;">
  <div style="font-size: 15px; line-height: 1.6;">
    {body_html}
  </div>
  <hr style="border: none; border-top: 1px solid #ddd; margin-top: 32px;">
  <p style="font-size: 12px; color: #999; margin-top: 12px;">
    Gerado automaticamente pelo News Hook Monitor &middot; Nação Valente
  </p>
</body>
</html>"""


def build_no_news_html(today: str) -> str:
    """Short email when no relevant articles were found."""
    return f"""\
<!DOCTYPE html>
<html lang="pt">
<head><meta charset="utf-8"></head>
<body style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 720px;
             margin: 0 auto; padding: 24px; color: #1a1a2e;">
  <h1 style="font-size: 22px; color: #1a1a2e;">Nação Valente — Media Monitor</h1>
  <p style="font-size: 14px; color: #666;">{today}</p>
  <hr style="border: none; border-top: 2px solid #E8611A; margin-bottom: 24px;">
  <p style="font-size: 16px;">Sem oportunidades relevantes hoje.</p>
  <p style="font-size: 14px; color: #666;">
    Nenhum dos artigos publicados nas últimas 24 horas tem ligação directa
    aos temas do livro. O monitor volta a correr amanhã às 08h00 (Lisboa).
  </p>
  <hr style="border: none; border-top: 1px solid #ddd; margin-top: 32px;">
  <p style="font-size: 12px; color: #999;">
    Gerado automaticamente pelo News Hook Monitor &middot; Nação Valente
  </p>
</body>
</html>"""


def send_email(html_body: str, subject: str) -> None:
    """Send an HTML email via Gmail SMTP."""
    smtp_email = os.environ["SMTP_EMAIL"]
    smtp_password = os.environ["SMTP_PASSWORD"]
    notify_email = os.environ["NOTIFY_EMAIL"]
    cc_email = os.environ.get("CC_EMAIL", "")

    msg = MIMEMultipart("alternative")
    msg["From"] = smtp_email
    msg["To"] = notify_email
    if cc_email:
        msg["Cc"] = cc_email
    msg["Subject"] = subject
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    recipients = [notify_email]
    if cc_email:
        recipients.append(cc_email)

    log.info("Sending email to %s (CC: %s)...", notify_email, cc_email or "none")

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(smtp_email, smtp_password)
        server.sendmail(smtp_email, recipients, msg.as_string())

    log.info("Email sent successfully.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    subject = f"\U0001f514 Nação Valente — Oportunidades de Media [{today}]"

    # Validate required env vars early
    required_vars = ["OPENAI_API_KEY", "SMTP_EMAIL", "SMTP_PASSWORD", "NOTIFY_EMAIL"]
    missing = [v for v in required_vars if not os.environ.get(v)]
    if missing:
        log.error("Missing required environment variables: %s", ", ".join(missing))
        sys.exit(1)

    # 1. Fetch articles
    articles = fetch_recent_articles()

    if not articles:
        log.info("No recent articles found across any feed.")
        html = build_no_news_html(today)
        try:
            send_email(html, subject)
        except Exception:
            log.exception("Failed to send 'no news' email.")
        return

    # 2. Analyse with Claude
    try:
        analysis = analyse_with_openai(articles)
    except Exception:
        log.exception("Claude API call failed.")
        sys.exit(1)

    # 3. Build and send email
    html = build_html_email(analysis, len(articles), today)
    try:
        send_email(html, subject)
    except Exception:
        log.exception("Failed to send results email.")
        sys.exit(1)

    log.info("Done. %d articles analysed, email dispatched.", len(articles))


if __name__ == "__main__":
    main()
