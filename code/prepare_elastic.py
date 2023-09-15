"""Preparing the ElasticSearch file

Takes the output of the merge.py script and creates input for ElasticSearch. Creates one file 
for each topic and that file can be used for a bulk import.

Uses the following fields:
- name
- year
- title
- authors
- abstract
- text
- entities-TYPE for each key in the entities dictionary
- topic

For now, the entities are just lists that enumerate each token, so if the merged file had

"entities": {
    "ORG": { "the Cassini INMS": 1, "RS": 2 },
    "PRODUCT": { "Saturn": 6, "Voyager 2": 2 } }

Then the output will have

"entities-ORG": ["the Cassini INMS", "RS", "RS" ],
"entities-PRODUCT": ["Saturn", "Saturn", "Saturn", "Saturn", "Saturn", "Saturn", "Voyager 2", "Voyager 2" ]

Output is written to three files in the code directory:

    elastic-biomedical.json
    elastic-geoarchive.json
    elastic-molecular_physics.json

These can be used for an elastic bulk import:

$ curl http://localhost:9200/xdd-bio/_doc/_bulk \
    -o /dev/null \
    -H "Content-Type: application/json" \
    -X POST --data-binary @/code/elastic-biomedical.json

"""

import os, sys, json
from config import TOPICS_DIR, TOPICS

data_dir = 'processed_mer'


def prepare_topic(topic: str):
    path = os.path.join(TOPICS_DIR, topic, data_dir)
    fnames = [os.path.join(path, fname) for fname in os.listdir(path)]
    elastic_file = f'elastic-{topic}.json'
    print(f'Creating {elastic_file}')
    with open(elastic_file, 'w') as fh:
        for n, fname in enumerate(sorted(fnames)):
            if n % 100 == 0:
                print(n)
            json_obj = json.load(open(fname))
            elastic_obj = { "topic": topic }
            for field in ('year', 'title', 'authors'):
                elastic_obj[field] = json_obj[field]
            for field in ('abstract', 'text'):
                elastic_obj[field] = json_obj[field]
            fh.write(json.dumps({"index": {}}) + '\n')
            fh.write(json.dumps(elastic_obj) + '\n')
        fh.write('\n')



if __name__ in '__main__':

    for topic in TOPICS:
        print()
        prepare_topic(topic)

