import itertools


def assign_paper(reviewer, submission, assign_count):
    """Assigns a paper to a reviewer after checking for conflicts

    Check that:
    - Reviewer is not a submitter
    - Reviewer is not already reviewing this paper
    - That reviewer isn't already assigned papers > assign_count
    """
    reviewer.assign_attempts += 1

    if reviewer.email in submission.emails:
        reviewer.not_assigned_reason[submission.subid] = "is_submitter"
        return False
    elif submission in reviewer.to_review:
        reviewer.not_assigned_reason[submission.subid] = "already_assigned"
        return False
    elif submission.subid in reviewer.cois:
        reviewer.not_assigned_reason[submission.subid] = "COI"
        return False
    elif len(reviewer.to_review) > assign_count:
        reviewer.not_assigned_reason[submission.subid] = "too_many_assigned"
        return False
    else:
        reviewer.to_review.append(submission)
        submission.reviewers.append(reviewer)
        return True


def do_single_assign(revlist, sub):
    reviewers = [rev for rev in revlist if sub.domain in rev.domains]
    reviewer_cycle = itertools.cycle(reviewers)
    do_assign(reviewers, reviewer_cycle, sub)


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

    reviewer = next(reviewers_cycle)
    assign_count = get_assign_count(reviewers)

    # possible to deadlock if reviewer has fewer
    # submissions to review but can't be assigned because of COI
    # if we cycle through everyone, then nudge up the assign count
    nudge = 0
    count = 0
    while not assign_paper(reviewer, sub, assign_count):
        count += 1
        if count > len(reviewers):
            nudge += 1
            count = 0
        reviewer = next(reviewers_cycle)
        assign_count = get_assign_count(reviewers) + nudge


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
        min_count = min([len(rev.to_review) for rev in reviewers])
        max_count = max([len(rev.to_review) for rev in reviewers])
    except ValueError:
        min_count, max_count = 0, 0

    return min_count + 1 if min_count == max_count else min_count
