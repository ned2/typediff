#!/usr/bin/env python2

from __future__ import division

import sys
import os
import argparse
from collections import Counter, defaultdict

import delphin
import config
import stats
import cPickle


def argparser():
    ap = argparse.ArgumentParser()
    ap.add_argument("grammar", metavar="GRAMMAR_NAME", help="The alias of a grammar found in config.py")
    ap.add_argument("profile", metavar="PROFILE", help="Path to profile")
    ap.add_argument("tbstats", metavar="TBSTATS_FILE", help="Path to treebank stats file")
    ap.add_argument("example", nargs='?', metavar="EXAMPLE", help="Query example")
    ap.add_argument("--descendants")
    ap.add_argument("--cutoff", type=float, default=.5)
    ap.add_argument("--best", type=int, default=1)
    ap.add_argument("--gold", action='store_true')
    return ap


def do_query(results, grammar, signature):
    found_items = set()
    
    for iid, readings in results.items():
        hit = True
        for t in signature:
            if t not in readings[0].types:
                hit = False
                break
        if hit:
            found_items.add(iid)

    return found_items


def get_type_sig(fragment, grammar, type_stats, num_trees, cutoff, supertype=None):
    signature = {}

    if supertype is not None:
        hierarchy = delphin.load_hierarchy(grammar.types_path)
        try:
            descendant_types = set(t.name for t in hierarchy[ancestor].descendants())
        except delphin.TypeNotFoundError as e:
            sys.stderr.write(str(e))
            sys.exit()
    
    for t in fragment.best.types:
        if supertype is not None and t not in descendant_types:
            continue
        ts = type_stats[t]
        if ts.items == 0:
            continue
        if t.startswith('"'):
            continue
        ts.coverage = ts.items/num_trees
        if ts.coverage <= cutoff:
            signature[t] = ts          
    return signature


def output(signature, items):
    lines = []

    for t,val in sorted(signature.items(), key=lambda x:x[1].coverage):
        lines.append('# {:.4f} {}'.format(val.coverage, t))

    return '\n'.join(lines) + '\n' + '\n'.join(str(x) for x in items)


def main():
    arg = argparser().parse_args()

    if arg.example is None:
        example = sys.stdin.read()
    else:
        example = arg.example

    num_trees = int(os.path.splitext(os.path.basename(arg.tbstats))[0].split('--')[-1])

    with open(arg.tbstats, 'rb') as f:
        type_stats = cPickle.load(f)

    grammar = config.load_grammar(arg.grammar)

    try:
        fragment = delphin.Fragment(example, grammar, count=1, typifier=config.TYPIFIERBIN)
    except delphin.AceError as e:
        print e
        return 

    signature = get_type_sig(fragment, grammar, type_stats, num_trees, arg.cutoff, arg.descendants)
    results = delphin.get_profile_results([arg.profile], 
                                          best=arg.best, 
                                          gold=arg.gold, 
                                          grammar=grammar,
                                          lextypes=False,
                                          typifier=config.TYPIFIERBIN)
    items = do_query(results, grammar, signature)
    print output(signature, items)


if __name__ == "__main__":
    sys.exit(main())
