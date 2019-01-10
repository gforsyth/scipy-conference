import re
import pandas

APP_REGEX = re.compile(r'Applicant \d: (\w*)')
EMAIL_REGEX = re.compile(r'[\w\.-]+@[\w\.-]+')

class Submission(object):
    def __init__(self, authors, emails, title, domain, subid):
        self.authors = authors
        self.emails = emails
        self.title = title
        self.domain = domain
        self.subid = subid
        self.reviewers = []

    def __repr__(self):
        return f"{self.title}, {self.domain}"

    def __str_(self):
        return f"{self.title}"

def get_submissions(csvfile=None, columns=None):
    """Read in the columns from the etouches csv with the info needed
    Likely: Name, email, title, domain
    """
    subs = pandas.read_csv(csvfile, usecols=columns)
    count = subs['Submission-Initial Stage-Submission Subgroup'].value_counts()

    return subs, count

def get_submission_pools(count, sublist):
    """Generate pools of submissions for each topic

    """
    submission_pools = {}
    for category in count.keys():
        submission_pools[category] = [resub for resub in sublist if resub.domain == category]

    return submission_pools

def populate_submissions(subs, authors):
    sublist = []
    for sub in subs.itertuples():
        subid, _, title, domain = sub
        names = []
        emails = []
        for auth in authors[authors['submission #'] == subid].itertuples():
            _, _, first, last, email, *rest = auth
            if not isinstance(first, str):
                first = ''
            names.append(' '.join([first, last]))
            emails.append(email)

        sublist.append(Submission(names, emails, title, domain, subid))

    return sublist




