import itertools

from ldassn import load_rev_sublist, save_rev_sublist
from assign import do_assign

def reassign(sub, reviewer, revlist):
    """Pop the given reviewer from the submission, add the subid to the reviewer's
    COI list and then reassign the submission to someone in the appropriate
    domain pool
    """
    sub.reviewers.remove(reviewer)
    reviewer.cois.append(sub.subid)
    reviewer.to_review.remove(sub)

    revpool = [rev for rev in revlist if sub.domain in rev.domains]
    revcycle = itertools.cycle(revpool)

    do_assign(revpool, revcycle, sub)
