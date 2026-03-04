#!/usr/bin/env python3
"""Image Prompt Engineer — Weekly AI image generation prompts.

Schedule: Monday 10:00 UTC
Generates 5 Midjourney/DALL-E prompts tied to the week's content themes.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shared import BOOK, call_llm, send_email, email_wrap, book_context, today, iso_week

SYSTEM_PROMPT = """You are an expert AI image prompt engineer specializing in
professional, editorial-quality visuals for book marketing campaigns.

Your expertise:
- Crafting detailed prompts for Midjourney v6, DALL-E 3, and Stable Diffusion
- Professional photography terminology (aperture, focal length, lighting)
- Editorial and corporate visual aesthetics
- Creating brand-consistent imagery across a campaign

Brand visual identity for "Nação Valente":
- Primary: Navy blue (#1a1a2e), Gold (#C5A55A), Warm cream (#f5f0e8)
- Style: Sophisticated, authoritative, European editorial
- Mood: Strategic confidence, forward-looking, Portuguese national pride
- Avoid: Casual, trendy, aggressive/militaristic, partisan imagery
- References: The Economist covers, editorial photography, strategic consulting visuals

Output format for each prompt:
- Midjourney format (--ar, --v, --style, --s, etc.)
- DALL-E 3 format (natural language, detailed)
- Visual description for a human designer (fallback)

IMPORTANT: Never include real people's faces or likenesses in prompts.
Use symbolic, abstract, or environmental imagery instead."""


def main():
    week = iso_week()
    print(f"🎨 Image Prompt Engineer — Week {week}")

    # Rotate themes by week
    themes = [
        ("Prevenção & Antecipação", "Prevenir pillar — foresight, intelligence, early warning"),
        ("Proteção & Resiliência", "Proteger pillar — shields, infrastructure, digital security"),
        ("Projeção Internacional", "Projetar pillar — Portugal in the world, diplomacy, influence"),
        ("Prosperidade Sustentável", "Prosperar pillar — growth, innovation, economic strength"),
        ("Soberania Digital", "Cybersecurity, data sovereignty, digital autonomy"),
        ("Portugal Estratégico", "Portugal's strategic position, Atlantic, geopolitics"),
    ]
    theme_name, theme_desc = themes[week % len(themes)]

    user_prompt = f"""Date: {today()} (ISO week {week})
WEEKLY THEME: {theme_name} — {theme_desc}

{book_context()}

Generate 5 AI image prompts for this week's social media content:

1. **LINKEDIN HEADER** (1584×396) — Professional banner for João's LinkedIn
   featuring the week's theme
2. **INSTAGRAM QUOTE CARD BACKGROUND** (1080×1080) — Textured/atmospheric
   background for overlaying a Portuguese quote
3. **INSTAGRAM FEED POST** (1080×1080) — Editorial-style image for an
   educational post about the weekly 4P pillar
4. **INSTAGRAM STORY** (1080×1920) — Vertical atmospheric image for Story
   background
5. **META AD CREATIVE** (1080×1080) — Eye-catching image for a book
   promotion ad

For each prompt provide:
- **PURPOSE**: What this image is for
- **MIDJOURNEY PROMPT**: Full Midjourney v6 prompt with parameters
- **DALL-E 3 PROMPT**: Natural language prompt for DALL-E 3
- **DESIGNER BRIEF**: 2-3 sentence description for a human designer
- **COLOR NOTES**: How brand colors should appear

Format as clean HTML with styled sections. Use <code> blocks for the prompts
so they're easy to copy-paste."""

    result = call_llm(SYSTEM_PROMPT, user_prompt, max_tokens=4500)
    print(f"✅ Generated 5 image prompts (theme: {theme_name})")

    html = email_wrap(
        f"🎨 Image Prompts — Week {week}: {theme_name}",
        f"""<p style="color:#666;margin-bottom:20px;">
        5 AI image generation prompts for this week's theme:
        <strong>{theme_name}</strong>. Copy prompts directly into
        Midjourney or DALL-E.</p>
        {result}
        <hr style="border:none;border-top:1px solid #eee;margin:24px 0;">
        <p style="color:#888;font-size:13px;">
        🎨 <strong>Pro tip:</strong> Generate 4 variations per prompt in
        Midjourney, pick the best, then upscale to 2x for print quality.</p>"""
    )
    send_email(f"Image Prompts — Semana {week}: {theme_name} | Nação Valente", html)


if __name__ == "__main__":
    main()
