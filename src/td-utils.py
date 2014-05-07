#!/usr/bin/env python

"""

A script for generating data needed by Typediff.

Usage:

$ td-utils.py make-data [grammar-alias]

If the grammar-alias is provided, data for just that grammar will be
generated, otherwise data for all grammars configured in config.py
will be generated.

Requires that DATAPATH in config.py is set to an appropriate value.

"""

from subprocess import Popen, PIPE

import sys
import os
import stat
import argparse
import cPickle

from config import *

import common
import delphin


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
    argparser.add_argument("command", metavar="COMMAND")
    argparser.add_argument("grammar", nargs='?', metavar="GRAMMAR")
    return argparser


def pickle_typesfile(grammar):
    sys.setrecursionlimit(10000)
    print "pickling {} hierarchy".format(grammar.alias)
    hierarchy = delphin.TypeHierarchy(grammar.types_path)
    cPickle.dump(hierarchy, open(grammar.pickle_path, 'wb'))


def build_grammar_image(grammar):
    if ACESRC is not None:
        os.chdir(ACESRC)
    print "compiling {}".format(grammar.alias)
    args = [ACEBIN, '-g', grammar.aceconfig, '-G', grammar.dat_path]
    process= Popen(args, stdout=PIPE, stderr=PIPE)
    out, err = process.communicate()
    
    if process.returncode != 0:
        msg = "Failed to build {}; ACE returned:\n{}"
        raise UtilError(msg.format(grammar.alias, err)) 
    
    permissions = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH
    os.chmod(grammar.dat_path, permissions)
         

def get_types_dump(grammar):
    print "dumping {} hierarchy".format(grammar.alias)
    args = [DUMPHIERARCHYBIN, grammar.dat_path]
    process= Popen(args, stdout=PIPE, stderr=PIPE)
    out, err = process.communicate()
    
    if err != '':
        msg = "Failed to dump {} hierarchy; dumphierarchy returned:\n{}"
        raise UtilError(msg.format(grammar.alias, err)) 
    
    with open(grammar.types_path, 'w') as f:
        f.write(out)
        

def make_data(grammar):
    build_grammar_image(grammar)
    get_types_dump(grammar)
    pickle_typesfile(grammar)


def main():
    arg = argparser().parse_args()
    
    try:
        if arg.command == "make-data":
            if not os.path.exists(DATAPATH):
                os.makedirs(DATAPATH)

            if arg.grammar is not None:
                grammars = common.get_grammars(GRAMMARLIST)
                grammar = common.Grammar(grammars[arg.grammar], DATAPATH)
                make_data(grammar)
            else:
                grammars = [grammar.Grammar(params, DATAPATH) 
                            for alias, params in GRAMMARS.items()]
                for grammar in grammars:
                    make_data(grammar)
    except UtilError as e:
        sys.stderr.write(e.msg+'\n')

        
if __name__ == "__main__":
    sys.exit(main())
