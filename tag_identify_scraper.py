import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import time
from urllib.parse import urlparse

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Educational Network Project)"
}

BAD_HEADINGS = {
    "Related Articles",
    "Contact",
    "Information",
    "Follow Us",
    "Matching Careers, Character Traits and Educational Path",
    "Seven Attractive Career Options for Introverts"
}

def is_job_heading(text: str) -> bool:
    text = text.strip()
    lower = text.lower()

    # length
    if len(text) < 3 or len(text) > 60:
        return False

    # throw out questions / section titles
    if text.endswith("?"):
        return False

    # drop anything that sounds like a section label
    bad_words = ["guides", "event", "case",
                 "diversity", "mission", "hub", "study"
                 "articles", "blog", "contact", 
                 "introvert", "extrovert", "career"
                 "information", "follow", "related", 
                 "path"]
    if any(w in text.lower() for w in bad_words):
        return False

    return True

    # reject headings that look like full sentences
    if lower.count(" ") > 5:
        return False

def scrape_jobs_from_url(url: str) -> list[str]:
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    jobs = []
    for tag in soup.find_all(["h3"]):
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
    url = "https://www.multiverse.io/en-GB/blog/best-jobs-for-introverts"
    jobs = scrape_jobs_from_url(url)

    print("Jobs found:")
    for j in jobs:
        print("-", j)