import pandas as pd

from ldassn import load_rev_sublist
from incomplete import domain_pool_subs

revlist, sublist, revdict, subdict = load_rev_sublist()

# need to filter out posters
df = pd.read_excel('/home/gil/Dropbox/scipy/2018/program_committee/SciPy 2018_data_2018-03-15.xlsx', sheet_name='Submissions')
df['subtype'] = df['form fields'].apply(lambda x: x.split('\n')[0].split(' ')[-1])
for sub in sublist:
    sub.subtype = df[df['#'] == sub.subid]['subtype'].values[0]

sublist = [sub for sub in sublist if sub.subtype == 'Talk']

domain_pool = domain_pool_subs(sublist)
total_subs = len(sublist)
total_talks = 60

talk_slots = dict()
for domain, subs in domain_pool.items():
    talk_slots[domain] = round(len(subs) / total_subs * total_talks)
    print(f'{domain}: {talk_slots[domain]} of {len(subs)}')

print(f'Total assigned: {sum(talk_slots.values())}')
