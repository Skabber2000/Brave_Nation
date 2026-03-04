#!/usr/bin/env python3
"""LinkedIn Ghostwriter — Weekly ready-to-publish LinkedIn posts for João Annes.

Schedule: Monday 8:00 UTC
Generates 3 polished LinkedIn posts with hooks, body, CTA, and hashtags.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shared import BOOK, call_llm, send_email, email_wrap, book_context, today, iso_week

SYSTEM_PROMPT = """You are an expert LinkedIn ghostwriter and content strategist for
João Annes, author of "Nação Valente — Decisões Soberanas para Portugal".

Your role:
- Write in João's voice: authoritative but accessible, strategic but practical,
  serious about Portugal's future but never partisan or alarmist.
- João writes in PORTUGUESE (European Portuguese, not Brazilian).
- Every post must subtly reinforce his expertise in cybersecurity, defense, and
  national strategy without being overtly promotional.
- Posts should generate engagement: thought-provoking questions, contrarian takes,
  or frameworks people want to share.

Style guidelines:
- Open with a strong hook (first 2 lines are visible before "see more")
- Use short paragraphs (2-3 sentences max)
- Include line breaks between paragraphs for readability
- End with a question or call-to-action that invites discussion
- 1200-1500 characters per post (LinkedIn sweet spot)
- Include 3-5 relevant hashtags at the end
- Mix post types: thought leadership, personal insight, framework/listicle
"""


def main():
    week = iso_week()
    user_prompt = f"""Date: {today()} (ISO week {week})

{book_context()}

Generate 3 LinkedIn posts for João Annes to publish this week (Monday, Wednesday, Friday).

For each post provide:
1. **POST TITLE** (internal reference, not published)
2. **BEST DAY/TIME** to publish (Lisbon timezone)
3. **POST TYPE** (Thought Leadership / Personal Insight / Framework / Industry Commentary)
4. **FULL POST TEXT** in Portuguese — ready to copy-paste into LinkedIn
5. **ENGAGEMENT PREDICTION** (why this post should perform well)

Make each post different in tone and format. At least one should reference current
events or trends in defense, cybersecurity, or sovereignty (you can reference generic
current topics even if you don't have today's specific news).

One post should subtly mention the book or 4P framework without being a hard sell.

Format your output in clean HTML with <h3> for each post title and styled sections."""

    print(f"📝 LinkedIn Ghostwriter — Week {week}")
    result = call_llm(SYSTEM_PROMPT, user_prompt, max_tokens=4000)
    print(f"✅ Generated 3 LinkedIn posts")

    html = email_wrap(
        f"📝 LinkedIn Posts — Week {week}",
        f"""<p style="color:#666;margin-bottom:20px;">
        3 ready-to-publish LinkedIn posts for João Annes this week.
        Copy-paste directly into LinkedIn.</p>
        {result}
        <hr style="border:none;border-top:1px solid #eee;margin:24px 0;">
        <p style="color:#888;font-size:13px;">
        💡 <strong>Tip:</strong> Post between 8:00–9:30 AM Lisbon time for
        maximum reach. Engage with comments in the first hour.</p>"""
    )
    send_email(f"LinkedIn Posts — Semana {week} | Nação Valente", html)


if __name__ == "__main__":
    main()
