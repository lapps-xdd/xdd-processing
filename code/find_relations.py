"""find_relations.py

Uses the pos results of spaCy processing (see ner.py) and creates lists of
relations ordered on TF-IDF score relative to the three domains.

Usage

$ python find_relations.py [LIMIT]

Output is written to three files:

out/relations-biomedical.txt
out/relations-geoarchive.txt
out/relations-molecular_physics.txt

"""

import os, sys, math, collections
from tqdm import tqdm
from config import TOPICS, data_directory


POS_SUBDIR = 'processed_pos'


def main(limit: int):
    verbs = {}
    for topic in TOPICS:
        # TODO: directories should not be hard-coded, use values in config file
        pos_dir = data_directory(topic, POS_SUBDIR)
        print(f'\nReading {pos_dir}...')
        verbs[topic] = collect_verbs_in_topic(pos_dir, topic, limit)
    print(f'\nCalculating TF-IDF scores...')
    tfidfs = calculate_tfidf(verbs)
    print(f'Printing relations...')
    print_tfidfs(tfidfs)
    print()


def collect_verbs_in_topic(pos_dir: str, topic: str, limit: int):
    verbs = collections.Counter()
    docs = os.listdir(pos_dir)
    for doc in tqdm(list(sorted(docs))[:limit]):
        try:
            verbs.update(count_verbs(pos_dir, doc))
        except Exception as e:
            print(f'{doc}\t{e}\n')
    return verbs


def count_verbs(topic_dir: str, doc: str):
    fname = os.path.join(topic_dir, doc)
    with open(fname) as fh:
        verbs = []
        for line in fh:
            fields = line.strip().split('\t')
            # fields: (i, token, lemma, pos1, pos2)
            if len(fields) == 5 and fields[3] == 'VERB':
                verbs.append(fields[2])
        return collections.Counter(verbs)


def calculate_tfidf(verbs):
    tfidfs = {}
    for topic in verbs:
        relations = calculate_tfidf_for_topic(topic, verbs)
        tfidfs[topic] = relations
    return tfidfs


def calculate_tfidf_for_topic(topic, verbs):
    relations = []
    verb_count_for_topic = sum(verbs[topic].values())
    number_of_topics = len(verbs)
    for verb in verbs[topic]:
        frequency = verbs[topic][verb]
        number_of_topics_with_verb = sum([1 for t in verbs if verb in verbs[t]])
        tf = frequency / verb_count_for_topic
        idf = math.log(number_of_topics / number_of_topics_with_verb)
        tfidf = tf * idf
        relations.append((tfidf, frequency, verb))
        #print(f'{verb:15}  {frequency:3d}  {tf:.4f}  {idf:.4f}  {tfidf:.4f}')
    return reversed(sorted(relations))


def print_tfidfs(tfidfs):
    for topic in tfidfs:
        relations = tfidfs[topic]
        with open(f'out/relations-{topic}.txt', 'w') as fh:
            for tfidf, freq, rel in relations:
                if freq > 1:
                    fh.write(f'{tfidf:.8f}  {freq:4d}  {rel}\n')


if __name__ == '__main__':

    limit = int(sys.argv[1]) if len(sys.argv) > 1 else sys.maxsize
    main(limit)
