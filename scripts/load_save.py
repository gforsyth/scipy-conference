import pandas
import pickle
import yaml

import sys
sys.setrecursionlimit(3000) # the reviewer and submission lists are deeply linked. this lets pickle work

def save_rev_sublist(sublist,
                     revlist,
                     subpickle=None,
                     revpickle=None,
                     ):
    if not subpickle or not revpickle:
        with open('configs/config.yaml') as f:
            conf = yaml.load(f)

    if not subpickle:
        subpickle = conf['submissions']['pickle']
    if not revpickle:
        revpickle = conf['reviewers']['pickle']

    with open(subpickle, 'wb') as f:
        pickle.dump(sublist, f)

    with open(revpickle, 'wb') as f:
        pickle.dump(revlist, f)


def load_rev_sublist(subpickle=None, revpickle=None):
    if not subpickle or not revpickle:
        with open('configs/config.yaml') as f:
            conf = yaml.load(f)

    if not subpickle:
        subpickle = conf['submissions']['pickle']
    if not revpickle:
        revpickle = conf['reviewers']['pickle']

    with open(subpickle, 'rb') as f:
        sublist = pickle.load(f)

    with open(revpickle, 'rb') as f:
        revlist = pickle.load(f)

    # on deserialization the links between the reviewer objects and the sublist
    # objects is lost, so reconstruct from the reviewer assignments
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

