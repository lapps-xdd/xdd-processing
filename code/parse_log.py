
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
