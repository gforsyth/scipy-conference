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
    subs = pandas.read_csv(csvfile, usecols=columns)
    return subs


def populate_submissions(subs_kwargs):
    subs = get_submissions(**subs_kwargs)
    sublist = []
    for sub in subs.itertuples():
        _, title, domain, emails, first_names, last_names = sub
        names = list(zip(re.findall(APP_REGEX, first_names),
                         re.findall(APP_REGEX, last_names)))
        names = [' '.join(name) for name in names]
        emails = re.findall(EMAIL_REGEX, emails)
        sublist.append(Submission(names, emails, title, domain))

    return sublist




subs_kwargs = {'csvfile': 'submissions.csv',
               'columns': ['Applicant-First Name',
                           'Applicant-Last Name',
                           'Applicant-E-mail Address',
                           'Submission-Initial Stage-Title',
                           'Submission-Initial Stage-Submission Subgroup',
                            ]
              }
