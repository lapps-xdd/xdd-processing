"""Preparing the ElasticSearch file

Takes the output of the merge.py script and creates input for ElasticSearch. 

$ python prepare_elastic.py -i INDIR -o OUTDIR [--domain DOMAIN] [--limit N]

Assumes that INDIR containes the merged files and creates OUTDIR/elastic.json,
which can be used for a bulk import.

The --domain options adds a domain to each document (this is pending the addition
of pre-processing functionality to classify documents into domains) and --limit only
includes the first N documents from INDIR.

Uses the following fields:
- name
- year
- title
- authors
- abstract
- content
- summary
- entities
- terms
- domain


The elastic.json file can be used for an elastic bulk import from OUTDIR:

$ curl http://localhost:9200/xdd/_doc/_bulk \
    -o /dev/null \
    -H "Content-Type: application/json" \
    -X POST --data-binary @elastic.json

To test with a small sample first use the --limit option and do:

$ curl http://localhost:9200/test/_doc/_bulk \
    -H "Content-Type: application/json" \
    -X POST --data-binary @elastic.json

$ curl -X GET "http://localhost:9200/test/_search?pretty"

$ curl -X GET "http://localhost:9200/test/_mapping?pretty"

"""

import os, sys, json, argparse
from utils import fix_terms

ELASTIC_FILE = 'elastic.json'


def parse_args():
    def tags(tagstring: str):
        return tagstring.split(',')
    parser = argparse.ArgumentParser(
        description='Convert merged files into ElasticSearch import file')
    parser.add_argument('-i', metavar='PATH', help="input directory")
    parser.add_argument('-o', metavar='PATH', help="output directory")
    parser.add_argument('--tags', help="comma-separated list of tags", default=[], type=tags)
    parser.add_argument('--limit', help="number of documents to process", default=sys.maxsize, type=int)
    return parser.parse_args()


def prepare(indir: str, outdir: str, tags: list, limit: int):
    fnames = [os.path.join(indir, fname) for fname in os.listdir(indir)]
    elastic_fname = os.path.join(outdir, ELASTIC_FILE)
    print(f'Creating elastic bulk file {elastic_fname}')
    os.makedirs(outdir, exist_ok=True)
    with open(elastic_fname, 'w') as fh:
        for n, fname in enumerate(sorted(fnames)):
            if n and n % 100 == 0:
                print(n)
            if n + 1 > limit:
                break
            json_obj = json.load(open(fname))
            elastic_obj = create_elastic_object(json_obj, tags)
            fh.write(json.dumps({"index": {"_id": json_obj['name']}}) + '\n')
            fh.write(json.dumps(elastic_obj) + '\n')
        fh.write('\n')


def create_elastic_object(json_obj: dict, tags: list):
    """Creates a dictionary meant for bul import into ElasticSearch."""
    elastic_obj = {"tags": tags}
    for field in ('name', 'year', 'title', 'authors', 'url', 'abstract',
                  'content', 'summary', 'terms'):
        elastic_obj[field] = json_obj[field]
    elastic_obj['entities'] = {}
    for entity_type, dictionary in json_obj.get('entities', {}).items():
        elastic_obj['entities'][entity_type] = \
            [(entity, str(count)) for entity, count in dictionary.items()]
    fix_terms(elastic_obj)
    return elastic_obj



if __name__ in '__main__':

    args = parse_args()
    prepare(args.i, args.o, args.tags, int(args.limit))
