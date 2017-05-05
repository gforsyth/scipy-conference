#!/usr/bin/env python

"""This script was written for use with the eTouches/eSelect backend. The
`reviews.csv` file expected as input can be obtained as follows:

Log in to eTouches, select "Reports", then select "Reviewer List" and export to
csv. Make sure to click the radio button that exports ALL fields, not just the
current view.

"""

import sys
import email
import email.utils
import pandas
import jinja2
import smtplib
from collections import namedtuple
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from ldassn import load_rev_sublist

revlist, sublist, revdict, subdict = load_rev_sublist()

if len(sys.argv) < 3:
    sys.exit('Usage: ./mail_reviews.py reviews.csv reviews.txt.in')

csv = sys.argv[1]
reviews = pandas.read_csv(csv)

reviews = reviews.rename(columns={'Submission ID':'subid', 'Initial Stage : General Comments':'comments', 'Reviewer Name':'reviewer_name', 'Initial Stage : Proposal rating (1 - Poor, 5 - Excellent)':'rating' })

review = namedtuple('review', ['name', 'comments', 'rating'])

for rev in reviews.itertuples():
    try:
        sub = subdict[rev.subid]
        if not hasattr(sub, 'reviews'):
            sub.reviews = []
        sub.reviews.append(review(rev.reviewer_name, rev.comments, rev.rating))
    except KeyError:
        pass

with open('auth', 'r') as f:
    password = f.read()
username = 'gilforsyth@gmail.com'
server = smtplib.SMTP('smtp.gmail.com:587')
server.starttls()
server.login(username, password)

with open(sys.argv[2], 'r') as fp:
    email_template = fp.read()
template = jinja2.Template(email_template)

for sub in sublist:
    if hasattr(sub, 'reviews'):
        review_text = ''
        for i, rev in enumerate(sub.reviews):
            review_text += 'Review {} -- {}\n{} \n\n\nRating: {} / 5.0\n\n'.format(i + 1, rev.name, rev.comments, rev.rating)

        email_body = template.render(
            names = ', '.join(sub.authors),
            title = sub.title,
            reviews = review_text,
        )
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'SciPy2017 -- Abstract reviews'
        msg['From'] = 'Gil Forsyth <gilforsyth@gmail.com>'
        msg['To'] = ', '.join([em.strip() for em in sub.emails])
        msg['Cc'] = 'Lorena Barba <labarba@email.gwu.edu>,'
        msg['Date'] = email.utils.formatdate()
        msg.attach(MIMEText(email_body, 'plain'))
        from_address = 'Gil Forsyth <gilforsyth@gmail.com'
        to_address = [em.strip() for em in sub.emails]

        print(email_body)

        #server.sendmail(from_address, to_address, msg.as_string())
