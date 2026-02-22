import requests
from bs4 import BeautifulSoup
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Educational Network Project)"
}

bad_headers = {
    "Related Articles",
    "Contact",
    "Information",
    "Follow Us",
    "Matching Careers"
    "Character Traits",
    "Educational Path",
    "Attractive Career Options for Introverts"
}

bad_words = [
    "guide", "event", "case",
    "diversity", "mission", "hub", "study",
    "article", "blog", "contact",
    "introvert", "extrovert", "career",
    "follow", "related",
    "path"
]

BAD_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(w) + "s?" for w in bad_words) + r")\b",
    re.IGNORECASE
)

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
    for tag in soup.find_all(["h4"]):
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
    url = "https://blog.steppingblocks.com/15-best-jobs-for-introverts-in-2021"
    jobs = scrape_jobs_from_url(url)

    print(f"  Found {len(jobs)} jobs")
    for j in jobs:
        print("-", j)