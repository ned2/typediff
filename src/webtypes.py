#!/usr/bin/env python3


import cgitb
cgitb.enable(logdir='/tmp')

import json
import cgi
import sys
from collections import defaultdict

import config
import delphin

# Probably running with Apache, so set logonroot manually.
delphin.init_paths(logonroot=config.LOGONROOT)

import typediff


def parse_types_query(form):
    pinput = form.getvalue('pos-items')
    ninput = form.getvalue('neg-items')
    alias = form.getvalue('grammar-name')
    count = form.getvalue('count')
    supers = form.getvalue('supers')
    desc = form.getvalue('load-descendants') 
    fragments = form.getvalue('fragments') 
    tagger = form.getvalue('tagger')
  
    pos = pinput.strip().splitlines() if pinput is not None else []
    neg = ninput.strip().splitlines() if ninput is not None else []
    desc_flag = (desc == 'true')
    frags_flag = (fragments == 'true')
    supers_flag = (supers == 'true')
    grammar = config.get_grammar(alias)
    return typediff.export_json(pos, neg, grammar, count, frags_flag, supers_flag, desc_flag, tagger) 


def find_supers_query(form):
    alias = form.getvalue('grammar-name')
    kinds = form.getvalue('kinds')
    kinds = json.loads(kinds)
    return find_supers(alias, kinds)


def load_data_query():
    result = { 
        'grammars'    : config.get_grammars(), 
        'treebanks'   : [delphin.Treebank(t) for t in config.TREEBANKLIST] , 
        'fangornpath' : config.FANGORNPATH,
        'jsonpath'    : config.JSONPATH,
    }
    return json.dumps(result, cls=delphin.JSONEncoder)


def find_supers(alias, kinds):
    descendants = {}
    grammar = config.get_grammar(alias)
    hierarchy = delphin.load_hierarchy(grammar.types_path)
    types_to_supers = defaultdict(list)

    for kind, data in kinds.items():
        types = data['types']
        supers = data['supers']

        for s in supers:
            descendants[s] = set(t.name for t in hierarchy[s].descendants())

        for t in types:
            for s, ds in descendants.items():
                if t in ds:
                    types_to_supers[t].append([s, hierarchy[s].depth])

    result = { 'success'      : True,
               'typesToSupers': types_to_supers }
 
    return json.dumps(result, cls=delphin.JSONEncoder)


def test(json_str):
    jkinds = json.loads(json_str)
    find_supers('terg', jkinds)


def main():
    form = cgi.FieldStorage()
    query = form.getvalue('query')

    print('Content-Type: application/json; charset=utf-8\n\n')

    if query == 'parse-types':  
        print(parse_types_query(form))
    elif query == 'find-supers':
        print(find_supers_query(form))
    elif query == 'load-data':
        print(load_data_query())


if __name__ == "__main__":
    sys.exit(main())
