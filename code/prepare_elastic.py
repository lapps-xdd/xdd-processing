"""Preparing the ElasticSearch file

Takes the output of the merge.py script and creates input for ElasticSearch. 

$ python prepare_elastic.py -i INDIR -o OUTDIR [--domain DOMAIN] [--limit N]

Assumes that INDIR containes the merged files and creates OUTDIR/elastic.json,
which can be used for a bulk import.

The --domain options adds a domain to each document (this is pending the addition
of pre-processing funtionality to classify documents into domains) and --limit only
includes the first N documents from INDIR.

Uses the following fields:
- name
- year
- title
- authors
- abstract
- text
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

ELASTIC_FILE = 'elastic.json'


def parse_args():
    parser = argparse.ArgumentParser(description='Parse xDD files')
    parser.add_argument('-i', help="input directory")
    parser.add_argument('-o', help="output directory")
    parser.add_argument('--domain', help="Domain of the document", default=None)
    parser.add_argument('--limit', help="Maximum number of documents to process", default=sys.maxsize)
    return parser.parse_args()


def prepare(indir: str, outdir: str, domain: str, limit: int):
    fnames = [os.path.join(indir, fname) for fname in os.listdir(indir)]
    elastic_file = os.path.join(outdir, ELASTIC_FILE)
    print(f'Creating {elastic_file}')
    os.makedirs(outdir, exist_ok=True)
    with open(elastic_file, 'w') as fh:
        for n, fname in enumerate(sorted(fnames)):
            if n and n % 100 == 0:
                print(n)
            if n + 1 > limit:
                break
            json_obj = json.load(open(fname))
            elastic_obj = { "domain": domain }
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

    args = parse_args()
    prepare(args.i, args.o, args.domain, int(args.limit))
