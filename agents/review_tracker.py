#!/usr/bin/env python3
"""
Review Tracker — Nação Valente
Monitors Portuguese bookstore pages for new reviews and ratings.
Sends alert emails for new reviews (with Claude sentiment analysis)
and weekly summary digests on Mondays.
"""

import hashlib
import json
import logging
import os
import smtplib
import time
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import requests
from openai import OpenAI
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("review_tracker")

STATE_FILE = Path(__file__).parent / "review_state.json"

STORES = [
    {
        "name": "Bertrand",
        "url": "https://www.bertrand.pt/livro/nacao-valente-joao-annes/33089561",
        "parser": "parse_bertrand",
    },
    {
        "name": "Wook",
        "url": "https://www.wook.pt/livro/nacao-valente-joao-annes/33089561",
        "parser": "parse_wook",
    },
    {
        "name": "FNAC",
        "url": "https://www.fnac.pt/Nacao-Valente-Joao-Annes/a13916384",
        "parser": "parse_fnac",
    },
    {
        "name": "Amazon UK",
        "url": "https://www.amazon.co.uk/dp/9897774025",
        "parser": "parse_amazon",
    },
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-PT,pt;q=0.9,en;q=0.8",
}

REQUEST_DELAY = 2  # seconds between requests (respectful scraping)
REQUEST_TIMEOUT = 20  # seconds

# ---------------------------------------------------------------------------
# State management
# ---------------------------------------------------------------------------


def load_state() -> dict:
    """Load previous review state from JSON file."""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as exc:
            log.warning("Could not load state file, starting fresh: %s", exc)
    return {"stores": {}, "last_check": None}


def save_state(state: dict) -> None:
    """Save review state to JSON file."""
    state["last_check"] = datetime.now(timezone.utc).isoformat()
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    log.info("State saved to %s", STATE_FILE)


def hash_review(text: str) -> str:
    """Create a short hash of review text for deduplication."""
    return hashlib.sha256(text.strip().lower().encode("utf-8")).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Page fetching
# ---------------------------------------------------------------------------


