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
- entities
- terms
- topic

Output is written to three files:

    TOPICS_DIR/biomedical/processed_ela/elastic-biomedical.json
    TOPICS_DIR/geoarchive/processed_ela/elastic-geoarchive.json
    TOPICS_DIR/molecular_physics/processed_ela/elastic-molecular_physics.json

These can be used for an elastic bulk import from those directories:

$ curl http://localhost:9200/xdd-bio/_doc/_bulk \
    -o /dev/null \
    -H "Content-Type: application/json" \
    -X POST --data-binary @elastic-biomedical.json

$ curl http://localhost:9200/xdd-geo/_doc/_bulk \
    -o /dev/null \
    -H "Content-Type: application/json" \
    -X POST --data-binary @elastic-geoarchive.json

$ curl http://localhost:9200/xdd-mol/_doc/_bulk \
    -o /dev/null \
    -H "Content-Type: application/json" \
    -X POST --data-binary @elastic-molecular_physics.json

Testing a small sample:

$ curl http://localhost:9200/test/_doc/_bulk \
    -H "Content-Type: application/json" \
    -X POST --data-binary @elastic-biomedical.json

$ curl -X GET "http://localhost:9200/test/_search?pretty"

$ curl -X GET "http://localhost:9200/test/_mapping?pretty"

"""

import os, sys, json
from config import TOPICS_DIR, TOPICS, data_directory

mer_dir = 'processed_mer'
ela_dir = 'processed_ela'


def prepare_topic(topic: str, limit: int):
    path = os.path.join(TOPICS_DIR, topic, mer_dir)
    fnames = [os.path.join(path, fname) for fname in os.listdir(path)]
    elastic_file = os.path.join(data_directory(topic, ela_dir), f'elastic-{topic}.json')
    print(f'Creating {elastic_file}')
    with open(elastic_file, 'w') as fh:
        for n, fname in enumerate(sorted(fnames)):
            if n % 100 == 0:
                print(n)
            if n + 1 > limit:
                break
            json_obj = json.load(open(fname))
            elastic_obj = { "topic": topic }
            for field in ('name', 'year', 'title', 'authors', 'url', 'abstract',
                          'text', 'summary', 'terms'):
                elastic_obj[field] = json_obj[field]
            elastic_obj['entities'] = {}
            for entity_type, dictionary in json_obj.get('entities', {}).items():
                elastic_obj['entities'][entity_type] = \
                    [(entity, str(count)) for entity, count in dictionary.items()]
            fix_terms(elastic_obj)
            fh.write(json.dumps({"index": {"_id": json_obj['name']}}) + '\n')
            fh.write(json.dumps(elastic_obj) + '\n')
        fh.write('\n')


def fix_terms(elastic_obj: dict):
    """Elastic search does not allow lists with different types so turning the integer
    and the float into strings."""
    # TODO: consider using dictionaries
    for term_triple in elastic_obj['terms']:
        term_triple[1] = str(term_triple[1])
        term_triple[2] = "%.6f" % term_triple[2]


if __name__ in '__main__':

    limit = int(sys.argv[1]) if len(sys.argv) > 1 else sys.maxsize
    for topic in TOPICS:
        print()
        prepare_topic(topic, limit)

