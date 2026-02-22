import pandas as pd


CANONICAL_MAP = {
    "call centre operator": "call center operator",
    "counsellor": "counselor",
    "hairstylist": "hair stylist",
    "freelance":  "freelancer",
    "graphic design": "graphic designer",
    "hair stylist": "hairstylist",
    "health services manager": "health service manager",
    "human resources manager": "human resource manager",
    "physical therapists": "physical therapist",
    "psychologists": "psychologist",
    "writers": "writer",
    "data analysis": "data analyst",
    "journalism": "journalist",
    "social work": "social worker",
    "web development": "web developer",
    "entrepreneurship": "entrepreneur",
    "customer success representative": "customer service representative",
    "content creation": "content creator",
    "freeland writer" : "freelance writer",
    "transcription" : "transcriptionist",
    "hospitality management": "hospitality manager",
    "hairdresser": "hairstyler",
    "customer service": "customer service representative",
    "customer service rep": "customer service representative"
}

# read the data into a dataframe
df = pd.read_csv("cleanup\\job_edges_fuzzy_detection.csv")

df["job_clean"] = df["job"].str.lower().str.strip()

df["job_canonical"] = df["job_clean"].replace(CANONICAL_MAP)

df.to_csv("cleanup\\job_edges_clean.csv", index=False)

print("Saved cleaned file.")