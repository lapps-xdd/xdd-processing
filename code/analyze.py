"""Simple analysis of xDD directories

$ python analyze.py [--write]

Prints some statistics on the size to the terminal and, if the --write option 
is used, writes some files to the out directory with files ordered on size.

Locations of the xDD are hard-coded in the configuration file.

"""

import os, sys
from config import TOPICS_DIR, TOPICS, DATA_DIRS

def analyze_topics(write_overview: bool):
    print(
        '\nPrinting number of documents, total size, average_size and processing' +
        '\ntime in seconds (the latter gives some wacco results)\n')
    for topic in TOPICS:
        analyze_topic(topic, write_overview)
        print()

def analyze_topic(topic: str, write_overview: bool):
    print(f'{topic}\n')
    for data_dir in DATA_DIRS:
        path = os.path.join(TOPICS_DIR, topic, data_dir)
        if not os.path.exists(path):
            continue
        fnames = [os.path.join(path, fname) for fname in os.listdir(path)]
        fnames = [f for f in fnames if os.path.isfile(f)]
        fsizes = [(os.path.getsize(f), os.path.split(f)[-1]) for f in fnames]
        ftimes = [os.stat(f).st_birthtime for f in fnames]
        ftimes = list(sorted(ftimes))
        number_of_files = len(fnames)
        if number_of_files == 0:
            continue
        total_size = int(sum([pair[0] for pair in fsizes]) / 1000000)
        average_size = int(total_size * 1000 / number_of_files)
        elapsed_time = str(int(ftimes[-1] - ftimes[0]))
        if data_dir in ('text', 'scienceparse'):
            elapsed_time = '-'
        print(f'    {data_dir:15} {number_of_files:5d} {total_size:5d}M'
              + f'{average_size:5d}K  {elapsed_time:>6s}')
        if write_overview and data_dir == 'output/doc':
            overview_file = f'out/sizes-{topic}-{data_dir.split("/")[0]}.html'
            with open(overview_file, 'w') as fh:
                #print(f'Printing {overview_file}')
                fh.write('<html>\n')
                fh.write('<table cellpadding=5 cellspacing=0 border=1>\n')
                for n, (fsize, fname) in enumerate(sorted(fsizes, reverse=True)):
                    fh.write('<tr>\n')
                    fh.write(f'  <td>{n}</td>\n')
                    fh.write(f'  <td>{fsize}</td>\n')
                    fh.write(f'  <td><a href="{path}/{fname}">{fname}</a></td>\n')
                    fh.write('</tr>\n')
                fh.write('</table>\n')
                fh.write('</html>\n')

def ping_results():
    for topic in TOPICS:
        pos_dir = os.path.join(TOPICS_DIR, topic, 'processed_pos')
        docs = os.listdir(pos_dir)
        for doc in docs:
            tokens = []
            path = os.path.join(pos_dir, doc)
            with open(path) as fh:
                for line in fh:
                    fields = line.strip().split('\t')
                    if len(fields) > 3:
                        tokens.append(fields[1])
            print(f'{doc}  {len(tokens):6d}  {sum([len(t) for t in tokens]):8d}')
        break


if __name__ == '__main__':

    ping = True if '--ping' in sys.argv else False
    write_overview = True if '--write' in sys.argv else False
    if ping:
        ping_results()
    else:
        analyze_topics(write_overview=write_overview)
