import pandas as pd
from rapidfuzz import fuzz
import re

df = pd.read_csv(r"cleanup\job_edges_clean.csv")

# pick the best column to compare
if "job_canonical" in df.columns:
    col = "job_canonical"
elif "job_clean" in df.columns:
    col = "job_clean"
else:
    col = "job"

# normalize formatting on the chosen column (just in case)
df["compare"] = (
    df[col]
    .astype(str)
    .str.lower()
    .str.replace(r"[:\-]", "", regex=True)
    .str.replace(r"\s+", " ", regex=True)
    .str.strip()
)

unique_jobs = sorted(df["compare"].dropna().unique())

similar_pairs = []
THRESHOLD = 85

for i in range(len(unique_jobs)):
    for j in range(i + 1, len(unique_jobs)):
        score = fuzz.token_sort_ratio(unique_jobs[i], unique_jobs[j])
        if score >= THRESHOLD:
            similar_pairs.append((unique_jobs[i], unique_jobs[j], score))

# sort most similar first (helps review)
similar_pairs.sort(key=lambda x: x[2], reverse=True)

print(f"Comparing column: {col}")
for a, b, s in similar_pairs:
    print(f"{a}  <-->  {b}   (score={s})")