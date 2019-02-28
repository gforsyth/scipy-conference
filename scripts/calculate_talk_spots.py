import yaml
import pandas as pd

from load_save import load_rev_sublist
from domain import domain_pool_subs

with open("configs/config.yaml") as f:
    config = yaml.load(f)

revlist, sublist, revdict, subdict = load_rev_sublist()

# need to filter out posters
df = pd.read_excel(config["easychair"]["data_file"], sheet_name="Submissions")
"""
Hilariously, there is no column in the export that just says 'Poster' or 'Talk'
So instead we use the `form fields` column which looks like, e.g.

"'(Poster vs. Talk) Talk\n(Short summary of your topic.) Parallelization of array processing..."

where the entirety of the abstract follows.  So to get the submission type,
split on newlines, then split on spaces.
"""
df["subtype"] = df["form fields"].apply(lambda x: x.split("\n")[0].split(" ")[-1])
for sub in sublist:
    sub.subtype = df[df["#"] == sub.subid]["subtype"].values[0]

sublist = [sub for sub in sublist if sub.subtype == "Talk"]

domain_pool = domain_pool_subs(sublist)
total_subs = len(sublist)
total_talks = 60

talk_slots = dict()
for domain, subs in domain_pool.items():
    talk_slots[domain] = round(len(subs) / total_subs * total_talks)
    print(f"{domain}: {talk_slots[domain]} of {len(subs)}")

print(f"Total assigned: {sum(talk_slots.values())}")
