import pandas
import pickle

import sys
sys.setrecursionlimit(3000) # the reviewer and submission lists are deeply linked. this lets pickle work

def save_rev_sublist(sublist,
                    revlist,
                    subpickle='/home/gil/Dropbox/scipy/2018/sublist.pickle',
                    revpickle='/home/gil/Dropbox/scipy/2018/revlist.pickle',):
    with open(subpickle, 'wb') as f:
        pickle.dump(sublist, f)

    with open(revpickle, 'wb') as f:
        pickle.dump(revlist, f)


def load_rev_sublist(subpickle='/home/gil/Dropbox/scipy/2018/sublist.pickle',
                     revpickle='/home/gil/Dropbox/scipy/2018/revlist.pickle'):
#    with open(subpickle, 'rb') as f:
#        sublist = pickle.load(f)

    with open(revpickle, 'rb') as f:
        revlist = pickle.load(f)

    # something got corrupted, reconstruct
    sublist = []
    for rev in revlist:
        try:
            for sub in rev.to_review:
                if not sub in sublist:
                    sublist.append(sub)
        except:
            pass

    revdict = {**{rev.name: rev for rev in revlist}, **{rev.email: rev for rev in revlist}}
    subdict = {**{sub.title: sub for sub in sublist}, **{sub.subid: sub for sub in sublist}}

    return revlist, sublist, revdict, subdict

