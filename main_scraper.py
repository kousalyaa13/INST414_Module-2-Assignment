import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import time
from urllib.parse import urlparse
import os

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Educational Network Project)"
}

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
    "Track your credit score with SoFi"
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
    sources = pd.read_csv("sources.csv")
    all_rows = []

    for _, row in sources.iterrows():
        url = str(row.get("url", "")).strip()
        label = str(row.get("label", "")).strip()
        tag_name = str(row.get("tag", "")).strip()

        if not url:
            continue

        print(f"\nScraping: {url} (tag={tag_name})")

        try:
            jobs = scrape_jobs_from_url(url, tag_name)

            for job in jobs:
                all_rows.append({
                    "personality": label,
                    "job": job,
                    "source": urlparse(url).netloc
                })

            print(f"  Found {len(jobs)} jobs")

        except Exception as e:
            print(f"  Error scraping {url}: {e}")

        time.sleep(1.5)

    output_file = "job_edges_raw.csv"

# after loop: build dataframe
new_df = pd.DataFrame(all_rows).drop_duplicates()

if os.path.exists(output_file):
    existing_df = pd.read_csv(output_file, usecols=["personality", "job", "source"])

    # build a key to detect duplicates
    existing_keys = set(
        existing_df["personality"].astype(str).str.lower().str.strip()
        + "||" +
        existing_df["job"].astype(str).str.lower().str.strip()
        + "||" +
        existing_df["source"].astype(str).str.lower().str.strip()
    )

    new_keys = (
        new_df["personality"].astype(str).str.lower().str.strip()
        + "||" +
        new_df["job"].astype(str).str.lower().str.strip()
        + "||" +
        new_df["source"].astype(str).str.lower().str.strip()
    )

    to_add = new_df[~new_keys.isin(existing_keys)]

    if len(to_add) > 0:
        to_add.to_csv(output_file, mode="a", header=False, index=False)
        print(f"\nAppended {len(to_add)} new rows to job_edges_raw.csv")
    else:
        print("\nNo new rows to append (all duplicates).")

else:
    new_df.to_csv(output_file, index=False)
    print("\nCreated job_edges_raw.csv")