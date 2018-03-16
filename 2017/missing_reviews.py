import pandas as pd
from ldassn import load_rev_sublist

def update_rev_sub_lists(revlist, sublist, revdict, subdict):
    data = pd.read_excel('/home/gil/Dropbox/scipy/2018/program_committee/SciPy 2018_data_2018-03-15.xlsx', sheet_name='Reviews')


    data = data[['submission #', 'member #', 'member name']]
    for _, subid, revid, name in data.itertuples():
        try:
            revdict[name].to_review = [sub for sub in revdict[name].to_review if sub.subid != subid]
        except KeyError:
            pass

    revlist = [rev for rev in revlist if hasattr(rev, 'to_review')]
    for sub in sublist:
        keeprev = []
        for rev in sub.reviewers:
            if sub in rev.to_review:
                keeprev.append(rev)
        sub.reviewers = keeprev

    domains = set()
    for rev in revlist:
        domains = domains.union(rev.domains.split(', '))

    reviewer_pools = {}
    for category in domains:
        reviewer_pools[category] = [rev for rev in revlist if category in rev.domains]

    missing_reviews = 0
    for rev in revlist:
        if hasattr(rev, 'to_review'):
            missing_reviews += len(rev.to_review)

    total_reviews = len(sublist) * 6
    comp_reviews = total_reviews - missing_reviews

    print(f'{comp_reviews} completed out of {total_reviews} or {100 * comp_reviews / total_reviews:.2f}%\n')

    done = [rev.name for rev in revlist if len(rev.to_review) == 0]
    print(f'{len(done)} reviewers have finished all their reviews: ')
    print('\n'.join(done))

#    for cat in domains:
#        print("{:-^80}".format(cat))
#        pool = reviewer_pools[cat]
#        for rev in pool:
#            s = ''
#            for sub in rev.to_review:
#                if sub.domain == cat:
#                    s += f'{sub.subid}, {sub.title}\n'
#            if s:
#                print(rev.name, rev.email)
#                print(s)

    return revlist, sublist, revdict, subdict



if __name__ == '__main__':
    revlist, sublist, revdict, subdict = load_rev_sublist()
    update_rev_sub_lists(revlist, sublist, revdict, subdict)