def fetch_page(url: str) -> BeautifulSoup | None:
    """Fetch a page and return parsed BeautifulSoup, or None on failure."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        if resp.status_code == 403:
            log.warning("Blocked (403) fetching %s — may need different approach", url)
            return None
        if resp.status_code == 429:
            log.warning("Rate-limited (429) fetching %s — backing off", url)
            return None
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "lxml")
    except requests.RequestException as exc:
        log.warning("Failed to fetch %s: %s", url, exc)
        return None


# ---------------------------------------------------------------------------
# Store-specific parsers
# Each returns: {"review_count": int|None, "rating": float|None,
#                "reviews": [{"text": str, "author": str, "date": str}]}
# ---------------------------------------------------------------------------


def parse_bertrand(soup: BeautifulSoup) -> dict:
    """Parse reviews from Bertrand.pt product page."""
    result = {"review_count": None, "rating": None, "reviews": []}
    try:
        # Bertrand shows rating in a star widget and review count nearby
        rating_el = soup.select_one(".rating-value, .star-rating, [itemprop='ratingValue']")
        if rating_el:
            rating_text = rating_el.get("content") or rating_el.get_text(strip=True)
            try:
                result["rating"] = float(rating_text.replace(",", "."))
            except (ValueError, TypeError):
                pass

        count_el = soup.select_one(
            ".review-count, .num-reviews, [itemprop='reviewCount']"
        )
        if count_el:
            count_text = count_el.get("content") or count_el.get_text(strip=True)
            digits = "".join(c for c in count_text if c.isdigit())
            if digits:
                result["review_count"] = int(digits)

        # Individual reviews
        review_blocks = soup.select(
            ".review-item, .comment-item, [itemprop='review'], .review-body"
        )
        for block in review_blocks[:20]:  # cap at 20
            text_el = block.select_one(
                ".review-text, .comment-text, [itemprop='reviewBody'], p"
            )
            author_el = block.select_one(
                ".review-author, [itemprop='author'], .user-name"
            )
            date_el = block.select_one(
                ".review-date, [itemprop='datePublished'], time"
            )
            if text_el:
                result["reviews"].append({
                    "text": text_el.get_text(strip=True)[:500],
                    "author": author_el.get_text(strip=True) if author_el else "Anon",
                    "date": (
                        date_el.get("datetime") or date_el.get_text(strip=True)
                        if date_el else ""
                    ),
                })

        # Fallback: count reviews from blocks if count_el was missing
        if result["review_count"] is None and result["reviews"]:
            result["review_count"] = len(result["reviews"])

    except Exception as exc:
        log.warning("Bertrand parse error: %s", exc)
    return result


def parse_wook(soup: BeautifulSoup) -> dict:
    """Parse reviews from Wook.pt product page."""
    result = {"review_count": None, "rating": None, "reviews": []}
    try:
        # Wook uses similar schema.org markup
        rating_el = soup.select_one(
            "[itemprop='ratingValue'], .rating-value, .star-rating-value"
        )
        if rating_el:
            rating_text = rating_el.get("content") or rating_el.get_text(strip=True)
            try:
                result["rating"] = float(rating_text.replace(",", "."))
            except (ValueError, TypeError):
                pass

        count_el = soup.select_one(
            "[itemprop='reviewCount'], .review-count, .num-comments"
        )
        if count_el:
            count_text = count_el.get("content") or count_el.get_text(strip=True)
            digits = "".join(c for c in count_text if c.isdigit())
            if digits:
                result["review_count"] = int(digits)

        # Wook review blocks
        review_blocks = soup.select(
            ".review-item, [itemprop='review'], .comment-block, .review"
        )
        for block in review_blocks[:20]:
            text_el = block.select_one(
                "[itemprop='reviewBody'], .review-text, .comment-body, p"
            )
            author_el = block.select_one(
                "[itemprop='author'], .review-author, .comment-author"
            )
            date_el = block.select_one(
                "[itemprop='datePublished'], .review-date, time"
            )
            if text_el:
                result["reviews"].append({
                    "text": text_el.get_text(strip=True)[:500],
                    "author": author_el.get_text(strip=True) if author_el else "Anon",
                    "date": (
                        date_el.get("datetime") or date_el.get_text(strip=True)
                        if date_el else ""
                    ),
                })

        if result["review_count"] is None and result["reviews"]:
            result["review_count"] = len(result["reviews"])

    except Exception as exc:
        log.warning("Wook parse error: %s", exc)
    return result


def parse_fnac(soup: BeautifulSoup) -> dict:
    """Parse reviews from FNAC.pt product page."""
    result = {"review_count": None, "rating": None, "reviews": []}
    try:
        # FNAC uses its own class structure for ratings
        rating_el = soup.select_one(
            ".f-productRating__value, .ratingValue, [itemprop='ratingValue']"
        )
        if rating_el:
            rating_text = rating_el.get("content") or rating_el.get_text(strip=True)
            try:
                result["rating"] = float(rating_text.replace(",", ".").replace("/5", ""))
            except (ValueError, TypeError):
                pass

        count_el = soup.select_one(
            ".f-productRating__count, .reviewCount, [itemprop='reviewCount']"
        )
        if count_el:
            count_text = count_el.get("content") or count_el.get_text(strip=True)
            digits = "".join(c for c in count_text if c.isdigit())
            if digits:
                result["review_count"] = int(digits)

        # FNAC review blocks
        review_blocks = soup.select(
            ".f-review, .customerReview, [itemprop='review'], .Review"
        )
        for block in review_blocks[:20]:
            text_el = block.select_one(
                ".f-review__text, [itemprop='reviewBody'], .reviewBody, p"
            )
            author_el = block.select_one(
                ".f-review__author, [itemprop='author'], .reviewAuthor"
            )
            date_el = block.select_one(
                ".f-review__date, [itemprop='datePublished'], time"
            )
            if text_el:
                result["reviews"].append({
                    "text": text_el.get_text(strip=True)[:500],
                    "author": author_el.get_text(strip=True) if author_el else "Anon",
                    "date": (
                        date_el.get("datetime") or date_el.get_text(strip=True)
                        if date_el else ""
                    ),
                })

        if result["review_count"] is None and result["reviews"]:
            result["review_count"] = len(result["reviews"])

    except Exception as exc:
        log.warning("FNAC parse error: %s", exc)
    return result


def parse_amazon(soup: BeautifulSoup) -> dict:
    """Parse reviews from Amazon UK product page."""
    result = {"review_count": None, "rating": None, "reviews": []}
    try:
        # Amazon rating
        rating_el = soup.select_one(
            "#acrPopover .a-size-base, [data-hook='rating-out-of-text'], "
            ".a-icon-alt, #averageCustomerReviews .a-icon-alt"
        )
        if rating_el:
            rating_text = rating_el.get_text(strip=True)
            # Format: "4.5 out of 5 stars" or "4,5 de 5"
            parts = rating_text.split()
            if parts:
                try:
                    result["rating"] = float(parts[0].replace(",", "."))
                except (ValueError, TypeError):
                    pass

        # Review count
        count_el = soup.select_one(
            "#acrCustomerReviewText, [data-hook='total-review-count']"
        )
        if count_el:
            count_text = count_el.get_text(strip=True)
            digits = "".join(c for c in count_text if c.isdigit())
            if digits:
                result["review_count"] = int(digits)

        # Amazon review blocks (may be on the product page or a separate page)
        review_blocks = soup.select(
            "[data-hook='review'], .review, .a-section.review"
        )
        for block in review_blocks[:20]:
            text_el = block.select_one(
                "[data-hook='review-body'] span, .review-text-content span, "
                ".review-text span"
            )
            author_el = block.select_one(
                ".a-profile-name, [data-hook='review-author']"
            )
            date_el = block.select_one(
                "[data-hook='review-date'], .review-date"
            )
            if text_el:
                result["reviews"].append({
                    "text": text_el.get_text(strip=True)[:500],
                    "author": author_el.get_text(strip=True) if author_el else "Anon",
                    "date": date_el.get_text(strip=True) if date_el else "",
                })

        if result["review_count"] is None and result["reviews"]:
            result["review_count"] = len(result["reviews"])

    except Exception as exc:
        log.warning("Amazon parse error: %s", exc)
    return result


# ---------------------------------------------------------------------------
# Claude sentiment analysis
# ---------------------------------------------------------------------------


def analyze_review(review_text: str) -> str:
    """Use OpenAI GPT-4o-mini to analyze review sentiment and suggest a reply."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        log.warning("OPENAI_API_KEY not set — skipping sentiment analysis")
        return "(Sentiment analysis unavailable — API key not configured)"

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=400,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Analyze this book review sentiment (positive/negative/mixed) "
                        "and suggest a brief, warm response Joao could post as a reply. "
                        "In Portuguese.\n\n"
                        f"Review:\n{review_text}"
                    ),
                }
            ],
        )
        return response.choices[0].message.content or ""
    except Exception as exc:
        log.warning("OpenAI analysis failed: %s", exc)
        return f"(Sentiment analysis error: {exc})"


