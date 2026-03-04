#!/usr/bin/env python3
"""Trend Researcher — Weekly PT market intelligence for book campaign.

Schedule: Wednesday 8:00 UTC
Analyzes PT news landscape, book market, and trending topics for opportunities.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shared import BOOK, call_llm, send_email, email_wrap, book_context, today, iso_week

import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# News RSS feeds
RSS_FEEDS = {
    "Observador": "https://observador.pt/feed/",
    "Expresso": "https://expresso.pt/rss",
    "Público": "https://feeds.feedburner.com/PublicoRSS",
    "Diário de Notícias": "https://www.dn.pt/rss/",
    "RTP Notícias": "https://www.rtp.pt/noticias/rss",
}

# Bertrand bestseller pages (nonfiction/politics)
BESTSELLER_URLS = [
    ("Bertrand Top Vendas", "https://www.bertrand.pt/top-vendas/livros"),
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

SYSTEM_PROMPT = """You are an expert market intelligence analyst specializing in
the Portuguese media landscape, book market, and strategic communications.

Your role:
- Analyze news trends and identify opportunities for the book "Nação Valente"
- Assess the competitive landscape in Portuguese nonfiction (defense, strategy, politics)
- Identify trending topics that connect to the book's 4P framework
- Provide actionable, time-bound recommendations
- Be analytical and evidence-based, not speculative
- Write analysis in English (for the campaign team) but include Portuguese
  keywords/phrases where relevant for social media use

Your output should read like a professional intelligence brief — concise,
prioritized, and actionable. Use bullet points, bold text for key findings,
and clearly separate observations from recommendations."""


def fetch_news_landscape():
    """Fetch PT news from last 7 days, categorized by theme."""
    cutoff = datetime.utcnow() - timedelta(days=7)
    articles = []
    for source, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:20]:
                articles.append({
                    "source": source,
                    "title": entry.get("title", ""),
                    "summary": entry.get("summary", "")[:150],
                })
        except Exception as e:
            print(f"⚠️ {source}: {e}")
    return articles[:50]


def fetch_bestsellers():
    """Try to scrape Bertrand bestseller list."""
    results = []
    for name, url in BESTSELLER_URLS:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "lxml")
                titles = soup.select(".title-lnk, .book-title, h3 a")[:10]
                for t in titles:
                    text = t.get_text(strip=True)
                    if text:
                        results.append(f"{name}: {text}")
            else:
                results.append(f"{name}: HTTP {resp.status_code} (blocked)")
        except Exception as e:
            results.append(f"{name}: Error — {e}")
    return results


def main():
    week = iso_week()
    print(f"🔍 Trend Researcher — Week {week}")

    # Gather data
    news = fetch_news_landscape()
    print(f"📰 Collected {len(news)} news articles")
    bestsellers = fetch_bestsellers()
    print(f"📚 Bestseller data: {len(bestsellers)} entries")

    news_text = "\n".join(
        f"- [{a['source']}] {a['title']}: {a['summary']}"
        for a in news
    ) or "No news articles collected."

    bestseller_text = "\n".join(f"- {b}" for b in bestsellers) or "Could not fetch bestseller data."

    user_prompt = f"""Date: {today()} (ISO week {week})

{book_context()}

You are a market intelligence analyst for the "Nação Valente" book campaign.
Analyze the following data and produce a weekly intelligence brief.

PT NEWS LANDSCAPE (last 7 days):
{news_text}

BOOKSTORE BESTSELLERS:
{bestseller_text}

Produce a comprehensive WEEKLY INTELLIGENCE BRIEF with:

## 1. NEWS LANDSCAPE ANALYSIS
- Top 5 themes dominating PT media this week
- Which themes have the strongest connection to Nação Valente's message
- Emerging narratives João should be aware of

## 2. BOOK MARKET INTELLIGENCE
- Assessment of current bestseller trends (nonfiction, politics, strategy)
- Any competing or complementary books João should reference or position against
- Window of opportunity analysis (is the market receptive this week?)

## 3. TRENDING TOPICS & KEYWORDS
- Top 10 keywords/topics trending in PT (defense, sovereignty, economy, tech)
- Social media conversation temperature (hot/warm/cold) for each
- Recommended keywords for João's posts this week

## 4. OPPORTUNITY RADAR
- **URGENT** (act this week): Specific news events João can comment on
- **MEDIUM-TERM** (next 2-4 weeks): Upcoming events, conferences, dates to prepare for
- **STRATEGIC** (next quarter): Macro trends to build content around

## 5. COMPETITIVE LANDSCAPE
- Other voices in PT on defense/sovereignty/strategy topics
- How João can differentiate (tone, depth, framework)
- Potential collaboration opportunities

## 6. WEEKLY RECOMMENDATION
- The #1 action João should take this week for maximum campaign impact
- Why, and how to execute it

Format as professional HTML with clear sections, bold key insights,
and a summary box at the top."""

    result = call_llm(SYSTEM_PROMPT, user_prompt, max_tokens=5000, temperature=0.7)
    print(f"✅ Generated intelligence brief")

    html = email_wrap(
        f"🔍 Weekly Intelligence — Week {week}",
        f"""<div style="background:#1a1a2e;color:#C5A55A;padding:16px 20px;
        border-radius:6px;margin-bottom:20px;font-size:14px;">
        <strong>INTELLIGENCE BRIEF</strong> · Week {week} · {today()}<br>
        <span style="color:#aaa;">{len(news)} news sources · bestseller data ·
        trend analysis</span></div>
        {result}"""
    )
    send_email(f"Intelligence Brief — Semana {week} | Nação Valente", html)


if __name__ == "__main__":
    main()
