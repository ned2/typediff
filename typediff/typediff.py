import sys
import os
import argparse
import json
import pickle
import functools
from itertools import chain

from . import delphin
from . import config
from . import gram


"""typediff.py
Author: Ned Letcher
https://github.com/ned2/typediff

Typediff is a tool to allow you to quickly explore the types used in
the processing of input by DELPH-IN grammars.

"""


HELP = """Usage:
$ typediff [options] GRAMMAR_NAME pos_sent1 pos_sent2 ... @ neg_sent1 neg_sent2 ...

Options:

The remainder of the options are only relevant to the command line mode:

-d 
  Operate in difference mode (default).

-i
  Operate in intersection mode.

-u
  Operate in union mode.
 
-n count
  The number of trees ACE is limited to returning.

--profiles

--frags
  Include fragment readings (only supported by ERG currently).

--all 
  Take types from all of the parses returned by ACE instead of just the best.

--supers
  Include the super types in the output.

--raw
  Don't sort and colorize the list of types.

"""


# TODO
# move help text into argparse
# update various config files to reflect LOGONROOT variable 


def argparser():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("grammar", metavar="GRAMMAR NAME")
    argparser.add_argument("--count", default=10)
    argparser.add_argument("--all", action='store_true')
    argparser.add_argument("--tagger")
    argparser.add_argument("--fragments", action='store_true')
    argparser.add_argument("--supers", action='store_true')
    argparser.add_argument("--profiles", action='store_true')
    argparser.add_argument("--raw", action='store_true')
    group = argparser.add_mutually_exclusive_group(required=False)
    group.add_argument("-i", action='store_true')
    group.add_argument("-d", action='store_true')
    group.add_argument("-u", action='store_true')
    argparser.add_argument("sentences", nargs=argparse.REMAINDER)
    return argparser


class ColorText(object):
    WHITE = '\033[97m'
    CYAN = '\033[96m'
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLACK = '\033[90m'
    END = '\033[0m'
    
    def __init__(self, text, color):
        self.text = text
        self.color = getattr(self, color.upper())
        
    def __str__(self):
        return ''.join((self.color, self.text, self.END))


def pretty_print_types(types, hierarchy):
    """
    Print the type list to the terminal, sorting and colorizing as
    specified by the TYPES variable.
    """
    def descendants(s):
        if s == 'other':
            return []
        else:
            return set(t.name for t in hierarchy[s].descendants())

    kinds = [(descendants(t), col) for t, _rgba, col in config.TYPES]

    def keyfunc(t):
        for i, x in enumerate(kinds): 
            if t.lstrip('^') in kinds[i][0]:
                return i
        return 1000

    types.sort(key=keyfunc)
    output = []

    for t in types:
        for ds, col in kinds:
            if t.lstrip('^') in ds:
                output.append(str(ColorText(t, col)))
                break
        else:
            output.append(t)
    
    return '\n'.join(output)


def compare_types(pos_types, neg_types, arg):
    if arg.d:
        types = pos_types - neg_types
    elif arg.i:
        # currently only works when there are pos and neg items
        types = set.intersection(pos_types, neg_types)
    else:
        types = pos_types | neg_types
    return types


@functools.lru_cache(maxsize=32)
def get_hierarchy(grammar):
    return delphin.load_hierarchy(grammar.types_path)


@functools.lru_cache(maxsize=32)
def load_descendants(grammar):
    hierarchy = get_hierarchy(grammar)
    desc_func = lambda x: set(t.name for t in hierarchy[x].descendants())
    kinds = [name for name, _rgba, _col in config.TYPES if name != 'other']
    descendants = {}
    for kind in kinds:
        for t in desc_func(kind):
            descendants[t] = kind
    return descendants


def type_data():
    return {t:{'rank':i+1, 'col':rgba}
            for i, (t, rgba, _col) in enumerate(config.TYPES)}


def typediff_web(pos_items, neg_items, opts):
    data = {
        'pos-items' : pos_items,
        'neg-items' : neg_items,
        'descendants' : load_descendants(opts.grammar) if opts.desc else False,
        'typeData': type_data(),
        'grammar': opts.grammar.alias,
        'treebank': opts.treebank,
    }

    if opts.supers:
        hierarchy = get_hierarchy(opts.grammar)
        for item in chain(pos_items, neg_items):
            item.load_supers(hierarchy)
                
    return data


def typediff(pos_items, neg_items, opts):
    """pos_items and neg_items are lists of either Fragment or Reading objects"""
    # currently assuming that the Reading objects are only coming from gold
    # profiles, therefore only one per item. otherwise we'd need to be using s
    # list of Reading objects or probably could be defining an ProfileItem
    # class that emulates the relevant interface to Fragment
    tfunc = lambda x:x.types.keys() if opts.all else x.best.types.keys()
    pos_types = set(chain.from_iterable(tfunc(x) for x in pos_items))
    neg_types = set(chain.from_iterable(tfunc(x) for x in neg_items))

    if len(pos_types) + len(neg_types) > 1:
        typelist = list(compare_types(pos_types, neg_types, opts))
    else:
        typelist = list(max(pos_types, neg_types))
        
    if opts.raw:
        return '\n'.join(typelist)

    hierarchy = delphin.load_hierarchy(opts.grammar.types_path)    
        
    if opts.supers:
        for group in (pos, neg):
            for item in group:
                item.load_supers(hierarchy)     
    
        sfunc = lambda x:x.supers
        pos_supers = set(chain.from_iterable(sfunc(x) for x in pos))
        neg_supers = set(chain.from_iterable(sfunc(x) for x in neg))
        supers = compare_types(pos_supers, neg_supers, opts)
        typelist.extend('^'+t for t in supers)

    return pretty_print_types(typelist, hierarchy)


def process_sentences(inputs, opts):
    def process(sentence):
        return delphin.Fragment(
            sentence,
            opts.grammar,
            fragments=opts.fragments, 
            count=opts.count,
            tnt=opts.get('tnt', False), 
            dat_path=opts.grammar.dat_path,  
            ace_path=config.ACEBIN,
            typifier=config.TYPIFIERBIN,
            logpath=config.LOGPATH
        )

    return [process(i) for i in inputs]


def process_profiles(queries, opts):
    # assume queries is a string of the form: PROFILE_PATH:opt_tsql_query
    sep = ':'
    items = []

    # support both list of queries and single query
    if isinstance(queries, str):
        queries = [queries]
        
    for query in queries:
        if query.find(sep) >= 0:
            path, condition = query.split(':')
            condition = None if condition == '' else condition
        else:
            path = query
            condition = None
        items.extend(process_gold_profile(
            path,
            condition=condition,
            grammar=opts.grammar,
        ))
    return items
    

def process_gold_profile(path, condition=None, grammar=None):
    return delphin.get_profile_results(
        [path],
        gold=True,
        grammar=grammar,
        condition=condition,
        typifier=config.TYPIFIERBIN
    )


def main():
    arg = argparser().parse_args()
    arg.grammar = gram.get_grammar(arg.grammar)

    if '@' in arg.sentences and not (arg.u or arg.i or arg.d):
        arg.d = True

    pos, neg = [], []

    # assign the inputs into pos and neg lists accordingly 
    stype = pos
    for s in arg.sentences:
        if s =='@':
            stype = neg
        else:
            stype.append(s)

    process_func = process_profiles if arg.profiles else process_sentences
    pos_items = process_func(pos, arg)
    neg_items = process_func(neg, arg)
    result = typediff(pos_items, neg_items, arg)
    print(result)


if __name__ == "__main__":
    main()
