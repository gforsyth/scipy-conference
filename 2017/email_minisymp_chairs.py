import sys
import email
import email.utils
import jinja2
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from incomplete import get_incomp_reviewers
from chairs import chairs

domain_pool, revlist, sublist = get_incomp_reviewers()

with open('auth', 'r') as f:
    password = f.read()
username = 'gilforsyth@gmail.com'
server = smtplib.SMTP('smtp.gmail.com:587')
server.starttls()
server.login(username, password)

for domain in domain_pool.keys():
    if domain == 'General':
        continue
    norevs = [sub for sub in sublist if len(sub.reviewers) == 3 and sub.domain == domain]
    email_body = """
    Dear chairs,

    Thanks for being part of the SciPy 2017 Program Committee!

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

    for i in range(4, 0, -1):
        revs = [rev for rev in domain_pool[domain] if len(rev.to_review) == i]
        if revs:
            email_body += '\n    Reviewers who have to complete {} review(s): \n\n'.format(i)
            for rev in revs:
                email_body += '    ' + str(rev) + '\n'

            email_body += '\n    And a easily copy-pasteable list of their email address:\n    '
            email_body += ', '.join([rev.email for rev in revs])
            email_body += '\n\n'

    email_body += '\n    And if you just want to email-blast all of the reviewers with work still to do in your area: \n\n'
    email_body += '    '
    email_body += ', '.join([rev.email for rev in domain_pool[domain]])

    email_body += """
    \n\n
    As always, please let us know if you have any questions or concerns, or just want to yell about eTouches.

    Thanks,
    Lorena & Gil
    Program Co-chairs"""

    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'SciPy2017 Minisymposia Info for Chairs'
    msg['From'] = 'Gil Forsyth <gilforsyth@gmail.com>'
    msg['To'] = ', '.join([chair.email for chair in chairs[domain]])
    msg['Cc'] = 'Lorena Barba <labarba@email.gwu.edu>,'
    msg['Date'] = email.utils.formatdate()
    msg.attach(MIMEText(email_body, 'plain'))
    from_address = 'Gil Forsyth <gilforsyth@gmail.com>'
    to_address = [chair.email for chair in chairs[domain]]
    print(email_body)

    server.sendmail(from_address, to_address, msg.as_string())
