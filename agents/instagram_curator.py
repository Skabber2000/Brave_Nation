#!/usr/bin/env python3
"""Instagram Curator — Weekly grid plan with captions, hashtags, and timing.

Schedule: Monday 9:00 UTC
Generates a 5-post weekly grid plan plus Stories suggestions.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shared import BOOK, call_llm, send_email, email_wrap, book_context, today, iso_week

SYSTEM_PROMPT = """You are an expert Instagram marketing curator for the book
"Nação Valente" by João Annes (@nacaovalente).

Your expertise:
- Visual storytelling for non-fiction/thought leadership brands
- Instagram algorithm optimization (2025-2026 best practices)
- Portuguese audience engagement patterns
- Cohesive grid aesthetics for professional/authority brands

Brand aesthetic:
- Colors: Navy (#1a1a2e), Gold (#C5A55A), Warm cream (#f5f0e8)
- Tone: Authoritative, elegant, strategic — NOT casual or trendy
- Visual style: Clean typography-focused designs, book photography, editorial layouts
- Language: European Portuguese

Content mix (per week):
- 2 quote cards (book quotes with strong typography)
- 1 educational/framework post (4P pillars, infographic style)
- 1 behind-the-scenes or author insight
- 1 engagement post (question, poll, or community callout)

Output all captions and text in PORTUGUESE."""


def main():
    week = iso_week()
    user_prompt = f"""Date: {today()} (ISO week {week})

{book_context()}

Create a complete Instagram grid plan for @nacaovalente this week.

For each of 5 posts, provide:
1. **POST #** and **DAY** (Mon through Fri)
2. **POST TYPE** (Quote Card / Educational / Behind-the-Scenes / Engagement)
3. **VISUAL DESCRIPTION** — exact description of what the image should look like
   (colors, layout, text overlay, photography direction)
4. **CAPTION** in Portuguese (150-300 words, with line breaks, emojis sparingly)
5. **HASHTAG SET** — 20 hashtags in 3 tiers:
   - 5 high-reach (#Portugal, #Política)
   - 10 medium (#EstratégiaNacional, #Cibersegurança)
   - 5 niche (#NaçãoValente, #DecisõesSoberanas)
6. **BEST TIME** to post (Lisbon timezone)

Then add a STORIES PLAN:
- 3 Story sequences for the week (2-4 frames each)
- Include interactive elements (polls, questions, quizzes)
- At least one should drive traffic to bio link

Also provide GRID AESTHETIC NOTES:
- How these 5 posts create visual rhythm in the 3-column grid
- Color balance across the row

Format as clean HTML with styled sections."""

    print(f"📸 Instagram Curator — Week {week}")
    result = call_llm(SYSTEM_PROMPT, user_prompt, max_tokens=5000)
    print(f"✅ Generated weekly grid plan")

    html = email_wrap(
        f"📸 Instagram Grid Plan — Week {week}",
        f"""<p style="color:#666;margin-bottom:20px;">
        Complete 5-post grid plan + Stories for @nacaovalente this week.</p>
        {result}
        <hr style="border:none;border-top:1px solid #eee;margin:24px 0;">
        <p style="color:#888;font-size:13px;">
        📊 <strong>Best times for PT audience:</strong> Tue-Thu 12:00-13:00,
        Mon/Fri 8:30-9:30 (Lisbon). Stories: 18:00-20:00.</p>"""
    )
    send_email(f"Instagram Grid — Semana {week} | Nação Valente", html)


if __name__ == "__main__":
    main()
