import pandas
import pickle

with open('/home/gil/Dropbox/sublist.pickle', 'rb') as f:
    sublist = pickle.load(f)

with open('/home/gil/Dropbox/revlist.pickle', 'rb') as f:
    revlist = pickle.load(f)

assignments = pandas.read_csv('scipy2017.reviewer.assignments - assignments.csv', usecols=(0, 2, 3, 4, 5, 6, 7, 8))

for sub in sublist:
    sub.reviewers = []

for rev in revlist:
    rev.to_review = []
    rev.email = rev.email.strip()

for _, subid, title, rev1, rev1em, rev2, rev2em, rev3, rev3em in assignments.itertuples():
    sub = [sub for sub in sublist if sub.subid == subid][0]
    for rev in revlist:
        if rev.email in [rev1em, rev2em, rev3em]:
            rev.to_review.append(sub)
            sub.reviewers.append(rev)
