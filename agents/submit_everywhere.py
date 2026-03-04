#!/usr/bin/env python3
"""Submit nacaovalente.com.pt to search engines, directories, and platforms."""

import sys, os
sys.stdout.reconfigure(encoding="utf-8")

import requests
import json
from datetime import datetime

URL = "https://nacaovalente.com.pt/"
SITEMAP = "https://nacaovalente.com.pt/sitemap.xml"
TITLE = "Nação Valente — Decisões Soberanas para Portugal"
DESC = ("Nação Valente propõe um modelo estratégico para a soberania de Portugal "
        "assente em quatro pilares: Prevenir, Proteger, Projetar e Prosperar. "
        "De João Annes, especialista em cibersegurança e defesa nacional.")
AUTHOR = "João Annes"
ISBN = "978-989-693-214-5"

results = []

def log(service, status, note=""):
    results.append({"service": service, "status": status, "note": note})
    icon = "✅" if status == "OK" else "⚠️" if status == "MANUAL" else "❌"
    print(f"{icon} {service}: {status} {note}")


# ── 1. Search Engine Submissions ─────────────────────────────────────────

# IndexNow (Bing, Yandex, Seznam, Naver, DuckDuckGo)
try:
    r = requests.post("https://api.indexnow.org/indexnow",
        json={"host": "nacaovalente.com.pt", "key": "nacaovalente",
              "keyLocation": f"{URL}nacaovalente.txt",
              "urlList": [URL]}, timeout=10)
    log("IndexNow (Bing/Yandex/Seznam/Naver)", "OK" if r.status_code in (200, 202) else "FAIL",
        f"HTTP {r.status_code}")
except Exception as e:
    log("IndexNow", "FAIL", str(e))

# Bing direct
try:
    r = requests.get(f"https://www.bing.com/indexnow?url={URL}&key=nacaovalente", timeout=10)
    log("Bing IndexNow Direct", "OK" if r.status_code in (200, 202) else "FAIL",
        f"HTTP {r.status_code}")
except Exception as e:
    log("Bing Direct", "FAIL", str(e))

# ── 2. Manual Submission URLs (require browser login) ─────────────────────

manual_submissions = [
    ("Google Search Console", "https://search.google.com/search-console/welcome",
     "Add property → URL prefix → https://nacaovalente.com.pt/ → Verify via HTML tag or DNS"),
    ("Bing Webmaster Tools", "https://www.bing.com/webmasters/about?mkt=pt-PT",
     "Sign in → Add site → https://nacaovalente.com.pt/ → Verify → Submit sitemap"),
    ("Yandex Webmaster", "https://webmaster.yandex.com/sites/add/",
     "Add site → nacaovalente.com.pt → Verify → Submit sitemap"),
    ("Google Business Profile", "https://business.google.com/create",
     "Create profile for 'Nação Valente' as a Book/Product"),
    ("Google Books", "https://books.google.com/books?isbn=9789896932145",
     f"Check if ISBN {ISBN} is already listed — if not, publisher (Edições 70) can submit"),
    ("Goodreads", "https://www.goodreads.com/book/new",
     "Create author page for João Annes → Add book with ISBN, cover, description"),
    ("Open Library", "https://openlibrary.org/books/add",
     f"Add by ISBN: {ISBN} — fills automatically from publisher data"),
    ("WorldCat / OCLC", "https://search.worldcat.org/search?q=isbn:9789896932145",
     "Check if listed via library catalog. Publisher usually registers."),
    ("WIPO / ISBN Registry", "https://grp.isbn-international.org/",
     "ISBN already assigned — verify it resolves correctly in international databases"),
    ("Facebook Page", "https://business.facebook.com/latest/home?business_id=910598064909754",
     "Update Page info: website=nacaovalente.com.pt, add book details, post launch link"),
    ("Instagram Bio", "https://www.instagram.com/nacaovalente/",
     "Update bio link to https://nacaovalente.com.pt/"),
    ("LinkedIn — João Annes", "https://www.linkedin.com/in/joaoannes/",
     "Add Featured section: website link + book cover + 'Comprar' CTA"),
    ("Amazon Author Central", "https://author.amazon.co.uk/",
     "Claim author page, add bio, link to nacaovalente.com.pt"),
    ("WOOK Author Page", "https://www.wook.pt/autor/joao-annes/4991729",
     "Check author page exists and book is linked"),
    ("Bertrand Author Page", "https://www.bertrand.pt/autor/joao-annes/4991729",
     "Check author page exists with correct info"),
    ("PORDATA / Fundação Francisco Manuel dos Santos", "https://www.pordata.pt/",
     "Not a submission — but reference PORDATA stats in content for SEO backlinks"),
]

