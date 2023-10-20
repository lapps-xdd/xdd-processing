"""

Print some statistics on availabilty of metadata and abstracts.

"""

import os, json, collections
from config import TOPICS_DIR, TOPICS, data_directory


# Metadata files. Information in these files can also be obtained by pinging the xDD API
# at https://xdd.wisc.edu/api/articles. For example:
# https://xdd.wisc.edu/api/articles?docids=5783bcafcf58f176c768f5cc,5754e291cf58f1b0c7844cd2
# TODO: this is also in merge.py, move to config.py
METADATA = {
    'biomedical': 'biomedical_docids_10k.bibjson',
    'geoarchive': 'geoarchive.bibjson',
    'molecular_physics': 'molecular_physics_docids_10k.bibjson' }


def analyze_topics():
    for topic in TOPICS:
        analyze_topic(topic)

def analyze_topic(topic: str):
    print(topic)
    metadata_file = os.path.join(TOPICS_DIR, topic, METADATA.get(topic))
    scpa_dir = data_directory(topic, 'scienceparse')
    #print('   ', metadata_file)
    #print('   ', scpa_dir)
    analyze_metadata(metadata_file)
    analyze_scienceparse(scpa_dir)

def analyze_metadata(metadata_file: str):
    metadata = json.load(open(metadata_file))
    metadata_fields = collections.defaultdict(int)
    for doc_data in metadata:
        for key in doc_data.keys():
            if doc_data[key]:
                metadata_fields[key] += 1
    print()
    for k, v in sorted(metadata_fields.items()):
        if k not in ('_gddid', 'identifier'):
            print(f'    {k:10}  {v:5d}')
    print()

def analyze_scienceparse(scpa_dir: str):
    abstracts = 0
    for n, fname in enumerate(os.listdir(scpa_dir)):
        #if n > 10: break
        scpa = json.load(open(os.path.join(scpa_dir, fname)))
        abstract = scpa['metadata'].get('abstractText')
        if abstract:
            abstracts += 1
    print(f'    abstract    {abstracts:5d}\n')


if __name__ == '__main__':

    analyze_topics()
