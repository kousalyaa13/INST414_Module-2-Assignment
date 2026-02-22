import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import time
from urllib.parse import urlparse
import os
import unicodedata

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Educational Network Project)"
}

PROCESSED_FILE = "extrovert_processed_urls.txt"
OUTPUT_FILE = "job_edges_raw.csv"

bad_headers = {
    "Related Articles",
    "Contact",
    "Information",
    "Follow Us",
    "Matching Careers",
    "Character Traits",
    "Educational Path",
    "Attractive Career Options for Introverts",
    "Trending Stories",
    "Photostories",
    "TOI",
    "Visual Stories",
    "Track your credit score with SoFi",
    "Deep focus and concentration:",
    "Thoughtful decision-making:",
    "Strong listening skills:",
    "Self-motivation:",
    "Written communication:",
}

bad_words = [
    "guide", "event", "case",
    "diversity", "mission", "hub", "study",
    "article", "blog", "contact",
    "introvert", "extrovert", "career",
    "follow", "related",
    "path", "average", "salary", "job",
    "quality", "quantity", "tip", "skill", 
    "adaptability", "situation", "professional"
]

BAD_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(w) + "s?" for w in bad_words) + r")\b",
    re.IGNORECASE
)

def load_processed_urls(path: str) -> set[str]:
    if not os.path.exists(path):
        return set()
    with open(path, "r", encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}

def mark_url_processed(path: str, url: str) -> None:
    with open(path, "a", encoding="utf-8") as f:
        f.write(url.strip() + "\n")

# cleans encoding issues and removed colons
def normalize_job_text(text: str) -> str:
    if text is None:
        return ""

    t = str(text)

    # remove encoding artifacts
    t = t.replace("\u00a0", " ")   # non-breaking space
    t = t.replace("Â", "")         # mojibake artifact

    # normalize unicode
    t = unicodedata.normalize("NFKC", t)

    # collapse whitespace
    t = " ".join(t.split()).strip()

    return t

def contains_bad_word(text: str) -> bool:
    return bool(BAD_PATTERN.search(text))

def is_job_heading(text: str) -> bool:
    text = (text or "").strip()
    lower = text.lower()

    # length
    if len(text) < 3 or len(text) > 60:
        return False

    # throw out questions / section titles
    if text.endswith("?"):
        return False

    # exact blacklist
    if text in bad_headers:
        return False

    # reject headings that look like full sentences
    if lower.count(" ") > 5:
        return False

    # drop anything that sounds like a section label (singular/plural)
    if contains_bad_word(text):
        return False

    return True

def scrape_jobs_from_url(url: str, tag_name: str) -> list[str]:
    """
    Scrape job titles from a page using the provided HTML tag (e.g., 'h2', 'h3', 'h4').
    """
    tag_name = (tag_name or "").strip().lower()
    if not tag_name:
        return []

    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    jobs = []
    for el in soup.find_all(tag_name):
        text = el.get_text(strip=True)
        text = re.sub(r"^\d+[\.\)]\s*", "", text)  # remove numbering like "1. Job"
        if is_job_heading(text):
            jobs.append(text)

    # de-duplicate while preserving order
    seen = set()
    unique_jobs = []
    for j in jobs:
        key = j.lower()
        if key not in seen:
            seen.add(key)
            unique_jobs.append(j)

    return unique_jobs

if __name__ == "__main__":
    sources = pd.read_csv("extrovert_sources.csv")
    processed = load_processed_urls(PROCESSED_FILE)

    all_rows = []

    for _, row in sources.iterrows():
        url = str(row.get("url", "")).strip()
        label = str(row.get("label", "")).strip()
        tag_name = str(row.get("tag", "")).strip()

        if not url:
            continue

        # skip old sources
        if url in processed:
            print(f"\nSkipping already-scraped: {url}")
            continue

        print(f"\nScraping NEW source: {url} (tag={tag_name})")

        try:
            jobs = scrape_jobs_from_url(url, tag_name)

            for job in jobs:
                job_clean = normalize_job_text(job)
                if job_clean:
                    all_rows.append({
                        "personality": label,
                        "job": job_clean,
                        "source": urlparse(url).netloc
                    })

            print(f"  Found {len(jobs)} jobs")

            # mark this URL as processed ONLY if scrape succeeded
            processed.add(url)
            mark_url_processed(PROCESSED_FILE, url)

        except Exception as e:
            print(f"  Error scraping {url}: {e}")

        time.sleep(1.5)

    # append only new scraped rows
    if all_rows:
        new_df = pd.DataFrame(all_rows).drop_duplicates()

        file_exists = os.path.exists(OUTPUT_FILE)
        new_df.to_csv(OUTPUT_FILE, mode="a", header=not file_exists, index=False)
        print(f"\nAppended {len(new_df)} rows to {OUTPUT_FILE}")
    else:
        print("\nNo new sources to scrape. Nothing appended.")