for name, url, instructions in manual_submissions:
    log(name, "MANUAL", f"{url} → {instructions}")

# ── 3. Portuguese Directories & Platforms ─────────────────────────────────

pt_directories = [
    ("SAPO (PT search)", "https://pesquisa.sapo.pt/",
     "SAPO indexes PT sites automatically via Google. Verify: search 'nação valente joão annes'"),
    ("Diretório de Sites PT", "https://www.directorio-de-sites.pt/",
     "Submit site in Cultura > Livros category"),
    ("Portugal Digital", "https://portugaldigital.pt/",
     "Government initiative — check if relevant listing available"),
    ("Worten", "https://www.worten.pt/",
     "Check if book is listed (Worten sells books online)"),
    ("El Corte Inglés PT", "https://www.elcorteingles.pt/livros/",
     "Check if book is available for additional sales channel"),
]

for name, url, instructions in pt_directories:
    log(name, "MANUAL", f"{url} → {instructions}")

# ── 4. Academic / Professional Directories ────────────────────────────────

academic = [
    ("Google Scholar", "https://scholar.google.com/",
     "If João has academic papers, link them to his Scholar profile with book reference"),
    ("ResearchGate", "https://www.researchgate.net/",
     "Create/update profile, add book as publication, link to website"),
    ("ORCID", "https://orcid.org/",
     "Register ORCID ID if not exists, add book to works"),
    ("SEDES", "https://sfranciscodosantos.pt/",
     "Request listing/mention on SEDES website (member organization)"),
]

for name, url, instructions in academic:
    log(name, "MANUAL", f"{url} → {instructions}")

# ── 5. Structured Data / Rich Results ─────────────────────────────────────

# Test structured data
try:
    r = requests.get(URL, timeout=10, verify=False)
    has_jsonld = '"@type":"Book"' in r.text or '"@type": "Book"' in r.text
    has_og = 'og:title' in r.text
    has_twitter = 'twitter:card' in r.text
    log("JSON-LD (Book schema)", "OK" if has_jsonld else "MISSING",
        "Rich results eligible" if has_jsonld else "Add Book structured data!")
    log("Open Graph tags", "OK" if has_og else "MISSING")
    log("Twitter Card tags", "OK" if has_twitter else "MISSING")
except Exception as e:
    log("Structured Data Check", "FAIL", str(e))

# Rich Results Test
log("Google Rich Results Test", "MANUAL",
    "https://search.google.com/test/rich-results?url=https://nacaovalente.com.pt/")

# ── Summary ───────────────────────────────────────────────────────────────

print("\n" + "="*60)
print(f"SUBMISSION SUMMARY — {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
print("="*60)
auto = [r for r in results if r["status"] == "OK"]
manual = [r for r in results if r["status"] == "MANUAL"]
failed = [r for r in results if r["status"] in ("FAIL", "MISSING")]

print(f"✅ Automated: {len(auto)}")
print(f"📋 Manual needed: {len(manual)}")
print(f"❌ Failed/Missing: {len(failed)}")

if failed:
    print("\nISSUES TO FIX:")
    for r in failed:
        print(f"  - {r['service']}: {r['note']}")

print(f"\nTotal platforms: {len(results)}")
