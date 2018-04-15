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

############################################################
### Files
############################################################
with open('configs/config.yaml') as f:
    config = yaml.load(f)

# Download from EasyChair
# Premium -> Conference Data Download -> Excel
easy_chair_data = config['easychair']['data_file']
# Download from google form spreadsheet
reviewer_signup = config['reviewers']['signup_csv']


############################################################
### Reviewers
############################################################

# read in PC from easychair
pc = pd.read_excel(easy_chair_data, sheet_name='Program committee')
# read in PC from signup sheet
pc_csv = pd.read_csv(reviewer_signup)
# rename horrible column
pc_csv['domain'] = pc_csv['Domain you volunteer to review (check all that apply)']
# strip whitespace
pc_csv.Email = pc_csv.Email.str.strip()
pc_csv.Email = pc_csv.Email.str.lower()
# Drop reviewers who only checked 'library science' (bummer)
pc_csv = pc_csv[~(pc_csv.domain == 'Library Science and Digital Humanities')]


topics = []
for _, _, _, _, _, email, *rest in pc.itertuples():
    email = email.strip().lower()
    if any(pc_csv.Email == email):
        topics.append(pc_csv[pc_csv.Email == email]['domain'].values[0])
    else:
        topics.append('none')

pc['domain'] = topics
# drop chairs and superchairs from df
pc = pc[pc.role == 'PC member']

# drop reviewers without any specified field
pc= pc[~(pc.domain == 'none')]

# join first, last names
pc['name'] = pc['first name'] + ' ' + pc['last name']

# lower all domain/topics
pc.domain = pc.domain.str.lower()

# rename earth, geo, ocean because of an annoying comma
pc.domain = pc.domain.str.replace('earth,', 'earth')

############################################################
### Submissions
############################################################

# columns needed from submissions subsheet
subs_cols = ['#', 'track #', 'title']

# load in submission and topics worksheet
subs = pd.read_excel(easy_chair_data, sheet_name='Submissions')
topics = pd.read_excel(easy_chair_data, sheet_name='Submission topics')
# temp fix to remove duplicate topics
topics.drop_duplicates(subset=['submission #'], inplace=True)

# filter columns
subs = subs[subs_cols]

# filter out tutorials
subs = subs[subs['track #'] == 1]

# set index to submission #
subs.set_index('#', inplace=True)
topics.set_index('submission #', inplace=True)

# join topics to subs
subs = subs.join(topics, lsuffix='subs')

# strip out plenary session entries
subs = subs[~subs.topic.str.contains('SciPy Tools')]

# lower all domain/topics
subs.topic = subs.topic.str.lower()

# rename earth, geo, ocean because of an annoying comma
subs.topic = subs.topic.str.replace('earth,', 'earth')


############################################################
### Author list
############################################################

authors = pd.read_excel('SciPy 2018_data_2018-02-20.xlsx', sheet_name='Authors')

############################################################
### Load and assign
############################################################

responses = pc
domain_count = get_domain_order(responses.domain)
rev_list = populate_reviewers(responses)

### Load in CoIs from EasyChair
conflicts = pd.read_excel(easy_chair_data, sheet_name='Conflicts of interests')
for rev in rev_list:
    rev.cois = list(conflicts[conflicts['member name'] == rev.name]['submission #'].values)


reviewer_pools = get_reviewer_pools(domain_count, rev_list)

sublist = populate_submissions(subs, authors)
sub_count = subs.topic.value_counts()
submission_pools = get_submission_pools(sub_count, sublist)

REVIEWERS_PER_SUBMISSION = 6

# start assigning to areas with fewest number of reviewers first
for domain in domain_count.keys()[::-1]:
    submissions = iter(submission_pools.get(domain, '') * REVIEWERS_PER_SUBMISSION)
    reviewers = reviewer_pools[domain]
    reviewers_cycle = itertools.cycle(reviewers)

    for sub in submissions:
        do_assign(reviewers, reviewers_cycle, sub)

    print(f'Assignment of {domain} papers complete')


#    assert all([len(sub.reviewers) == 6 for sub in sublist])

############################################################
### Load in _different_ reviewer id numbers because yay relational databases
### Need to download `reviewer.csv` from easychair "Assignment -> Download in csv"
############################################################

names = pd.read_csv('reviewer.csv', names=['id', 'name', 'email', 'role'])
for rev in rev_list:
    rev.revid = names[names.name == rev.name]['id'].values[0]

revcount = [len(rev.to_review) for rev in rev_list]

print(numpy.min(revcount))
print(numpy.max(revcount))
print(numpy.std(revcount))

def write_csv_assigment(revlist):
    with open('reviewer_assignments.csv', 'w') as f:
        for rev in revlist:
            if hasattr(rev, 'to_review'):
                for sub in rev.to_review:
                    f.write(f'{rev.revid},{sub.subid}\n')
