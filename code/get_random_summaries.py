"""

Select random files from each topic and write JSON files, one for each topic.

$ python get_random_summaries.py -n COUNT

The random files are taken from the output/mer directory for each topic. Topics
are taken from the config file. Each line is a summary of a document in JSON format,
containing an identifier, the year, the title, a summary (created from abstract or
text) and some entities of interest (skipping obscure ones like work-of-art). The -n
option determines how many summaries to create.

Output is written to files out/random-mer-TOPIC-NUMBER.json

This is just meant for eye-balling the data.

"""

import os, sys, json, random, argparse
import utils
import config


# number of random files to pick
DEFAULT_NUMBER = 25

# entity types to include
ENTITY_TYPES = ('PERSON', 'GPE', 'ORG', 'LOC', 'FAC')


def select_random(topic: str, topic_dir: str, limit: int):
    print(f'Selecting {limit} summaries from {topic}')
    files = os.listdir(topic_dir)
    random.shuffle(files)
    with open(f'out/random-mer-{topic}-{limit:04d}.json', 'w') as fh:
        for fname in files[:limit]:
            #print('   ', fname)
            content = json.loads(open(os.path.join(topic_dir, fname)).read())
            content_summary = {
                'id': content['name'],
                'year': content['year'],
                'title': content['title'],
                'summary': get_summary(content),
                'entities': get_entities(content) }
            fh.write(f'{json.dumps(content_summary)}\n')


def get_summary(content: dict):
    summary = content['abstract'] or content['content']
    return ' '.join(summary.split()[:2000])


def get_entities(content):
    entities = {}
    for entity_type in content['entities'].keys():
        if entity_type in ENTITY_TYPES:
            entities[entity_type] = list(content['entities'][entity_type].keys())
    return entities


def parse_args():
    help = 'Selecting random summaries from the merged data'
    parser = argparse.ArgumentParser(description=help)
    parser.add_argument('-n', help="number to select", type=int, default=DEFAULT_NUMBER)
    return parser.parse_args()


if __name__ == '__main__':

    args = parse_args()
    for topic in config.TOPICS:
        topic_dir = os.path.join(config.TOPICS_DIR, topic, 'output/mer')
        select_random(topic, topic_dir, args.n)