# ---------------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------------


def send_email(subject: str, html_body: str) -> None:
    """Send an HTML email via Gmail SMTP."""
    smtp_email = os.environ.get("SMTP_EMAIL")
    smtp_password = os.environ.get("SMTP_PASSWORD")
    notify_email = os.environ.get("NOTIFY_EMAIL")
    cc_email = os.environ.get("CC_EMAIL", "")

    if not all([smtp_email, smtp_password, notify_email]):
        log.warning("Email credentials missing — skipping email send")
        return

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

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(smtp_email, smtp_password)
            server.sendmail(smtp_email, recipients, msg.as_string())
        log.info("Email sent: %s", subject)
    except smtplib.SMTPException as exc:
        log.error("Failed to send email: %s", exc)


# ---------------------------------------------------------------------------
# Email templates
# ---------------------------------------------------------------------------


def build_new_review_email(store_name: str, store_url: str, review: dict,
                           rating: float | None, analysis: str) -> str:
    """Build HTML body for a new review alert."""
    rating_display = f"{rating}/5" if rating else "N/A"
    return f"""\
<!DOCTYPE html>
<html lang="pt">
<head><meta charset="utf-8"></head>
<body style="font-family: Georgia, serif; max-width: 600px; margin: 0 auto;
             color: #1a1a2e; padding: 20px;">
  <h2 style="color: #E8611A; border-bottom: 2px solid #D4A843; padding-bottom: 8px;">
    Nova Review &mdash; Na&ccedil;&atilde;o Valente
  </h2>

  <table style="width:100%; border-collapse: collapse; margin: 16px 0;">
    <tr>
      <td style="padding: 6px 12px; background: #f5f5f5; font-weight: bold;">Loja</td>
      <td style="padding: 6px 12px; background: #f5f5f5;">
        <a href="{store_url}" style="color: #E8611A;">{store_name}</a>
      </td>
    </tr>
    <tr>
      <td style="padding: 6px 12px; font-weight: bold;">Rating</td>
      <td style="padding: 6px 12px;">{rating_display}</td>
    </tr>
    <tr>
      <td style="padding: 6px 12px; background: #f5f5f5; font-weight: bold;">Autor</td>
      <td style="padding: 6px 12px; background: #f5f5f5;">{review.get('author', 'Anon')}</td>
    </tr>
    <tr>
      <td style="padding: 6px 12px; font-weight: bold;">Data</td>
      <td style="padding: 6px 12px;">{review.get('date', 'N/A')}</td>
    </tr>
  </table>

  <div style="background: #fafaf5; border-left: 4px solid #D4A843; padding: 12px 16px;
              margin: 16px 0; font-style: italic;">
    &ldquo;{review.get('text', '')}&rdquo;
  </div>

  <h3 style="color: #1a1a2e;">An&aacute;lise &amp; Sugest&atilde;o de Resposta</h3>
  <div style="background: #f0f4ff; border-radius: 8px; padding: 12px 16px; margin: 12px 0;">
    {analysis.replace(chr(10), '<br>')}
  </div>

  <p style="font-size: 12px; color: #888; margin-top: 24px;">
    Review Tracker &mdash; Na&ccedil;&atilde;o Valente &bull;
    <a href="{store_url}" style="color: #888;">Ver na loja</a>
  </p>
</body>
</html>"""


