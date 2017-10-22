import sys
import os
import argparse
import json
import pickle
from itertools import chain

from . import delphin
from . import config
from . import gram


"""typediff.py
Author: Ned Letcher
https://github.com/ned2/grammalytics

Typediff is a tool to allow you to quickly explore the types used in
the processing of input by DELPH-IN grammars.

For usage, run parseit.py --help
"""


HELP = """Usage:
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
    argparser.add_argument("-n", default=10)
    argparser.add_argument("--all", action='store_true')
    argparser.add_argument("--tagger")
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


def web_typediff(pos_input, neg_input, grammar, count, frags, supers, load_desc, 
                tagger):
    hierarchy = delphin.load_hierarchy(grammar.types_path)
    parse = lambda x: delphin.Fragment(x, grammar, ace_path=config.ACEBIN,
                                       dat_path=grammar.dat_path,
                                       count=count,
                                       tnt=(tagger=='tnt'),
                                       typifier=config.TYPIFIERBIN,
                                       fragments=frags, 
                                       logpath=config.LOGPATH)
    try:
        pos = [parse(x) for x in pos_input]
        neg = [parse(x) for x in neg_input]
    except(delphin.AceError) as err:
        data = {
            'succes' : False, 
            'error'  : err.msg,
        }

        return json.dumps(data)

    if supers:
        for p in pos:
            p.load_supers(hierarchy)
        for n in neg:
            n.load_supers(hierarchy)

    data = {
        'success': True,
        'pos-items' : pos,
        'neg-items' : neg,
    }

    if load_desc:
        descendants = lambda x: set(t.name for t in hierarchy[x].descendants())
        kinds = [name for name, _rgba, _col in config.TYPES if name != 'other']
        data['descendants'] = {}

        for kind in kinds:
            for t in descendants(kind):
                data['descendants'][t] = kind
    else:
        data['descendants'] = False

    data['typeData'] = {t:{'rank':i+1, 'col':rgba}
                        for i, (t, rgba, _col) in enumerate(config.TYPES)} 
    return data


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
    grammar = gram.get_grammar(arg.grammar)

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
            print(export_json(pos, neg, grammar, arg.n, arg.frags, arg.supers, 
                              arg.descendants, arg.tagger))
        else:
            print(typediff(pos, neg, grammar, arg))
    except(delphin.AceError) as err:
        sys.stderr.write(err.msg)
        return 2
