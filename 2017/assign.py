import itertools

from reviewers import get_reviewer_info, get_domain_order, populate_reviewers, get_reviewer_pools
from submissions import get_submissions, get_submission_pools, populate_submissions

def assign_paper(reviewer, submission, assign_count):
    """Assigns a paper to a reviewer after checking for conflicts

    Check that:
    - Reviewer is not a submitter
    - Reviewer is not already reviewing this paper
    - That reviewer isn't already assigned papers > assign_count
    """
    if not hasattr(reviewer, 'to_review'):
        reviewer.to_review = []
    if not hasattr(submission, 'reviewers'):
        submission.reviewers = []

    if reviewer.email in submission.emails:
        return False
    elif submission in reviewer.to_review:
        return False
    elif submission.subid in reviewer.cois:
        return False
    elif len(reviewer.to_review) > assign_count:
        return False
    else:
        reviewer.to_review.append(submission)
        submission.reviewers.append(reviewer)
        return True

def do_single_assign(revlist, sub):
    reviewers = [rev for rev in revlist if sub.domain in rev.domains]
    reviewer_cycle = itertools.cycle(reviewers)
    do_assign(reviewers, reviewer_cycle, sub)

def do_assign(reviewers, reviewers_cycle, sub):
    """
    Assigns a reviewer to the submission `sub`

    Arguments
    ---------
    reviewers : list
        reviewers in domain ``domain``
    reviewers_cycle : itertools cycle
        reviewers cycle in domain ``domain``
    sub : Submission
        submission to be assigned
    """

    domain = sub.domain
    reviewer = next(reviewers_cycle)
    assign_count = get_assign_count(reviewers)

    bump_me = 0
    while not assign_paper(reviewer, sub, assign_count):
        reviewer = next(reviewers_cycle)
        assign_count = get_assign_count(reviewers)
        if bump_me > len(reviewers):
            assign_count += 1
        bump_me += 1

def get_assign_count(reviewers):
    """
    Figure out max # of papers one person should have to review at the moment

    Arguments
    ---------
    reviewers : list
        reviewers in a given domain

    Returns
    -------
    assign_count : int
        max # of papers to assign to one person
    """
    try:
        min_count = min([len(rev.to_review) for rev in
                        reviewers if hasattr(rev, 'to_review')])
        max_count = max([len(rev.to_review) for rev in
                        reviewers if hasattr(rev, 'to_review')])
    except ValueError:
        min_count, max_count = 0, 0
    return min_count + 1 if min_count == max_count else min_count



