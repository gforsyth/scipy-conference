import pandas

def load_reviewer_report(csv='ReviewerListReport_220975.csv'):
    """
    Load etouches report and filter out Tutorial submissions
    """
    report = pandas.read_csv(csv)
    report = report[report['Submission Group'] == 'Conference Talks and Posters']

    return report

def get_reviewers_not_started(revlist, csv):
    """
    Return the reviewers who have not started a review in eTouches.
    """

    report = load_reviewer_report(csv)
    reviewers_started = set(report['Reviewer Name'].values)
    reviewers_all = {rev.name for rev in revlist}
    reviewers_to_bug = reviewers_all.difference(reviewers_started)

    return [rev for rev in revlist if rev.name in reviewers_to_bug]


