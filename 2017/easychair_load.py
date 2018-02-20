import pandas as pd

# columns needed from submissions subsheet
subs_cols = ['#', 'track #', 'title']

# load in submission and topics worksheet
subs = pd.read_excel('SciPy 2018_data_2018-02-20.xlsx', sheet_name='Submissions')
topics = pd.read_excel('SciPy 2018_data_2018-02-20.xlsx', sheet_name='Submission topics')
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
