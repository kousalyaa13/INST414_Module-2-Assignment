import requests
from bs4 import BeautifulSoup
import re
import os
import unicodedata

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Educational Network Project)"
}

PROCESSED_FILE = "processed_urls.txt"
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
    "guide", "case",
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

def scrape_jobs_from_url(url: str) -> list[str]:
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    jobs = []
    for tag in soup.find_all(["h2"]):
        text = tag.get_text(strip=True)
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
    url = "https://www.careeraddict.com/extrovert-jobs"
    jobs = scrape_jobs_from_url(url)

    print(f"  Found {len(jobs)} jobs")
    for j in jobs:
        print("-", j)