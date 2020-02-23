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
with open("configs/config2020.yaml") as f:
    config = yaml.load(f)

# Download from EasyChair
# Premium -> Conference Data Download -> Excel
easy_chair_data = config["easychair"]["data_file"]
# Download from google form spreadsheet
reviewer_signup = config["reviewers"]["signup_csv"]

REVIEWERS_PER_TALK = config["reviewers"]["talk_target_reviews"]
REVIEWERS_PER_POSTER = config["reviewers"]["poster_target_reviews"]
# Count of dummy subs to tack on to reviewers who are also reviewing tutorials
# to offset the double-review load
TUTORIAL_REVIEWER_PADDING= config["reviewers"]["tutorial_dummy_sub_count"]

TRACK_MAP = [
    ("Machine Learning and Data Science", "dsml"),
    ("General", "general"),
    ("High Performance Python", "hpp"),
    ("Earth, Ocean, Geo and Atmospheric Science", "earthgeo"),
    ("Biology and Bioinformatics", "bio"),
    ("Astronomy and Astrophysics", "astro"),
    ("Materials Science", "matsci"),
]

############################################################
### Reviewers
############################################################

# read in PC from easychair
progcomm = pd.read_excel(easy_chair_data, sheet_name="Program committee")
# rename column
progcomm["rev_number"] = progcomm["#"]
# read in PROGCOMM from signup sheet
# signup csv form has three columns (that we care about)
# name, email, domain
progcomm_csv = pd.read_csv(reviewer_signup, usecols=["name", "email", "domain", "tutorial"])

# Cast tutorial reviewer column as bool
progcomm_csv.tutorial = progcomm_csv.tutorial.apply(lambda x: True if x == "Yes" else False)


# strip and lower everything
for col in progcomm_csv.select_dtypes("object"):
    progcomm_csv[col] = progcomm_csv[col].str.strip().str.lower()

for col in progcomm.select_dtypes("object"):
    progcomm[col] = progcomm[col].str.strip().str.lower()

progcomm = pd.merge(progcomm, progcomm_csv, how="left", on="email")

# drop chairs and superchairs from df
progcomm = progcomm[progcomm.role == "pc member"]

# join first, last names
progcomm["name"] = progcomm["first name"] + " " + progcomm["last name"]

# lower all domain/topics
progcomm.domain = progcomm.domain.str.lower().str.strip()

# remove any reviewers without domain areas
# TODO: put them in general instead of dropping out right
progcomm.dropna(subset=["domain"], inplace=True)

############################################################
### Submissions
############################################################

# load in submission and topics worksheet
subs = pd.read_excel(easy_chair_data, sheet_name="Submissions")

# set index to submission #
subs.set_index("#", inplace=True)

# extract track and presentation type from "form fields"
subs["track"] = subs["form fields"].str.extract("\(Track\)(.*)\n")
subs["type"] = subs["form fields"].str.extract("\(Talk or Poster\)(.*)\n")

# strip out plenary session entries
subs = subs[~subs.track.str.contains("SciPy Tools")]
# strip out maintainers track
subs = subs[~subs.track.str.contains("Maintainers Track")]

# replace and rename all topics with shortcodes
for old, new in TRACK_MAP:
    subs.track = subs.track.str.replace(old, new)

subs.track = subs.track.str.lower().str.strip()
subs.type = subs.type.str.lower().str.strip()


############################################################
### Author list
############################################################

authors = pd.read_excel(easy_chair_data, sheet_name="Authors")

############################################################
### Load and  maintainers trackassign
############################################################

#progcomm.domain = progcomm.domain.str.split("|")
domain_count = get_domain_order(progcomm.domain)
rev_list = populate_reviewers(progcomm)

### Load in CoIs from EasyChair
conflicts = pd.read_excel(easy_chair_data, sheet_name="Conflicts of interests")
for rev in rev_list:
    rev.cois = list(
        conflicts[conflicts["member #"] == rev.rev_number]["submission #"].values
    )


reviewer_pools = get_reviewer_pools(domain_count, rev_list)

sublist = populate_submissions(subs[["title", "track", "type"]], authors)
sub_count = subs.track.value_counts()
submission_pools = get_submission_pools(sub_count, sublist)


# to offset tutorial reviewer work, add in dummy subs to every reviewer who is also reviewing tutorials
for rev in rev_list:
    if rev.tutorial:
        for i in range(TUTORIAL_REVIEWER_PADDING):
            rev.to_review.append(None)


# start assigning to areas with fewest number of reviewers first
for domain, _ in domain_count.most_common()[::-1]:
    allsubs = submission_pools.get(domain)
    # split up talks and posters (different # of reviewers assigned)
    talksubs = [sub for sub in allsubs if sub.subtype == "talk"]
    postersubs = [sub for sub in allsubs if sub.subtype == "poster"]
    assert len(talksubs) + len(postersubs) == len(allsubs)

    submissions = iter(talksubs * REVIEWERS_PER_TALK)
    reviewers = reviewer_pools[domain]
    reviewers_cycle = itertools.cycle(reviewers)

    for sub in submissions:
        do_assign(reviewers, reviewers_cycle, sub)

    print(f"Assignment of {domain} talks complete")

    submissions = iter(postersubs * REVIEWERS_PER_POSTER)
    reviewers = reviewer_pools[domain]
    reviewers_cycle = itertools.cycle(reviewers)

    for sub in submissions:
        do_assign(reviewers, reviewers_cycle, sub)

    print(f"Assignment of {domain} posters complete")

# Now strip out dummy assignments

for rev in rev_list:
    while None in rev.to_review:
        rev.to_review.remove(None)

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

revcount = [len(rev.to_review) for rev in rev_list if not rev.tutorial]

print(f"Smallest assign count for non-tut reviewers: {numpy.min(revcount)}")
print(f"Largest assign count for non-tut reviewers: {numpy.max(revcount)}")
print(f"Mean assign count for non-tut reviewers: {numpy.mean(revcount)}")

revcount = [len(rev.to_review) for rev in rev_list if rev.tutorial]

print(f"Smallest assign count for tut reviewers: {numpy.min(revcount)}")
print(f"Largest assign count for tut reviewers: {numpy.max(revcount)}")
print(f"Mean assign count for tut reviewers: {numpy.mean(revcount)}")


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
