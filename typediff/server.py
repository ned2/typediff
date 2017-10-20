import json
import sys
from collections import defaultdict

from flask import Flask, request, jsonify

from .config import LOGONROOT, TREEBANKLIST, FANGORNPATH
from .gram import get_grammar, get_grammars
from .delphin import init_paths, JSONEncoder, load_hierarchy, Treebank

# set LOGONROOT environment variable in case it's not set
init_paths(logonroot=LOGONROOT)

from .typediff import web_typediff

# TODO:
# create a setup.py file with executable entry points for the main functions of:
# -- typediff.py, grammar-utils.py, type-stats.py, parseit.py, queryex.py, eval.py


app = Flask(__name__)
app.json_encoder = JSONEncoder


@app.route('/parse-types', methods=['POST'])
def parse_types():
    pinput = request.form.get('pos-items')
    ninput = request.form.get('neg-items')
    alias = request.form.get('grammar-name')
    count = request.form.get('count')
    supers = request.form.get('supers')
    desc = request.form.get('load-descendants') 
    fragments = request.form.get('fragments') 
    tagger = request.form.get('tagger')
  
    pos = pinput.strip().splitlines() if pinput is not None else []
    neg = ninput.strip().splitlines() if ninput is not None else []
    desc_flag = (desc == 'true')
    frags_flag = (fragments == 'true')
    supers_flag = (supers == 'true')
    grammar = get_grammar(alias)
    return jsonify(web_typediff(pos, neg, grammar, count, frags_flag,
                                supers_flag, desc_flag, tagger))


@app.route('/find-supers', methods=['POST'])
def find_supers():
    alias = request.form.get('grammar-name')
    types = json.loads(request.form.get('types'))
    supers = json.loads(request.form.get('supers'))

    # For each type provided, work out which of its supertypes
    # we are interested in -- ie are present after the diff
    
    descendants = {} # {supertype: set of descendents}
    grammar = get_grammar(alias)
    hierarchy = load_hierarchy(grammar.types_path)
    types_to_supers = defaultdict(list)

    for s in supers:
        descendants[s] = set(t.name for t in hierarchy[s].descendants())

    for this_type in types:
        for s, ds in descendants.items():
            if this_type in ds:
                types_to_supers[this_type].append([s, hierarchy[s].depth])
            
    return jsonify({'typesToSupers': types_to_supers})


@app.route('/load-data', methods=['POST'])
def load_data():
    return jsonify({ 
        'grammars'    : get_grammars(), 
        'treebanks'   : [Treebank(t) for t in TREEBANKLIST] , 
        'fangornpath' : FANGORNPATH,
    })
