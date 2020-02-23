import re
from collections import defaultdict

import pandas

APP_REGEX = re.compile(r"Applicant \d: (\w*)")
EMAIL_REGEX = re.compile(r"[\w\.-]+@[\w\.-]+")


class Submission(object):
    def __init__(self, authors, emails, title, domain, subid, subtype):
        self.authors = authors
        self.emails = emails
        self.title = title
        self.domain = domain
        self.subid = subid
        self.subtype = subtype
        self.reviewers = []

    def __repr__(self):
        return f"{self.title}, {self.domain}"

    def __str_(self):
        return f"{self.title}"


def get_submission_pools(sublist):
    """Generate pools of submissions for each topic
    """
    submission_pools = defaultdict(list)
    for sub in sublist:
        submission_pools[sub.domain].append(sub)

    return submission_pools


def populate_submissions(subs, authors):
    sublist = []
    for sub in subs.itertuples():
        subid, title, domain, subtype = sub
        names = []
        emails = []
        for auth in authors[authors["submission #"] == subid].itertuples():
            _, _, first, last, email, *rest = auth
            if not isinstance(first, str):
                first = ""
            names.append(" ".join([first, last]))
            emails.append(email)

        sublist.append(Submission(names, emails, title, domain, subid, subtype))

    return sublist
