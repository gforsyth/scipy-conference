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
    elif len(reviewer.to_review) > assign_count:
        return False
    else:
        reviewer.to_review.append(submission)
        submission.reviewers.append(reviewer)
        return True

review_kwargs = {'csvfile': 'responses.csv',
                 'columns': ['Name:',
                             'Email',
                             'Domain you volunteer to review (check all that apply)'],
                 'rename_dict': {'Name:': 'name',
                                 'Email': 'email',
                                 'Domain you volunteer to review (check all that apply)': 'domain'},
                'dup_drop': 'email'}


responses = get_reviewer_info(**review_kwargs)
# Fix for domains with commas in them
domain_count = get_domain_order(responses.domain)
rev_list = populate_reviewers(responses)
reviewer_pools = get_reviewer_pools(domain_count, rev_list)

subs_kwargs = {'csvfile': 'submissions.csv',
               'columns': ['Applicant-First Name',
                           'Applicant-Last Name',
                           'Applicant-E-mail Address',
                           'Submission-Initial Stage-Title',
                           'Submission-Initial Stage-Submission Subgroup',
                            ]
              }

subs, sub_count = get_submissions(**subs_kwargs)
sublist = populate_submissions(subs)
submission_pools = get_submission_pools(sub_count, sublist)


# start assigning to areas with fewest number of reviewers first
for domain in domain_count.keys()[::-1]:
    reviewers = itertools.cycle(reviewer_pools[domain])
    # run each submission 3 times
    submissions = iter(submission_pools.get(domain, '') * 3)

    assign_count = 0
    for sub in submissions:
        # If we run out of reviewers reload the list and pop the submission to
        # the back of the queue
        reviewer = next(reviewers)

        if not hasattr(reviewer, 'to_review'):
            reviewer.to_review = []
        if not hasattr(sub, 'reviewers'):
            sub.reviewers = []
        if not assign_paper(reviewer, sub, assign_count):
            submissions = itertools.chain(submissions, (sub))

        assign_count = max([len(rev.to_review) for rev in
                            reviewer_pools[domain] if hasattr(rev, 'to_review')])

    print(f'Assignment of {domain} papers complete')


assert all([len(sub.reviewers) == 3 for sub in sublist])
