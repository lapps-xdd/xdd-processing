"""

Given a log file with NER results, print all documents that took longer than 
twenty seconds to process. Also tally the total time spent in these outliers.

"""

import sys

logfile = sys.argv[1]

file_number = 0
outliers = 0
total_time = 0
total_time_in_outliers = 0

for line in open(logfile):
	try:
		fname, time = line.strip().split('\t')
		file_number += 1
		time = float(time)
		total_time += int(time)
		if time > 20:
			print(f'{file_number} {fname} {time}')
			outliers += 1
			total_time_in_outliers += int(time)
	except ValueError:
		pass

ratio = int(100 * total_time_in_outliers / total_time)
total_time_in_outliers = int(total_time_in_outliers / 60 / 60)

print()
print(f'Time spent in {outliers} outliers is {total_time_in_outliers} hours ({ratio}%)')