def build_weekly_summary_email(store_summaries: list[dict]) -> str:
    """Build HTML body for the weekly summary digest."""
    rows = ""
    for s in store_summaries:
        rating_display = f"{s['rating']}/5" if s.get("rating") else "N/A"
        count_display = str(s.get("review_count") or 0)
        status = s.get("status", "OK")
        rows += f"""\
    <tr>
      <td style="padding: 8px 12px; border-bottom: 1px solid #eee;">
        <a href="{s['url']}" style="color: #E8611A;">{s['name']}</a>
      </td>
      <td style="padding: 8px 12px; border-bottom: 1px solid #eee; text-align: center;">
        {rating_display}
      </td>
      <td style="padding: 8px 12px; border-bottom: 1px solid #eee; text-align: center;">
        {count_display}
      </td>
      <td style="padding: 8px 12px; border-bottom: 1px solid #eee; text-align: center;">
        {status}
      </td>
    </tr>
"""
    return f"""\
<!DOCTYPE html>
<html lang="pt">
<head><meta charset="utf-8"></head>
<body style="font-family: Georgia, serif; max-width: 600px; margin: 0 auto;
             color: #1a1a2e; padding: 20px;">
  <h2 style="color: #E8611A; border-bottom: 2px solid #D4A843; padding-bottom: 8px;">
    Resumo Semanal &mdash; Na&ccedil;&atilde;o Valente
  </h2>

  <p>Resumo das reviews em todas as lojas monitoradas.</p>

  <table style="width: 100%; border-collapse: collapse; margin: 16px 0;">
    <thead>
      <tr style="background: #1a1a2e; color: #fff;">
        <th style="padding: 8px 12px; text-align: left;">Loja</th>
        <th style="padding: 8px 12px; text-align: center;">Rating</th>
        <th style="padding: 8px 12px; text-align: center;">Reviews</th>
        <th style="padding: 8px 12px; text-align: center;">Estado</th>
      </tr>
    </thead>
    <tbody>
{rows}
    </tbody>
  </table>

  <p style="font-size: 12px; color: #888; margin-top: 24px;">
    Review Tracker &mdash; Na&ccedil;&atilde;o Valente &bull;
    Gerado automaticamente todas as segundas-feiras
  </p>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------------


def main() -> None:
    log.info("=== Review Tracker — Nação Valente ===")

    state = load_state()
    new_state = {"stores": {}, "last_check": state.get("last_check")}
    prev_stores = state.get("stores", {})

    all_new_reviews: list[dict] = []  # collected across all stores
    store_summaries: list[dict] = []  # for weekly summary
    state_changed = False

    parsers = {
        "parse_bertrand": parse_bertrand,
        "parse_wook": parse_wook,
        "parse_fnac": parse_fnac,
        "parse_amazon": parse_amazon,
    }

    for i, store in enumerate(STORES):
        store_name = store["name"]
        store_url = store["url"]
        parser_fn = parsers[store["parser"]]

        log.info("Checking %s: %s", store_name, store_url)

        if i > 0:
            time.sleep(REQUEST_DELAY)

        soup = fetch_page(store_url)
        if soup is None:
            log.warning("Skipping %s — could not fetch page", store_name)
            # Carry forward previous state
            if store_name in prev_stores:
                new_state["stores"][store_name] = prev_stores[store_name]
            store_summaries.append({
                "name": store_name,
                "url": store_url,
                "rating": prev_stores.get(store_name, {}).get("rating"),
                "review_count": prev_stores.get(store_name, {}).get("review_count"),
                "status": "Fetch failed",
            })
            continue

        data = parser_fn(soup)
        log.info(
            "  %s: rating=%s, review_count=%s, reviews_found=%d",
            store_name,
            data["rating"],
            data["review_count"],
            len(data["reviews"]),
        )

        # Build current hashes
        current_hashes = {hash_review(r["text"]): r for r in data["reviews"]}

        # Compare with previous state
        prev = prev_stores.get(store_name, {})
        prev_hashes = set(prev.get("review_hashes", []))

        new_hashes = set(current_hashes.keys()) - prev_hashes
        if new_hashes:
            log.info("  %d NEW review(s) found on %s!", len(new_hashes), store_name)
            for h in new_hashes:
                review = current_hashes[h]
                all_new_reviews.append({
                    "store_name": store_name,
                    "store_url": store_url,
                    "review": review,
                    "rating": data["rating"],
                })

        # Check if review count changed (even if we can't see individual reviews)
        prev_count = prev.get("review_count")
        curr_count = data["review_count"]
        if prev_count is not None and curr_count is not None and curr_count > prev_count:
            if not new_hashes:
                log.info(
                    "  Review count increased %d -> %d on %s but no new text found",
                    prev_count, curr_count, store_name,
                )

        # Save new state for this store
        new_state["stores"][store_name] = {
            "review_count": data["review_count"],
            "rating": data["rating"],
            "review_hashes": list(set(current_hashes.keys()) | prev_hashes),
            "last_reviews": [
                {"text": r["text"][:200], "author": r["author"], "date": r["date"]}
                for r in data["reviews"][:5]
            ],
        }

        # Detect state changes
        if new_state["stores"][store_name] != prev.get(store_name):
            state_changed = True

        store_summaries.append({
            "name": store_name,
            "url": store_url,
            "rating": data["rating"],
            "review_count": data["review_count"],
            "status": f"+{len(new_hashes)} new" if new_hashes else "No changes",
        })

    # -----------------------------------------------------------------------
    # Send alert emails for new reviews
    # -----------------------------------------------------------------------
    for item in all_new_reviews:
        log.info("Analyzing review from %s with Claude...", item["store_name"])
        analysis = analyze_review(item["review"]["text"])

        subject = f"\u2b50 Nova review \u2014 Na\u00e7\u00e3o Valente [{item['store_name']}]"
        html = build_new_review_email(
            item["store_name"], item["store_url"],
            item["review"], item["rating"], analysis,
        )
        send_email(subject, html)
        time.sleep(1)  # brief pause between emails

    # -----------------------------------------------------------------------
    # Weekly summary on Mondays
    # -----------------------------------------------------------------------
    today = datetime.now(timezone.utc)
    force_summary = os.environ.get("FORCE_SUMMARY", "").lower() in ("true", "1", "yes")
    if today.weekday() == 0 or force_summary:  # Monday or forced
        log.info("Sending weekly summary (Monday=%s, forced=%s)", today.weekday() == 0, force_summary)
        subject = "\U0001f4ca Na\u00e7\u00e3o Valente \u2014 Resumo Semanal de Reviews"
        html = build_weekly_summary_email(store_summaries)
        send_email(subject, html)
    else:
        log.info("Not Monday (day=%d) — skipping weekly summary", today.weekday())

    # -----------------------------------------------------------------------
    # Save updated state
    # -----------------------------------------------------------------------
    save_state(new_state)

    # Summary
    log.info("=== Done ===")
    log.info(
        "New reviews found: %d | Stores checked: %d | State changed: %s",
        len(all_new_reviews), len(STORES), state_changed,
    )


if __name__ == "__main__":
    main()
