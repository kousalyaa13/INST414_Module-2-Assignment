#web scraping\job_edges_raw.csv

from rapidfuzz import fuzz, process

# Simple ratio calculation
ratio = fuzz.ratio("this is a test", "this is a test!")

# Finding the best match in a list
choices = ["Atlanta Falcons", "New York Jets", "New York Giants", "Dallas Cowboys"]
best_match = process.extractOne("new york jets", choices)
