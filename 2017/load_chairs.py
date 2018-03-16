from collections import namedtuple
chair = namedtuple('chair', ['name', 'email'])
chairs = dict()

with open('SciPy 2018 Program Chairs planning - chair emails.csv', 'r') as f:
    a = f.readlines()

for line in a:
    line = line.strip().split(',')
    chairs[line[0].lower()] = [chair(line[1], line[2]), chair(line[3], line[4])]
