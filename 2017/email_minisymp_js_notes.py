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

from incomplete import populate_domain_pool
from review_bookmarklet_generator import generate_js_bookmarklet


with open('auth', 'r') as f:
    password = f.read()
username = 'gilforsyth@gmail.com'
server = smtplib.SMTP('smtp.gmail.com:587')
server.starttls()
server.login(username, password)

with open('raw_html', 'r') as f:
    html_doc = f.read()

revlist, sublist, revdict, subdict = load_rev_sublist()
revlist = [rev for rev in revlist if hasattr(rev, 'to_review')]
domain_pool = populate_domain_pool(revlist, sublist)

for domain in domain_pool.keys():
    print(generate_js_bookmarklet(html_doc, domain))
