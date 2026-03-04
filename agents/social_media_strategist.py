#!/usr/bin/env python3
"""Social Media Strategist — Trending engagement opportunities for LinkedIn.

Schedule: Tuesday & Friday 7:00 UTC
Scans PT news for trending topics and suggests engagement angles with draft comments.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shared import BOOK, call_llm, send_email, email_wrap, book_context, today, iso_week

import feedparser
from datetime import datetime, timedelta

# Portuguese news RSS feeds (same as news_hook_monitor)
RSS_FEEDS = {
    "Observador": "https://observador.pt/feed/",
    "Expresso": "https://expresso.pt/rss",
    "Público": "https://feeds.feedburner.com/PublicoRSS",
    "Diário de Notícias": "https://www.dn.pt/rss/",
    "Lusa": "https://www.lusa.pt/rss",
    "RTP Notícias": "https://www.rtp.pt/noticias/rss",
}

RELEVANT_KEYWORDS = [
    "defesa", "nato", "cibersegurança", "cybersecurity", "soberania",
    "forças armadas", "segurança nacional", "geopolítica", "europa",
    "china", "rússia", "ucrânia", "infraestrutura", "energia",
    "tecnologia", "inteligência artificial", "portugal", "estratégia",
    "política externa", "economia", "investimento", "inovação",
    "digital", "proteção", "resiliência", "fronteiras", "mar",
]

SYSTEM_PROMPT = """You are an expert social media strategist specializing in
LinkedIn thought leadership for João Annes, author of "Nação Valente".

Your role:
- Identify the BEST trending topics for João to engage with on LinkedIn
- Write draft comments/reactions that position him as a strategic thinker
- Suggest profiles and posts to engage with
- Find angles that naturally connect current events to the 4P framework
- All content in European Portuguese

Strategy principles:
- Be the "wise analyst" voice — not reactive, not partisan
- Add unique value: frameworks, historical parallels, strategic implications
- Every engagement should subtly reinforce João's expertise
- Prioritize topics where cybersecurity/defense/sovereignty intersects
  with mainstream conversation
- Don't be promotional — be insightful
"""


def fetch_recent_headlines():
    """Fetch headlines from PT news RSS feeds (last 48 hours)."""
    cutoff = datetime.utcnow() - timedelta(hours=48)
    articles = []
    for source, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:15]:
                title = entry.get("title", "")
                summary = entry.get("summary", "")[:200]
                text = f"{title} {summary}".lower()
                if any(kw in text for kw in RELEVANT_KEYWORDS):
                    articles.append({
                        "source": source,
                        "title": title,
                        "summary": summary,
                        "link": entry.get("link", ""),
                    })
        except Exception as e:
            print(f"⚠️ Failed to fetch {source}: {e}")
    return articles[:20]  # Top 20 relevant articles


def main():
    week = iso_week()
    day = datetime.utcnow().strftime("%A")
    print(f"🎯 Social Media Strategist — {day}, Week {week}")

    headlines = fetch_recent_headlines()
    print(f"📰 Found {len(headlines)} relevant PT headlines")

    headlines_text = "\n".join(
        f"- [{a['source']}] {a['title']}\n  {a['summary']}\n  {a['link']}"
        for a in headlines
    ) or "No relevant headlines found — use evergreen topics."

    user_prompt = f"""Date: {today()} ({day})

{book_context()}

TRENDING PT NEWS (last 48 hours):
{headlines_text}

Based on these current events and trends, provide:

## 1. TOP 3 ENGAGEMENT OPPORTUNITIES
For each:
- **TOPIC**: What's trending and why it matters
- **ANGLE**: How João should engage (comment, share with insight, original post)
- **DRAFT TEXT** in Portuguese: Ready-to-use comment or post (200-400 words)
- **WHERE TO ENGAGE**: Suggest the type of LinkedIn posts/profiles to find
  (e.g., "search for posts about X from defense analysts")
- **CONNECTION TO BOOK**: How this ties to the 4P framework (subtle, not forced)
- **URGENCY**: Post today / within 48h / this week

## 2. PROACTIVE ENGAGEMENT CHECKLIST
- 3 types of LinkedIn posts João should like/comment on this week
- 2 connection requests to send (types of profiles, not specific people)
- 1 LinkedIn article idea if a topic is strong enough

## 3. COMPETITOR WATCH
- Any competing voices João should be aware of on these topics
- How to differentiate his perspective

Format as clean HTML with styled sections and clear headers."""

    result = call_llm(SYSTEM_PROMPT, user_prompt, max_tokens=4000)
    print(f"✅ Generated engagement strategy")

    html = email_wrap(
        f"🎯 LinkedIn Engagement — {day}",
        f"""<p style="color:#666;margin-bottom:20px;">
        {len(headlines)} trending PT topics analyzed. Top 3 engagement
        opportunities for João this {'start' if day == 'Tuesday' else 'end'} of week.</p>
        {result}"""
    )
    send_email(f"LinkedIn Strategy — {day} | Nação Valente", html)


if __name__ == "__main__":
    main()
