import json
import sys
from collections import defaultdict

from flask import Flask, request, jsonify

from .config import LOGONROOT, TREEBANKLIST, FANGORNPATH, PROFILELIST
from .gram import get_grammar, get_grammars
from .delphin import (init_paths, JSONEncoder, load_hierarchy, Treebank,
                      dotdict, Profile)

# set LOGONROOT environment variable in case it's not set
init_paths(logonroot=LOGONROOT)

from .typediff import typediff_web, process_sentences, process_profiles

# TODO:
# create a setup.py file with executable entry points for the main functions of:
# -- typediff.py, grammar-utils.py, type-stats.py, parseit.py, queryex.py, eval.py


app = Flask(__name__)
app.json_encoder = JSONEncoder

PROFILES = {p['alias']: Profile(p) for p in PROFILELIST}

@app.route('/parse-types', methods=['POST'])
def parse_types():
    opts = dotdict({
        'count': int(request.form.get('count')),
        'tnt': request.form.get('tagger') == 'tnt2D',
        'grammar': get_grammar(request.form.get('grammar-name')),
        'desc': request.form.get('load-descendants') == 'true',
        'fragments': request.form.get('fragments') == 'true',
        'supers': request.form.get('supers')
    })

    pos_inputs = request.form.get('pos-items', '').strip().splitlines()
    neg_inputs = request.form.get('neg-items', '').strip().splitlines()
    pos_items = process_sentences(pos_inputs, opts)
    neg_items = process_sentences(neg_inputs, opts)
    return jsonify(typediff_web(pos_items, neg_items, opts))


@app.route('/process-profiles', methods=['POST'])
def process_the_profiles():
    pos_prof_name = request.form.get('pos-profile', '')
    neg_prof_name = request.form.get('neg-profile', '')
    pos_prof_filter = request.form.get('pos-profile-filter', '')
    neg_prof_filter = request.form.get('neg-profile-filter', '')

    pos_items, neg_items = [], []
    
    opts = dotdict({
        'desc': request.form.get('load-descendants') == 'true',
    })
    
    if pos_prof_name != '':
        prof = PROFILES[pos_prof_name]
        query = f'{prof.home}:{pos_prof_filter}'
        opts.grammar = get_grammar(prof.grammar)
        opts.treebank = prof.treebank
        pos_items = process_profiles(query, opts)

    if neg_prof_name != '':
        prof = PROFILES[neg_prof_name]
        query = f'{prof.home}:{pos_prof_filter}'
        opts.grammar = get_grammar(prof.grammar)
        opts.treebank = prof.treebank
        neg_items = process_profiles(query, opts)

    # for now assume that both profiles will be parsed using the
    # same grammar version, so use whichever grammar was assigned
    return jsonify(typediff_web(pos_items, neg_items, opts))


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
        'profiles' : [Profile(p) for p in PROFILELIST] 
    })
