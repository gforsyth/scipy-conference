from ldassn import load_rev_sublist, save_rev_sublist
import pandas

def get_comp_reviewers(csv='ReviewerListReport_220975.csv'):
    revlist, sublist = load_filter_reviews(csv)
    top_reviewers = [rev for rev in revlist if len(rev.to_review) == 0]

    return top_reviewers

def populate_domain_pool(revlist, sublist):

    delinquents = [rev for rev in revlist if len(rev.to_review) > 0]
    needy_subs = [sub for sub in sublist if len(sub.reviewers) > 0]

    domains = set()
    for sub in needy_subs:
        domains.add(sub.domain)

    domain_pool = dict()
    for domain in domains:
        domain_pool[domain] = []

    for sub in needy_subs:
        for rev in sub.reviewers:
            if rev not in domain_pool[sub.domain]:
                domain_pool[sub.domain].append(rev)

    return domain_pool

def load_filter_reviews(csv='ReviewerListReport_220975.csv'):
    revlist, sublist, revdict, subdict = load_rev_sublist()
    report = pandas.read_csv(csv)
    report = report[report['Submission Group'] == 'Conference Talks and Posters']

    bad_keys = []
    bad_sub = []
    for rev in report.itertuples():
        sub = subdict[rev.Title]
        if rev._2 == 'Complete':
            try:
                reviewer = revdict[rev._1]
                reviewer.to_review.remove(sub)
                sub.reviewers.remove(reviewer)
            except KeyError:
                bad_keys.append(rev._1)
            except ValueError:
                bad_sub.append(sub)
    print(bad_keys)
    print(bad_sub)

    return revlist, sublist
