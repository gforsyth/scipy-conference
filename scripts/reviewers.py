"""Assumes that there is a csv (probably generated from a Google Form) that has
fields like "name", "email" and a list of "domains" in which each submittee is
comfortable reviewing.

"""

import re
import pandas
from collections import namedtuple, Counter

EMAIL_REGEX = re.compile(r"[\w\.-]+@[\w\.-]+")


class Reviewer(object):
    def __init__(self, name, email, domains, rev_number, tutorial, cois=[]):
        self.name = name
        self.email = email
        self.domains = domains
        self.rev_number = rev_number
        self.tutorial = tutorial
        self.cois = cois
        self.to_review = []
        self.assign_attempts = 0
        self.not_assigned_reason = dict()
        self.revid = None

    def __repr__(self):
        return f"{self.name}, {self.email}"

    def __str_(self):
        return f"{self.name}"


def get_domain_order(domains):
    """Return list of all domains of all reviewers

    domains : pandas.Series
      comma delimited string of domains reviewers selected
    """
    count = []
    for domain in domains:
        for i in domain.split("|"):
            count.append(i)
    return Counter(count)


def populate_reviewers(responses):
    """Take a pandas dataframe and return a list of Reviewers created
    from that dataframe.

    Dataframe has columns "name", "email", "domain" where "domain" is a
    comma-separated list
    """
    reviewers = []
    for rev in responses.itertuples():
        if rev.domain == "None":
            domain = ["General"]
        else:
            domain = rev.domain
        reviewers.append(Reviewer(rev.name, rev.email, domain, rev.rev_number, rev.tutorial))

    return reviewers


def domain_count_sort(item):
    """Return number of domains reviewer has.

    Use to sort reviewers in pools by number of other domains checked
    """
    return len(item.domains)


def get_reviewer_pools(count, reviewers):
    """Generate pools of reviewers for each topic

    Members of pool are sorted by number of domains they review in from least
    to most
    """
    reviewer_pools = {}
    for category in count.keys():
        reviewer_pools[category] = [per for per in reviewers if category in per.domains]
        reviewer_pools[category] = sorted(
            reviewer_pools[category], key=domain_count_sort
        )

    return reviewer_pools

