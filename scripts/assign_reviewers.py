"""Assumes that there is a csv (probably generated from a Google Form) that has
fields like "name", "email" and a list of "domains" in which each submittee is
comfortable reviewing.

"""

import pandas

class Reviewer(object):
    def __init__(self, name, email, domains):
        self.name = name
        self.email = email
        self.domains = domains

    def __repr__(self):
        return f"{self.name}, {self.email}"

    def __str_(self):
        return f"{self.name}"

def get_reviewer_info(csvfile=None, columns=None, rename_dict=None, dup_drop=None):
    """Read csv file selecting given columns and optionally renaming them as
    specified in ``rename_dict``
    """
    responses = pandas.read_csv(csvfile, usecols=columns)

    if rename_dict:
        responses.rename(columns=rename_dict, inplace=True)

    responses.domain.str.split(', ')
    return responses.drop_duplicates(subset=dup_drop)


def get_domain_order(domains):
    """Return list of all domains of all reviewers"""
    count = []
    for domain in domains:
        for i in domain.split(', '):
            count.append(i)
    count = pandas.Series(count).value_counts()
    return count


def populate_reviewers(responses):
    """Take a pandas dataframe and return a list of Reviewers created
    from that dataframe.

    Dataframe has columns "name", "email", "domain" where "domain" is a
    comma-separated list
    """
    reviewers = []
    for rev in responses.itertuples():
        reviewers.append(Reviewer(rev.name,
                                  rev.email,
                                  rev.domain.split(', ')))

    return reviewers

def get_reviewer_pools(count, reviewers):
    reviewer_pools = {}
    for category in count.keys():
        reviewer_pools[category] = [per for per in reviewers if category in per.domains]

    return reviewer_pools

kwargs = {'csvfile': 'responses.csv',
          'columns': ['Name:',
                      'Email',
                      'Domain you volunteer to review (check all that apply)'],
          'rename_dict': {'Name:': 'name',
                          'Email': 'email',
                          'Domain you volunteer to review (check all that apply)': 'domain'},
          'dup_drop': 'email'}


responses = get_reviewer_info(**kwargs)
# Fix for domains with commas in them
count = get_domain_order(responses.domain)
rev = populate_reviewers(responses)
reviewer_pools = get_reviewer_pools(count, rev)
