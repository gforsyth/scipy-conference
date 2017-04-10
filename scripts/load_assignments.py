import pandas
import pickle
import pickle

import sys
sys.setrecursionlimit(3000) # the reviewer and submission lists are deeply linked. this lets pickle work

def save_rev_sublist(sublist,
                    revlist,
                    subpickle='/home/gil/Dropbox/sublist.pickle',
                    revpickle='/home/gil/Dropbox/revlist.pickle',):
    with open(subpickle, 'wb') as f:
        pickle.dump(sublist, f)

    with open(revpickle, 'wb') as f:
        pickle.dump(revlist, f)


def load_rev_sublist(subpickle='/home/gil/Dropbox/sublist.pickle',
                     revpickle='/home/gil/Dropbox/revlist.pickle',
                     assign_csv='scipy2017.reviewer.assignments - assignments.csv'):
    with open(subpickle, 'rb') as f:
        sublist = pickle.load(f)

    with open(revpickle, 'rb') as f:
        revlist = pickle.load(f)

    assignments = pandas.read_csv(assign_csv, usecols=(0, 2, 3, 4, 5, 6, 7, 8))

    for sub in sublist:
        sub.reviewers = []

    for rev in revlist:
        rev.to_review = []
        rev.email = rev.email.strip()

    for _, subid, title, rev1, rev1em, rev2, rev2em, rev3, rev3em in assignments.itertuples():
        sub = [sub for sub in sublist if sub.subid == subid][0]
        for rev in revlist:
            if rev.email in [rev1em, rev2em, rev3em]:
                rev.to_review.append(sub)
                sub.reviewers.append(rev)

    revdict = {**{rev.name: rev for rev in revlist}, **{rev.email: rev for rev in revlist}}
    subdict = {**{sub.title: sub for sub in sublist}, **{sub.subid: sub for sub in sublist}}

    return revlist, sublist, revdict, subdict

