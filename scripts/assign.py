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

    while not assign_paper(reviewer, sub, assign_count):
        reviewer = next(reviewers_cycle)
        assign_count = get_assign_count(reviewers)


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



review_kwargs = {'csvfile': 'responses.csv',
                 'columns': ['Name:',
                             'Email',
                             'Domain you volunteer to review (check all that apply)'],
                 'rename_dict': {'Name:': 'name',
                                 'Email': 'email',
                                 'Domain you volunteer to review (check all that apply)': 'domain'},
                'dup_drop': 'email'}


subs_kwargs = {'csvfile': 'submissions.csv',
               'columns': ['Applicant-First Name',
                           'Applicant-Last Name',
                           'Applicant-E-mail Address',
                           'Submission-Initial Stage-Title',
                           'Submission-Initial Stage-Submission Subgroup',
                           'Submission ID',
                            ]
              }

responses = get_reviewer_info(**review_kwargs)
# Fix for domains with commas in them
domain_count = get_domain_order(responses.domain)
rev_list = populate_reviewers(responses)
reviewer_pools = get_reviewer_pools(domain_count, rev_list)

subs, sub_count = get_submissions(**subs_kwargs)
sublist = populate_submissions(subs)
submission_pools = get_submission_pools(sub_count, sublist)


REVIEWERS_PER_SUBMISSION = 3

# start assigning to areas with fewest number of reviewers first
for domain in domain_count.keys()[::-1]:
    submissions = iter(submission_pools.get(domain, '') * REVIEWERS_PER_SUBMISSION)
    reviewers = reviewer_pools[domain]
    reviewers_cycle = itertools.cycle(reviewers)

    for sub in submissions:
        do_assign(reviewers, reviewers_cycle, sub)

    print(f'Assignment of {domain} papers complete')


assert all([len(sub.reviewers) == 3 for sub in sublist])
assert all([len(rev.to_review) < 5 for rev in rev_list])
