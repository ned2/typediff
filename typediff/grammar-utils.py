import sys
import os
import stat
import argparse
import pickle
from subprocess import Popen, PIPE

from .delphin import TypeHierarchy
from .config import ACESRC, ACEBIN, DUMPHIERARCHYBIN, DATAPATH
from .gram import get_grammar, get_grammars


"""
A convenience script for generating data needed Typediff. Other functions
may be added in the future.

Usage:

$ grammar-utils.py make-data [GRAMMARS ...]

If one or more grammar-alias is provided, data for just those grammar
will be generated, otherwise data for all grammars configured in
config.py will be generated.

Requires that DATAPATH in config.py is set to an appropriate value.
"""


class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return "Argument parsing error: {}".format(self.msg)


class UtilError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


def argparser():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("command", choices=('make-data'), metavar="COMMAND")
    argparser.add_argument("grammars", nargs=argparse.REMAINDER, metavar="GRAMMAR")
    return argparser


def pickle_typesfile(grammar):
    sys.setrecursionlimit(10000)
    print("pickling {} hierarchy".format(grammar.alias))
    hierarchy = TypeHierarchy(grammar.types_path)
    pickle.dump(hierarchy, open(grammar.pickle_path, 'wb'))


def build_grammar_image(grammar):
    if ACESRC is not None:
        os.chdir(ACESRC)
    print("compiling {}".format(grammar.alias))
    args = [ACEBIN, '-g', grammar.aceconfig, '-G', grammar.dat_path]
    process= Popen(args, stdout=PIPE, stderr=PIPE)
    out, err = process.communicate()

    if process.returncode != 0:
        msg = "Failed to build {}; ACE returned:\n{}"
        raise UtilError(msg.format(grammar.alias, err.decode('utf8'))) 
    
    permissions = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH
    os.chmod(grammar.dat_path, permissions)
         

def get_types_dump(grammar):
    print("dumping {} hierarchy".format(grammar.alias))
    args = [DUMPHIERARCHYBIN, grammar.dat_path]
    process= Popen(args, stdout=PIPE, stderr=PIPE)
    out, err = process.communicate()
    
    if process.returncode != 0:
        msg = "Failed to dump {} hierarchy; dumphierarchy returned:\n{}"
        raise UtilError(msg.format(grammar.alias, err.decode('utf8')))

    with open(grammar.types_path, 'w', encoding='utf8') as f:
        f.write(out.decode('utf8'))
        

def make_data(grammar):
    build_grammar_image(grammar)
    get_types_dump(grammar)
    pickle_typesfile(grammar)


def main():
    arg = argparser().parse_args()
    
    if arg.command == "make-data":
        if not os.path.exists(DATAPATH):
            os.makedirs(DATAPATH)

        if len(arg.grammars) == 0:
            grammars = get_grammars()
        else:
            grammars = [get_grammar(alias) for alias in arg.grammars]

        for grammar in grammars:
            try:
                make_data(grammar)
            except UtilError as e:
                sys.stderr.write(e.msg+'\n')
