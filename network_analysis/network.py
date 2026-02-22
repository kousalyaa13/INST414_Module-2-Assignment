import pandas as pd

# read input file
df = pd.read_csv("cleanup\\job_edges_clean.csv")

# choose which job column to use
job_col = "job_canonical"

# keep only needed columns
df = df[["personality", job_col]].dropna()
df = df.rename(columns={job_col: "job"})
#print(df)

# aggregate weights (how many times the edge appears)
edges = (
    df.groupby(["personality", "job"])
      .size()
      .reset_index(name="weight")
      .rename(columns={"personality": "source", "job": "target"})
)

# nodes: personality nodes + job nodes
personality_nodes = pd.DataFrame({
    "id": sorted(edges["source"].unique()),
    "label": sorted(edges["source"].unique()),
    "type": "personality"
})

job_nodes = pd.DataFrame({
    "id": sorted(edges["target"].unique()),
    "label": sorted(edges["target"].unique()),
    "type": "job"
})

nodes = pd.concat([personality_nodes, job_nodes], ignore_index=True)

# write gephi files
nodes.to_csv("network_analysis\\gephi_nodes.csv", index=False)
edges.to_csv("network_analysis\\gephi_edges.csv", index=False)

print("Saved:")
print(" - cleanup/gephi_nodes.csv")
print(" - cleanup/gephi_edges.csv")
print(f"Nodes: {len(nodes)}")
print(f"Edges: {len(edges)}")