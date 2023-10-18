"""Pinging the merged files

Prints a few statistics for each merged file in processed_mer for each topic.

"""

import os, sys, json
from config import TOPICS_DIR, TOPICS

data_dir = 'processed_mer'


def analyze_topic(topic: str):
    path = os.path.join(TOPICS_DIR, topic, data_dir)
    fnames = [os.path.join(path, fname) for fname in os.listdir(path)]
    for fname in sorted(fnames):
        json_obj = json.load(open(fname))
        abs_size = text_size(json_obj['abstract'])
        txt_size = text_size(json_obj['text'])
        entities = entities_size(json_obj['entities'])
        print(f'{topic}  {os.path.basename(fname)}  {abs_size:5d}  {txt_size:6d}  {entities:4d}')
    print(f'\nTotal documents in {topic}: {len(fnames)}')


def text_size(obj):
    if obj == None:
        return 0
    else:
        return len(obj)


def entities_size(obj):
    entities = 0
    for d in obj.values():
        entities += sum(d.values())
    return entities


if __name__ in '__main__':

    for topic in TOPICS:
        print()
        analyze_topic(topic)
