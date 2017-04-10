import pandas
report = pandas.read_csv('ReviewerListReport_220975.csv')
report = report[report['Submission Group'] == 'Conference Talks and Posters']
#print('Reviewers who have logged in and started a review')
#print(report['\ufeff"Reviewer Name"'].value_counts())
print('Reviewers who have started a review')
print(len(report['"Reviewer Name"'].value_counts()))
done = report[report['Initial Stage : Review Status'] == 'Complete']
#print('Reviewers who have completed reviews')
#print(done['\ufeff"Reviewer Name"'].value_counts())
print('Number of reviewers who have completed reviews')
print(len(done['"Reviewer Name"'].value_counts()))
print('Reviews started (possibly completed)')
print(len(report))
print('Total reviews completed')
complete = sum(done['\ufeff"Reviewer Name"'].value_counts().values)
print(complete)
print('Percentage of reviews started: {:d}%'.format(int(100*len(report)/444)))
print('Percentage of reviews completed: {:d}%'.format(int(100*complete/444)))
