import pandas
report = pandas.read_csv('ReviewerListReport_220975.csv')
report = report[report['Submission Group'] == 'Conference Talks and Posters']
#print('Reviewers who have logged in and started a review')
#print(report['\ufeff"Reviewer Name"'].value_counts())

print('{} reviewers have started a review'.format(len(report['Reviewer Name'].value_counts())))
done = report[report['Initial Stage : Review Status'] == 'Complete']
#print('Reviewers who have completed reviews')
#print(done['\ufeff"Reviewer Name"'].value_counts())
print('{} reviewers have completed a review'.format(len(done['Reviewer Name'].value_counts())))
complete = sum(done['Reviewer Name'].value_counts().values)
print('{} reviews completed'.format(complete))
print('{:d}% of the way there'.format(int(100*complete/444)))
