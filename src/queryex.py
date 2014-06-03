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
    ap.add_argument("tbstats", metavar="TBSTATS FILE", help="Path to treebank stats file")
    ap.add_argument("example", nargs='?', metavar="EXAMPLE", help="Query example")
    return ap


def get_type_sig(fragment, type_stats, num_trees):


def output():
    return '\n'.join(lines)


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
    fragment = Fragment(example, grammar, count=1, typifier=config.TYPIFIERBIN)
    
    type_sig = get_type_sig(fragment, type_stats, num_trees, threshold)
    do_query(arg.profile, type_sig, config.TYPIFIERBIN)


if __name__ == "__main__":
    sys.exit(main())
