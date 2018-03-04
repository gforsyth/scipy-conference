#!/usr/bin/env python

"""This script sends an email to the minisymposia chairs with a list of
'delinquent' reviews in their track, so that they can _gently_ prod those
reviewers in to completing their assigned reviews.

Note that the `chairs` import is not version controlled as it contains a bunch
of email addresses that we aren't publishing publicly here.

The format of those email address is as follows:

`chairs` is a dict, the keys of which are the track names and the values of which are lists, where each list element is a namedtuple `chair`:

```
chair = namedtuple('chair', ['name', 'email'])
```
"""

import sys
import email
import email.utils
import jinja2
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from ldassn import load_rev_sublist
from load_chairs import chairs
from incomplete import populate_domain_pool
from missing_reviews import update_rev_sub_lists


with open('auth', 'r') as f:
    password = f.read()
username = 'gilforsyth@gmail.com'
server = smtplib.SMTP('smtp.gmail.com:587')
server.starttls()
server.login(username, password)



revlist, sublist, revdict, subdict = load_rev_sublist()
revlist, sublist, revdict, subdict = update_rev_sub_lists(revlist, sublist, revdict, subdict)
domain_pool = populate_domain_pool(revlist, sublist)

for domain in domain_pool.keys():
    if domain == 'general': # program chairs handle general talks, so no email to ourselves
        continue
    norevs = [sub for sub in sublist if len(sub.reviewers) == 6 and sub.domain == domain]
    print(f"{domain:-^80}")
    email_body = f"""
    Dear chairs,

    Thanks for being part of the SciPy 2018 Program Committee!

    We are a little more than 1 week into the review period. There is still plenty of time to gather reviews, but it never hurts to give a little nudge to keep things moving.

    Here are a list of submissions/reviewers in your symposia that might need a
    little extra attention

    """
    if norevs:
        email_body += "\n    Submissions with no reviews (and the assigned reviewers):\n\n"
        for sub in norevs:
            email_body += '    ' + str(sub.title) + '\n'
            for rev in sub.reviewers:
                email_body += '    ' + str(rev) + '\n'
            email_body += '\n'
    else:
        email_body += "\n      Oh good! All of the submissions in your track have at least one review!\n\n"

#    for i in range(6, 0, -1):
#        revs = [rev for rev in domain_pool[domain] if len(rev.to_review) == i]
#        if revs:
#            email_body += '\n    Reviewers who have to complete {} review(s): \n\n'.format(i)
#            for rev in revs:
#                email_body += '    ' + str(rev) + '\n'
#
#            email_body += '\n    And a easily copy-pasteable list of their email address:\n    '
#            email_body += ', '.join([rev.email for rev in revs])
#            email_body += '\n\n'

    email_body += '\n    If you just want to email-blast all of the reviewers with work still to do in your area: \n\n'
    email_body += '    '
    email_body += ', '.join([rev.email for rev in domain_pool[domain]])

    email_body += """
    \n\n
    As always, please let us know if you have any questions or concerns.

    Thanks,
    Lorena & Gil
    Program Co-chairs"""

    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'SciPy2018 Minisymposia Review Progress'
    msg['From'] = 'Gil Forsyth <gilforsyth@gmail.com>'
    msg['To'] = ', '.join([chair.email for chair in chairs[domain]])
    msg['Cc'] = 'Lorena Barba <labarba@email.gwu.edu>,'
    msg['Date'] = email.utils.formatdate()
    msg.attach(MIMEText(email_body, 'plain'))
    from_address = 'Gil Forsyth <gilforsyth@gmail.com>'
    to_address = [chair.email for chair in chairs[domain]]
    print(email_body)

#    server.sendmail(from_address, to_address, msg.as_string())
