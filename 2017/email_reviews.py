import smtplib
import pandas as pd
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from ldassn import load_rev_sublist


with open('auth', 'r') as f:
    password = f.read()
username = 'gilforsyth@gmail.com'
server = smtplib.SMTP('smtp.gmail.com:587')
server.starttls()
server.login(username, password)

revlist, sublist, revdict, subdict = load_rev_sublist()

reviews = pd.read_excel('SciPy 2018_data_2018-04-12.xlsx', sheet_name='Reviews')
# drop most columns
reviews = reviews[['submission #', 'member name', 'text', 'total score']]

for sub in sublist:
    email_body = f"""
Thank you for submitting to SciPy 2018.

Last year, SciPy moved to a double-open peer review process, and we hope
you will find value in the candid comments from your reviewers.

Also note that SciPy requested that reviewers abide by Guidelines
introduced last year, aimed at interrupting implicit bias and avoiding
conflicts of interest.
You can review those guidelines at https://scipy2018.scipy.org/ehome/299527/648151/

The reviews for your submission

    {sub.title}

are printed below. Please feel free to contact
us with any questions and we hope to see you in Austin in July!

The SciPy 2018 Program Chairs,
Gil Forsyth & Lorena A. Barba\n\n\n"""

    revs = reviews[reviews['submission #'] == sub.subid]
    for rev in revs.itertuples():
        email_body += 30*'-' + '\n'
        email_body += f'Reviewer: {rev._2}\nScore: {rev._4} (score range from -3 to 3)\nReview text: {rev.text}\n'

    email_addr = [em for em in sub.emails if isinstance(em, str)]
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'SciPy2018 Submission Reviews'
    msg['From'] = 'Gil Forsyth <gilforsyth@gmail.com>'
    msg['To'] = ', '.join(email_addr)
    msg['Cc'] = 'Lorena Barba <labarba@email.gwu.edu>,'
    msg['Date'] = email.utils.formatdate()
    msg.attach(MIMEText(email_body, 'plain'))
    from_address = 'Gil Forsyth <gilforsyth@gmail.com>'
    to_address = email_addr

    server.sendmail(from_address, to_address, msg.as_string())
