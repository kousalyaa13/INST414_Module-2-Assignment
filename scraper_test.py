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

    # throw out common non-job phrases
    bad_phrases = [
        "what is", "how to", "characteristics", "introvert", "extrovert",
        "skills", "traits", "differences", "begin", "leveraging",
        "building", "contents", "resources", "blog", "events", "case studies",
        "about", "mission", "diversity", "news", "research hub"
    ]
    if any(p in lower for p in bad_phrases):
        return False

    # reject headings that look like full sentences
    if lower.count(" ") > 5:
        return False

    # ✅ accept job-ish words
    job_keywords = [
        "engineer", "developer", "analyst", "scientist", "designer", "manager",
        "writer", "accountant", "consultant", "specialist", "administrator",
        "architect", "technician", "teacher", "nurse", "recruiter"
    ]
    if any(k in lower for k in job_keywords):
        return True

    # allow short title-case roles that don't include keywords (optional)
    # e.g., "Controller", "Criminologist"
    if text.istitle() and lower.count(" ") <= 3:
        return True

    return False

def scrape_jobs_from_url(url: str) -> list[str]:
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    # ✅ focus on the main article area
    container = soup.find("article")
    if container is None:
        container = soup  # fallback if no <article> tag exists

    jobs = []
    for tag in container.find_all(["h2", "h3"]):
        text = tag.get_text(strip=True)
        text = re.sub(r"^\d+[\.\)]\s*", "", text)

        if is_job_heading(text):
            jobs.append(text)

    # de-duplicate
    seen = set()
    out = []
    for j in jobs:
        k = j.lower()
        if k not in seen:
            seen.add(k)
            out.append(j)
    return out


# if __name__ == "__main__":
#     url = "https://blog.steppingblocks.com/15-best-jobs-for-introverts-in-2021"
#     jobs = scrape_jobs_from_url(url)

#     print("Jobs found:")
#     for j in jobs:
#         print("-", j)


if __name__ == "__main__":

    sources = pd.read_csv("sources.csv")
    #print(sources.columns)

    all_rows = []

    for _, row in sources.iterrows():
        url = row["url"]
        label = row["label"]

        print(f"\nScraping: {url}")

        try:
            jobs = scrape_jobs_from_url(url)

            for job in jobs:
                all_rows.append({
                    "personality": label,
                    "job": job,
                    "source": urlparse(url).netloc
                })

            print(f"  Found {len(jobs)} jobs")

        except Exception as e:
            print(f"  Error scraping {url}: {e}")

        time.sleep(1.5)  # be polite

    # Create dataframe
    df = pd.DataFrame(all_rows)

    # Save raw job edges
    df.to_csv("job_edges_raw.csv", index=False)

    print("\nSaved to job_edges_raw.csv")