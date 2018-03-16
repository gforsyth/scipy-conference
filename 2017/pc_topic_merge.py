"""Some people will sign up for PC through easychair only and we won't have topic areas that they want to review in.  Default them to general"""

import pandas as pd

# read in PC from easychair
pc = pd.read_excel('SciPy 2018_data_2018-02-20.xlsx', sheet_name='Program committee')
# read in PC from signup sheet
pc_csv = pd.read_csv('SciPy 2018 Program Committee Interest Form (Responses).csv')
# rename horrible column
pc_csv['domain'] = pc_csv['Domain you volunteer to review (check all that apply)']

topics = []
for _, _, _, _, _, email, *rest in pc.itertuples():
    if any(pc_csv.Email == email):
        topics.append(pc_csv[pc_csv.Email == email]['domain'].values)
    else:
        topics.append('None')
topics

pc['domain'] = topics
# drop chairs and superchairs from df
pc = pc[pc.role == 'PC member']

# join first, last names
pc['name'] = pc['first name'] + ' ' + pc['last name']
