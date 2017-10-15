#!/USSR/bin/env python3

import json
import sys
from collections import defaultdict

from flask import Flask, request

import config
import delphin
import gram

# set LOGONROOT environment variable in case it's not set
delphin.init_paths(logonroot=config.LOGONROOT)

from . import typediff


app = Flask(__name__)
app.config["APPLICATION_ROOT"] = "/api"


@app.route('/parse-types', methods=['POST'])
def parse_types():
    pinput = request.form.getvalue('pos-items')
    ninput = request.form.getvalue('neg-items')
    alias = request.form.getvalue('grammar-name')
    count = request.form.getvalue('count')
    supers = request.form.getvalue('supers')
    desc = request.form.getvalue('load-descendants') 
    fragments = request.form.getvalue('fragments') 
    tagger = request.form.getvalue('tagger')
  
    pos = pinput.strip().splitlines() if pinput is not None else []
    neg = ninput.strip().splitlines() if ninput is not None else []
    desc_flag = (desc == 'true')
    frags_flag = (fragments == 'true')
    supers_flag = (supers == 'true')
    grammar = gram.get_grammar(alias)
    return typediff.export_json(pos, neg, grammar, count, frags_flag,
                                supers_flag, desc_flag, tagger) 


@app.route('/find-supers', methods=['POST'])
def find_supers():
    alias = request.form.getvalue('grammar-name')
    types = json.loads(request.form.getvalue('types'))
    supers = json.loads(request.form.getvalue('supers'))

    # For each type provided, work out which of its supertypes
    # we are interested in -- ie are present after the diff
    
    descendants = {} # {supertype: set of descendents}
    grammar = gram.get_grammar(alias)
    hierarchy = delphin.load_hierarchy(grammar.types_path)
    types_to_supers = defaultdict(list)

    for s in supers:
        descendants[s] = set(t.name for t in hierarchy[s].descendants())

    for this_type in types:
        for s, ds in descendants.items():
            if this_type in ds:
                types_to_supers[this_type].append([s, hierarchy[s].depth])
            
    return json.dumps({'typesToSupers': types_to_supers} , cls=delphin.JSONEncoder)


@app.route('/load-data', methods=['POST'])
def load_data():
    result = { 
        'grammars'    : gram.get_grammars(), 
        'treebanks'   : [delphin.Treebank(t) for t in config.TREEBANKLIST] , 
        'fangornpath' : config.FANGORNPATH,
        'jsonpath'    : config.JSONPATH,
    }
    return json.dumps(result, cls=delphin.JSONEncoder)



if __name__ == "__main__":
    app.run()
