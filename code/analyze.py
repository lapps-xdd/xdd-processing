"""Simple analysis of xDD directories

$ python analyze.py [--write]

Prints some statistics on the size to the terminal and, if the --write option 
is used, writes some files to the out directory with files ordered on size.

Locations of the xDD are hard-coded in this script.

"""

import os

topics_dir = '/Users/Shared/data/xdd/doc2vec/topic_doc2vecs'
topics = ('biomedical',  'geoarchive', 'molecular_physics')
data_dirs = ('text', 'scienceparse', 'processed_doc', 'processed_ner', 'processed_pos')

for topic in topics:
	print()
	for data_dir in data_dirs:
		path = os.path.join(topics_dir, topic, data_dir)
		fnames = [os.path.join(path, fname) for fname in os.listdir(path)]
		sized_fnames = [(os.path.getsize(f), os.path.split(f)[-1])
						for f in fnames if os.path.isfile(f)]
		number_of_files = len(fnames)
		total_size = int(sum([pair[0] for pair in sized_fnames]) / 1000000)
		print(f'{topic:20} {data_dir:20} {number_of_files:5d}  {total_size:4d}MB')
		if data_dir == 'processed_doc':
			with open(f'out/{topic}-{data_dir}-sizes.html', 'w') as fh:
				fh.write('<html>\n')
				fh.write('<table cellpadding=5 cellspacing=0 border=1>\n')
				for n, (fsize, fname) in enumerate(sorted(sized_fnames, reverse=True)):
					fh.write('<tr>\n')
					fh.write(f'  <td>{n}</td>\n')
					fh.write(f'  <td>{fsize}</td>\n')
					fh.write(f'  <td><a href="{path}/{fname}"">{fname}</a></td>\n')
					fh.write('</tr>\n')
				fh.write('</table>\n')
				fh.write('</html>\n')
