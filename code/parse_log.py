"""Parse log content

Usage:

$ python parse_log <logfile>

Goes through the log file and print all errors and the total processing time.

Log files are assumed to look like the following, with the input file and the 
time in seconds to process that file. Instead of the processing time there 
could be an error message.

54b4324ee138239d8684aeb2_input.pdf.json	0.91
54b43271e138239d86850fcd_input.pdf.json	1.13
54d0bed0e13823b501cdbeec_input.pdf.json	0.03
54d5354ce138238471e7f573_input.pdf.json	1.11

"""

import sys

messages = []
errors = []
logfiles = sys.argv[1:]
for logfile in logfiles:
	with open(logfile) as fh:
		times = []
		for line in fh:
			fname, message = line.strip().split('\t', 2)
			try:
				times.append(float(message))
			except ValueError:
				errors.append((logfile, fname, message))
		messages.append((logfile, int(sum(times)/60)))

print()
for logfile, fname,message in errors:
	print(f'{logfile} {fname}\n{message}')

print()
for logfile, message in messages:
	print(f'{logfile:35} -  Total time elapsed: {message:d} minutes')
print()
