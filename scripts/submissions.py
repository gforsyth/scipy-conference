import re
import pandas

APP_REGEX = re.compile(r'Applicant \d: (\w*)')
EMAIL_REGEX = re.compile(r'[\w\.-]+@[\w\.-]+')

class Submission(object):
    def __init__(self, authors, emails, title, domain):
        self.authors = authors
        self.emails = emails
        self.title = title
        self.domain = domain

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

def populate_submissions(subs):
    sublist = []
    for sub in subs.itertuples():
        _, title, domain, emails, first_names, last_names = sub
        names = list(zip(re.findall(APP_REGEX, first_names),
                         re.findall(APP_REGEX, last_names)))
        names = [' '.join(name) for name in names]
        emails = re.findall(EMAIL_REGEX, emails)
        sublist.append(Submission(names, emails, title, domain))

    return sublist




