import csv
import sys
import email
import email.utils
import jinja2
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

with open('auth', 'r') as f:
    password = f.read()
username = 'gilforsyth@gmail.com'
server = smtplib.SMTP('smtp.gmail.com:587')
server.starttls()
server.login(username, password)

if len(sys.argv) < 3:
    print('Usage: ./mail_decisions.py decisions.csv decision.txt.in')

with open(sys.argv[2], 'r') as fp:
    email_template = fp.read()
template = jinja2.Template(email_template)

with open(sys.argv[1], 'r') as f:
    filereader = csv.reader(f, delimiter=',')
    submissions = []
    for row in filereader:
        if row[0] == 'title':
            continue
        submission = {}
        submission['title'] = row[0]
        submission['domain'] = row[1]
        submission['authors'] = row[3].split(';')
        submission['emails'] = row[4].split(';')

        submissions.append(submission)

domain_map = {
    'Computational Science': 'Computation Science & Numerical Techniques',
    'Materials Science': 'Materials Science & Engineering',
    'bio': 'Biology, Biophysics & Biostatistics',
    'earth': 'Earth, Ocean & Geo Science',
    'Machine Learning': 'Machine Learning & Artifical Intelligence',
    }

for sub in submissions:
    domain = domain_map.get(sub['domain'], '')
    if domain:
        sub['domain'] = domain

    email_body = template.render(
        names = ', '.join(sub['authors']),
        title = sub['title'],
        track = sub['domain'],
    )
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'SciPy2017 Abstract Decision - Action Requested'
    msg['From'] = 'Gil Forsyth <gilforsyth@gmail.com>'
    msg['To'] = ', '.join([em.strip() for em in sub['emails']])
    msg['Cc'] = 'Lorena Barba <labarba@email.gwu.edu>,'
    msg['Date'] = email.utils.formatdate()
    msg.attach(MIMEText(email_body, 'plain'))
    from_address = 'Gil Forsyth <gilforsyth@gmail.com'
    to_address = [em.strip() for em in sub['emails']]

    print(email_body)

    server.sendmail(from_address, to_address, msg.as_string())
