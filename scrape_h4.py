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

    # basic length filter
    if len(text) < 3 or len(text) > 60:
        return False

    # remove headings we know are junk
    if text in BAD_HEADINGS:
        return False

    # drop anything that sounds like a section label
    bad_words = ["articles", "contact", "information", "follow", "related", "path"]
    if any(w in text.lower() for w in bad_words):
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

    print("Jobs found:")
    for j in jobs:
        print("-", j)


# if __name__ == "__main__":

#     sources = pd.read_csv("sources.csv")
#     #print(sources.columns)

#     all_rows = []

#     for _, row in sources.iterrows():
#         url = row["url"]
#         label = row["label"]

#         print(f"\nScraping: {url}")

#         try:
#             jobs = scrape_jobs_from_url(url)

#             for job in jobs:
#                 all_rows.append({
#                     "personality": label,
#                     "job": job,
#                     "source": urlparse(url).netloc
#                 })

#             print(f"  Found {len(jobs)} jobs")

#         except Exception as e:
#             print(f"  Error scraping {url}: {e}")

#         time.sleep(1.5)  # be polite

#     # Create dataframe
#     df = pd.DataFrame(all_rows)

#     # Save raw job edges
#     df.to_csv("job_edges_raw.csv", index=False)

#     print("\nSaved to job_edges_raw.csv")