from collections import Counter
from datetime import datetime


# average_token_length() and language_score() were originally taken from the
# utils.py file in https://github.com/lapps-xdd/xdd-docstructure


def average_token_length(number_of_tokens: int, tokens: Counter):
    """Returns the average token length in characters."""
    total_length = 0
    #print(tokens)
    for token, count in tokens.items():
        total_length += count * len(token)
    try:
        return total_length / number_of_tokens
    except ZeroDivisionError:
        return 0


def language_score(tokens: Counter, frequent_words: set) -> float:
    """This score measures what percentage of tokens are in a given list of
    frequent words. Returns a floating number between 0 and 1. This score
    tends to be below 0.1 when the text is not English or when it is more
    like a listing of results."""
    total_tokens = sum(tokens.values())
    in_frequent_words = sum([count for token, count in tokens.items()
                             if token in frequent_words])
    try:
        return in_frequent_words / total_tokens
    except ZeroDivisionError:
        return 0


def singletons_per_token(tokens: list) -> float:
    singletons = [t for t in tokens if len(t) == 1]
    try:
        return len(singletons) / len(tokens)
    except ZeroDivisionError:
        return 0.0


def timestamp():
    return datetime.strftime(datetime.now(), '%Y%m%d:%H%M%S')


def create_elastic_object(json_obj: dict, tags: list):
    """Creates a dictionary meant for bulk import into ElasticSearch."""
    elastic_obj = {"tags": tags}
    for field in ('name', 'year', 'title', 'authors', 'url', 'abstract',
                  'content', 'summary', 'terms'):
        if field in json_obj:
            elastic_obj[field] = json_obj[field]
        # TODO: still need to do this for some data, but should be deprecated soon
        elif field == 'content':
            elastic_obj[field] = json_obj['text']
    elastic_obj['entities'] = {}
    for entity_type, dictionary in json_obj.get('entities', {}).items():
        elastic_obj['entities'][entity_type] = \
            [(entity, str(count)) for entity, count in dictionary.items()]
    fix_terms(elastic_obj)
    return elastic_obj


def fix_terms(elastic_obj: dict):
    """Elastic search does not allow lists with different types so turning the integer
    and the float into strings."""
    # TODO: consider using dictionaries
    for term_triple in elastic_obj['terms']:
        term_triple[1] = str(term_triple[1])
        term_triple[2] = "%.6f" % term_triple[2]
