"""
SciPy + EasyChair review assignments

1. Download the files listed under `Files` to the working directory
2. Run `clean_and_assign.py` in IPython

`rev_list` is the list of reviewer objects with contact info and their assignments
`sublist` is the list of submission objects with contact info and their reviewers
"""

import yaml
import itertools
import numpy
import pandas as pd

from reviewers import get_domain_order, populate_reviewers, get_reviewer_pools
from submissions import get_submission_pools, populate_submissions
from assign import do_assign
from load_save import save_rev_sublist

############################################################
### Files
############################################################
with open("configs/config2019.yaml") as f:
    config = yaml.load(f)

# Download from EasyChair
# Premium -> Conference Data Download -> Excel
easy_chair_data = config["easychair"]["data_file"]
# Download from google form spreadsheet
reviewer_signup = config["reviewers"]["signup_csv"]

REVIEWERS_PER_SUBMISSION = config["reviewers"]["submissions"]
TRACK_MAP = [
    ("Neuroscience and Cognitive Science", "neuro"),
    ("Image Processing", "image"),
    ("Open Source Communities", "osc"),
    ("Earth, Ocean, Geo and Atmospheric Science", "earthgeo"),
    ("Science Communication through Visualization", "viz"),
    ("Data Driven Discoveries", "dsml"),
]

############################################################
### Reviewers
############################################################

# read in PC from easychair
pc = pd.read_excel(easy_chair_data, sheet_name="Program committee")
# rename column
pc["rev_number"] = pc["#"]
# read in PC from signup sheet
# signup csv form has three columns (that we care about)
# name, email, domain
pc_csv = pd.read_csv(reviewer_signup, usecols=["name", "email", "domain"])


# strip and lower everything
for col in pc_csv.select_dtypes("object"):
    pc_csv[col] = pc_csv[col].str.strip()
    pc_csv[col] = pc_csv[col].str.lower()
for col in pc.select_dtypes("object"):
    pc[col] = pc[col].str.strip()
    pc[col] = pc[col].str.lower()

pc = pd.merge(pc, pc_csv, how="left", on="email")

# drop chairs and superchairs from df
pc = pc[pc.role == "pc member"]
# drop reviewers without any specified field
pc = pc[~(pc.domain == "none")]

# join first, last names
pc["name"] = pc["first name"] + " " + pc["last name"]

# lower all domain/topics
pc.domain = pc.domain.str.lower()

# remove any reviewers without domain areas
pc.dropna(subset=["domain"], inplace=True)

############################################################
### Submissions
############################################################

# load in submission and topics worksheet
subs = pd.read_excel(easy_chair_data, sheet_name="Submissions")
topics = pd.read_excel(
    easy_chair_data,
    sheet_name="Submission field values",
    usecols=["field #", "submission #", "value"],
)

pres_type = topics[topics["field #"] == 1]  # corresponds to talk vs poster
topics = topics[topics["field #"] == 2]  # corresponds to track name

pres_type.drop(columns="field #", inplace=True)
topics.drop(columns="field #", inplace=True)


# set index to submission #
subs.set_index("#", inplace=True)
topics.set_index("submission #", inplace=True)
pres_type.set_index("submission #", inplace=True)

# join topics to subs
subs = subs.join(topics, lsuffix="subs")

# strip out plenary session entries
subs = subs[~subs.value.str.contains("SciPy Tools Mini Talk")]

# replace and rename all topics with shortcodes
subs["topic"] = subs.value

for old, new in TRACK_MAP:
    subs.topic = subs.topic.str.replace(old, new)

subs.topic = subs.topic.str.lower()


############################################################
### Author list
############################################################

authors = pd.read_excel(easy_chair_data, sheet_name="Authors")

############################################################
### Load and assign
############################################################

responses = pc
domain_count = get_domain_order(responses.domain)
rev_list = populate_reviewers(responses)

### Load in CoIs from EasyChair
conflicts = pd.read_excel(easy_chair_data, sheet_name="Conflicts of interests")
for rev in rev_list:
    rev.cois = list(
        conflicts[conflicts["member #"] == rev.rev_number]["submission #"].values
    )


reviewer_pools = get_reviewer_pools(domain_count, rev_list)

sublist = populate_submissions(subs[["title", "topic"]], authors)
sub_count = subs.topic.value_counts()
submission_pools = get_submission_pools(sub_count, sublist)

# start assigning to areas with fewest number of reviewers first
for domain in domain_count.keys()[::-1]:
    submissions = iter(submission_pools.get(domain, "") * REVIEWERS_PER_SUBMISSION)
    reviewers = reviewer_pools[domain]
    reviewers_cycle = itertools.cycle(reviewers)

    for sub in submissions:
        do_assign(reviewers, reviewers_cycle, sub)

    print(f"Assignment of {domain} papers complete")


############################################################
### Load in _different_ reviewer id numbers because yay relational databases
### Need to download `reviewer.csv` from easychair "Assignment -> Download in csv"
############################################################

names = pd.read_csv(
    config["reviewers"]["easychair_csv"], names=["id", "name", "email", "role"]
)

names.name = names.name.str.lower()
names.name = names.name.str.strip()
names.email = names.email.str.lower()
names.email = names.email.str.strip()

for rev in rev_list:
    if rev.email in names.email.values:
        rev.revid = names[names.email == rev.email]["id"].values[0]
    else:
        rev_list.remove(rev)
        print(f"{rev} removed from reviewer list (no match on easychair)")

revcount = [len(rev.to_review) for rev in rev_list]

print(numpy.min(revcount))
print(numpy.max(revcount))
print(numpy.std(revcount))


def write_csv_assigment(revlist):
    with open(config["easychair"]["assignment_output"], "w") as f:
        for rev in revlist:
            if hasattr(rev, "to_review"):
                for sub in rev.to_review:
                    f.write(f"{rev.revid},{sub.subid}\n")

print("Saving reviewer list and submission list to pickles (sorry world)")
save_rev_sublist(sublist, rev_list)
print(f"Saving assignment csv to {config['easychair']['assignment_output']}")
write_csv_assigment(rev_list)
print("Finished")
