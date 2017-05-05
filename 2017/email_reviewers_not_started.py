#!/usr/bin/env python

"""Script to mail all SciPy reviewers who have not yet started a review.

This script was written for use with the eTouches/eSelect backend. The
`ReviewerListReport.csv` file expected as input can be obtained as follows: Log
in to eTouches, select "Reports", then select "Reviewer List" and export to
csv.

That particular report will only include names of those who have at least
started a review and clicked "Save and continue later" so the set difference
between those names and the list of reviewers are those who have not started a
review. Unfortunately, this means we have to compare _names_ which is a _bad
idea_. Expect some false positives if people have entered their names/titles
differently in different systems (hopefully this will not happen, but expect
the worst.)

"""
import sys
import email
import email.utils
import jinja2
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from ldassn import load_rev_sublist
from reviewers import get_reviewers_not_started

if len(sys.argv) < 3:
    print('Usage: ./email_reviewers_not_started.py ReviewerListReport.csv review_reminder.txt.in')
    sys.exit()

revlist, sublist, revdict, subdict = load_rev_sublist()
to_mail = get_reviewers_not_started(revlist, sys.argv[1])

with open(sys.argv[2], 'r') as f:
    email_template = f.read()

template = jinja2.Template(email_template)

with open('auth', 'r') as f:
    password = f.read()
username = 'gilforsyth@gmail.com'
server = smtplib.SMTP('smtp.gmail.com:587')
server.starttls()
server.login(username, password)

for rev in to_mail:
    email_body = template.render(name=rev.name)
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'SciPy2017 review reminder'
    msg['From'] = 'Gil Forsyth <gilforsyth@gmail.com>'
    msg['To'] = rev.email
    msg['Cc'] = 'Lorena Barba <labarba@email.gwu.edu>,'
    msg['Date'] = email.utils.formatdate()
    msg.attach(MIMEText(email_body, 'plain'))
    from_address = 'Gil Forsyth <gilforsyth@gmail.com>'
    to_address = ['Lorena Barba <labarba@email.gwu.edu']
    to_address.append(rev.email)
    print(email_body)
