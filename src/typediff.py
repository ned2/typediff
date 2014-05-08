#!/usr/bin/env python2

import sys
import os
import argparse
import json
import cPickle
from itertools import chain

import delphin
import config


"""
Typediff is a tool to allow you to quickly explore the types used in
the processing of input by DELPH-IN grammars. 

Usage:
$ typediff.py [options] GRAMMAR_NAME pos_sent1 pos_sent2 ... @ neg_sent1 neg_sent2 ...

Options:

--json
 Tells typediff to return json data used for the web interface. In this mode
 the comparison of the types is not done by typediff as this is performed within 
 the browser.

--descendants
 In json mode, this instructs typediff to return a list of descentants for various
 high level supertypes used to sort and style the output list of types in the 
 inteface. This is optional as doing the hierarchy loopkup incurs a performace
 hit, and the results can be cached.


The remainder of the options are only relevant to the command line mode:

-d 
  Operate in difference mode (default).

-i
  Operate in intersection mode.

-u
  Operate in union mode.
 
-n count
  The number of trees ACE is limited to returning.

--frags
  Include fragment readigns (only supported by ERG currently).

--all 
  Take types from all of the parses returned by ACE instead of just the best.

--supers
  Include the super types in the output.

--raw
  Don't sort and colorize the list of types.
"""


# TODO
# update various config files to reflect LOGONROOT variable 

# add tnt option to typediff's interface
# work out best way to get tnt running on hum

# Recreate treebanks with new casing

# update typediff on hum

# send out email to developers email list.


def argparser():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("grammar", metavar="GRAMMAR NAME")
    argparser.add_argument("-n", default=10)
    argparser.add_argument("--all", action='store_true')
    argparser.add_argument("--frags", action='store_true')
    argparser.add_argument("--supers", action='store_true')
    argparser.add_argument("--json", action='store_true')
    argparser.add_argument("--descendants", action='store_true')
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

    kinds = [(descendants(t), tc) for t,tc,wc in config.TYPES]

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


def export_json(pos_input, neg_input, grammar, count, frags, supers, load_desc):
    hierarchy = delphin.load_hierarchy(grammar.types_path)

    parse = lambda x: delphin.Fragment(x, grammar, ace_path=config.ACEBIN,
                                       dat_path=grammar.dat_path,
                                       count=count,
                                       typifier=config.TYPIFIERBIN,
                                       fragments=frags, 
                                       logpath=config.LOGPATH) 
    try:
        pos  = [parse(x) for x in pos_input]
        neg  = [parse(x) for x in neg_input]
    except(delphin.AceError) as err:
        data = {
            'succes' : False, 
            'error'  : str(err),
            'PATH'   : os.environ['PATH']
        }

        return json.dumps(data)

    if supers:
        for p in pos: p.load_supers(hierarchy)
        for n in neg: n.load_supers(hierarchy)

    data = {
        'success': True,
        'pos-items' : pos,
        'neg-items' : neg,
    }

    if load_desc:
        descendants = lambda x: set(t.name for t in hierarchy[x].descendants())
        types = ('sign', 'head', 'synsem', 'cat', 'relation', 'predsort') 
        data['descendants'] = {t:descendants(t) for t in types}
    else:
        data['descendants'] = False

    data['typeOrdering'] = [t for t, tc, wc in config.TYPES] 
    data['typeColors'] = {t:wc for t, tc, wc in config.TYPES}
    return json.dumps(data, cls=delphin.JSONEncoder)


def typediff(pos_input, neg_input, grammar, arg):
    parse = lambda x: delphin.Fragment(x, grammar, ace_path=config.ACEBIN, 
                                       dat_path=grammar.dat_path,  
                                       count=arg.n,
                                       typifier=config.TYPIFIERBIN,
                                       fragments=arg.frags, 
                                       logpath=config.LOGPATH)

    pos  = [parse(x) for x in pos_input]
    neg  = [parse(x) for x in neg_input]
    hierarchy = None

    if arg.all:
        tfunc = lambda x:x.types.keys()
        sfunc = lambda x:x.supers
    else:
        tfunc = lambda x:x.best.types.keys()
        sfunc = lambda x:x.best.supers

    pos_types = set(chain.from_iterable(tfunc(x) for x in pos))
    neg_types = set(chain.from_iterable(tfunc(x) for x in neg))

    if len(pos) + len(neg) > 1:
        typelist = list(compare_types(pos_types, neg_types, arg))
    else:
        typelist = list(max(pos_types, neg_types))

    if arg.supers:
        hierarchy = delphin.load_hierarchy(grammar.types_path)
        for p in pos: p.load_supers(hierarchy)
        for n in neg: n.load_supers(hierarchy)
        pos_supers = set(chain.from_iterable(sfunc(x) for x in pos))
        neg_supers = set(chain.from_iterable(sfunc(x) for x in neg))
        supers = compare_types(pos_supers, neg_supers, arg)
        typelist.extend('^'+t for t in supers)

    if arg.raw:
        return '\n'.join(typelist)
    else:
        if hierarchy is None:
            hierarchy = delphin.load_hierarchy(grammar.types_path)
        return pretty_print_types(typelist, hierarchy)


def main():
    arg = argparser().parse_args()
    grammar = config.load_grammar(arg.grammar)

    if '@' in arg.sentences and not (arg.u or arg.i or arg.d):
        arg.d = True

    pos = []
    neg = []
    stype = pos

    for s in arg.sentences:
        if s =='@':
            stype = neg
        else:
            stype.append(s)
                
    try:
        if arg.json:
            print export_json(pos, neg, grammar, arg.n, arg.frags, arg.supers, arg.descendants)
        else:
            print typediff(pos, neg, grammar, arg)
    except(delphin.AceError) as err:
        sys.stderr.write(str(err))
        return 2


if __name__ == "__main__":
    sys.exit(main())
