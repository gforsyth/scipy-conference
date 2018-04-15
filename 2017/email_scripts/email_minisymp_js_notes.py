import email
import email.utils
import jinja2
import smtplib
import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from load_save import load_rev_sublist
from load_chairs import chairs
from domain import domain_pool_subs

from review_bookmarklet_generator import generate_js_bookmarklet


with open('auth', 'r') as f:
    password = f.read()
username = 'gilforsyth@gmail.com'
server = smtplib.SMTP('smtp.gmail.com:587')
server.starttls()
server.login(username, password)

with open('raw_html', 'r') as f:
    html_doc = f.read()

with open('mailings/minisymp_js_bookmarklet.txt.in', 'r') as f:
    text = f.read()

letter_temp = jinja2.Template(text)

revlist, sublist, _, _ = load_rev_sublist()
total_reviews = len(sublist) * 6

# need to filter out posters
df = pd.read_excel('/home/gil/Dropbox/scipy/2018/program_committee/SciPy 2018_data_2018-03-17.xlsx', sheet_name='Submissions')
df['subtype'] = df['form fields'].apply(lambda x: x.split('\n')[0].split(' ')[-1])
for sub in sublist:
    sub.subtype = df[df['#'] == sub.subid]['subtype'].values[0]

sublist = [sub for sub in sublist if sub.subtype == 'Talk']

domain_pool = domain_pool_subs(sublist)
total_subs = len(sublist)
total_talks = 60

talk_slots = dict()

for domain, subs in domain_pool.items():
    talk_slots[domain] = round(len(subs) / total_subs * total_talks)

total_reviews = 1134
review_pct = 84.74

for domain in domain_pool.keys():
    if domain != 'general':
        continue
    bookmarklet = generate_js_bookmarklet(html_doc, domain)
    email_body = letter_temp.render(total_reviews=total_reviews,
                                review_pct=review_pct, total_submissions=len(sublist),
                                domain_slots=talk_slots[domain], domain=domain, bookmarklet=bookmarklet)


    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'SciPy2018 Minisymposia Talk Selection Information'
    msg['From'] = 'Gil Forsyth <gilforsyth@gmail.com>'
    msg['To'] = ', '.join([chair.email for chair in chairs[domain]])
    msg['Cc'] = 'Lorena Barba <labarba@email.gwu.edu>,'
    msg['Date'] = email.utils.formatdate()
    msg.attach(MIMEText(email_body, 'plain'))
    from_address = 'Gil Forsyth <gilforsyth@gmail.com>'
    to_address = [chair.email for chair in chairs[domain]]
    print(email_body)

#    server.sendmail(from_address, to_address, msg.as_string())
