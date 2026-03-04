#!/usr/bin/env python3
"""Visual Storyteller — Weekly visual narrative concepts.

Schedule: Tuesday 8:00 UTC
Generates 1 carousel script + 1 Story sequence + 1 Reel/video concept.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shared import BOOK, call_llm, send_email, email_wrap, book_context, today, iso_week

SYSTEM_PROMPT = """You are an expert visual storyteller specializing in
transforming strategic/political book content into compelling visual narratives
for social media.

Your expertise:
- Instagram carousel storytelling (slide-by-slide narrative arcs)
- Instagram Story sequences with interactive elements
- Short-form video concepts (Reels, 30-90 seconds)
- Visual narrative structure: hook → tension → insight → resolution → CTA
- Data visualization and infographic storytelling
- European Portuguese content

Brand guidelines for "Nação Valente":
- Visual tone: Sophisticated, editorial, strategic (like The Economist meets TED)
- Colors: Navy (#1a1a2e), Gold (#C5A55A), Cream (#f5f0e8), White
- Typography: Strong serif headings, clean sans-serif body
- Imagery: Maps, strategic diagrams, Portuguese landmarks, abstract sovereignty symbols
- NEVER partisan, sensationalist, or clickbait

Narrative principles:
- Every visual story must teach something or shift a perspective
- The 4P framework is a powerful storytelling engine — each pillar is a chapter
- Use the "what if" technique: "What if Portugal had a 20-year strategy?"
- Personal anecdotes from the author add authenticity
- End every sequence with a reason to buy or follow"""


def main():
    week = iso_week()
    print(f"🎬 Visual Storyteller — Week {week}")

    # Rotate narrative focus
    narratives = [
        "The 4P Framework overview — why Portugal needs a national strategy",
        "Prevenir in action — a cyber threat scenario and how prevention works",
        "Proteger — what critical infrastructure really means for daily life",
        "Projetar — Portugal's untapped potential on the world stage",
        "Prosperar — building an economy that doesn't depend on luck",
        "Behind the book — why João Annes wrote Nação Valente",
    ]
    narrative_focus = narratives[week % len(narratives)]

    user_prompt = f"""Date: {today()} (ISO week {week})
NARRATIVE FOCUS: {narrative_focus}

{book_context()}

Create 3 visual content concepts for this week:

## 1. INSTAGRAM CAROUSEL (5 slides, 1080×1080)
For each slide:
- **SLIDE NUMBER & ROLE** (Hook / Problem / Insight / Framework / CTA)
- **HEADLINE TEXT** on the slide (Portuguese, max 8 words)
- **BODY TEXT** on the slide (Portuguese, 1-2 short sentences)
- **VISUAL DIRECTION**: Background, colors, icons/graphics, layout
- **DESIGN NOTES**: Typography size, alignment, visual hierarchy

Also provide:
- **CAROUSEL CAPTION** (Portuguese, 200 words, with hashtags)
- **NARRATIVE ARC**: How the 5 slides build a complete story

## 2. INSTAGRAM STORY SEQUENCE (5 frames)
For each frame:
- **FRAME TYPE**: Text / Image / Poll / Question / Quiz / Countdown
- **CONTENT**: What appears on screen (Portuguese)
- **INTERACTIVE ELEMENT**: Sticker, poll question, quiz answer, etc.
- **VISUAL STYLE**: Background color, animation suggestion
- **DURATION**: How long each frame should display

Goal: Drive engagement AND swipe-up/link clicks to bio.

## 3. REEL / SHORT VIDEO CONCEPT (60-90 seconds)
- **HOOK** (first 3 seconds): What stops the scroll
- **SCRIPT**: Full spoken narration in Portuguese (João's voice)
- **VISUAL SHOTS**: Shot-by-shot description (what the viewer sees)
- **TEXT OVERLAYS**: Key phrases that appear on screen
- **MUSIC/SOUND**: Mood and audio suggestions
- **CTA**: Final call to action

Format as clean HTML with clear visual hierarchy."""

    result = call_llm(SYSTEM_PROMPT, user_prompt, max_tokens=5000)
    print(f"✅ Generated visual concepts (focus: {narrative_focus})")

    html = email_wrap(
        f"🎬 Visual Stories — Week {week}",
        f"""<p style="color:#666;margin-bottom:20px;">
        This week's narrative focus: <strong>{narrative_focus}</strong><br>
        3 visual content concepts: carousel + Story sequence + Reel.</p>
        {result}"""
    )
    send_email(f"Visual Stories — Semana {week} | Nação Valente", html)


if __name__ == "__main__":
    main()
