"""

Select random files from a topic and write a JSON file that can serve as a ElasticSearch
bulk upload.

$ python random.py --topic TOPIC --tags TAGS -n N

This hands in the name of the topic, a comma-separated list of tags and a count (the
default is 25). The topic needs to be defined in the config file (and the merged files
for it need to be where the config file expects them to be).

Output is written to out/random-ela-TOPIC-NUMBER.json

Note that the output file is not exactly json, rather they are files where each line
is a json object (as required for an ELastiicSearch bulk import).

With the test domains as of March 2024, we use these invocations:

$ python get_random_ela.py --topic biomedical --tags biomedical -n 100
$ python get_random_ela.py --topic climate-change-modeling --tags climate-change -n 100
$ python get_random_ela.py --topic cultivars --tags cultivars -n 100
$ python get_random_ela.py --topic geoarchive --tags geoarchive -n 100
$ python get_random_ela.py --topic mars --tags mars -n 100
$ python get_random_ela.py --topic molecular-physics --tags molecular-physics -n 100
$ python get_random_ela.py --topic random --tags random -n 100

"""

import os, json, random, argparse
import utils
import config


def select_random(topic: str, topic_dir: str, tags: list, limit: int):
    outfile = f'out/random-ela-{topic}-{limit:04d}.json'
    print(f'Selecting {limit} samples from {topic}')
    print(f'Writing results to {outfile}')
    files = os.listdir(topic_dir)
    random.shuffle(files)
    with open(outfile, 'w') as fh:
        for fname in files[:limit]:
            content = json.loads(open(os.path.join(topic_dir, fname)).read())
            elastic_obj = utils.create_elastic_object(content, tags)
            # TODO: should scramble the contents of the content field
            # TODO: do this governed by an option
            fh.write(json.dumps({"index": {"_id": content['name']}}) + '\n')
            fh.write(json.dumps(elastic_obj) + '\n')


def parse_args():
    def tags(tagstring: str):
        return tagstring.split(',')
    parser = argparse.ArgumentParser(description='Selecting random files')
    parser.add_argument('--topic', help="one of the topics from the config file")
    parser.add_argument(
        '--tags', help="comma-separated list of tags", default=[], type=tags)
    parser.add_argument('-n', help="number to select", type=int, default=25)
    return parser.parse_args()


if __name__ == '__main__':

    args = parse_args()
    topic_dir = os.path.join(config.TOPICS_DIR, args.topic, 'output/mer')
    select_random(args.topic, topic_dir, args.tags, args.n)
