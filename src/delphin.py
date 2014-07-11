import os
import sys
import re
import math
import codecs
import itertools
import cPickle
import json
import time

from collections import Counter, defaultdict
from subprocess import Popen, PIPE


try:
    from lxml import etree
except ImportError:
    try:
        import xml.etree.cElementTree as etree
    except ImportError:
        import xml.etree.ElementTree as etree


def init_paths(logonroot=None):
    """
    Set various paths. If logonroot argument omitted, uses LOGONROOT
    environment variable.
    """
    global LOGONROOT
    global LOGONBIN
    global TSDBHOME
    global ACEBIN
    global LOGONREGPATH

    LOGONROOT = logonroot

    if LOGONROOT is None:
        LOGONROOT = os.environ.get('LOGONROOT')

    if LOGONROOT is None:
        home = os.environ.get('HOME')
        if home is not None:
            LOGONROOT = os.path.join(home, 'logon')
        else:
            sys.stderr.write("Warining: LOGONROOT environment variable not set.")
            LOGONROOT = ''

    LOGONBIN = os.path.join(LOGONROOT, 'bin')
    ACEBIN = os.path.join(LOGONROOT, 'lingo', 'answer', 'bin', 'linux.x86.64', 'ace')
    TSDBHOME = os.environ.get('TSDBHOME')
    LOGONREGPATH = os.path.join(LOGONROOT, 'etc', 'registry')
    
    if TSDBHOME is None:
        TSDBHOME = os.path.join(LOGONROOT, 'lingo', 'lkb', 'src', 'tsdb', 'home') 


GRAMMAR_NAMES = {
    'erg'  : 'ERG',
    'terg' : 'Trunk ERG',
    'gg'   : 'GG',
    'jacy' : 'Jacy',
    'srg'  : 'SRG',
    'hag'  : 'Hausa Gramma',
}


# Virtual profiles found in the logon repository
# TODO write a funciton to actually read virtual profiles
VIRTUAL_PROFILES = {
    'ws' : ('WeScience', ['ws01', 'ws02', 'ws03', 'ws04', 'ws05', 'ws06', 'ws07',
                          'ws08', 'ws09', 'ws10', 'ws11', 'ws12', 'ws13']),
    'vm' : ('Verbmobil', ['vm6', 'vm13', 'vm31', 'vm32']),
    'tc' : ('Tanaka Corpus', ['tc-000', 'tc-001', 'tc-002', 'tc-003', 'tc-004', 
                              'tc-005', 'tc-006', 'tc-007', 'tc-008', 'tc-009', 
                              'tc-010', 'tc-011', 'tc-012', 'tc-013', 'tc-014', 
                              'tc-015', 'tc-016', 'tc-017', 'tc-018', 'tc-019', 
                              'tc-020', 'tc-021', 'tc-022', 'tc-023', 'tc-024', 
                              'tc-025', 'tc-026', 'tc-027', 'tc-028', 'tc-029', 
                              'tc-030', 'tc-031', 'tc-032', 'tc-033', 'tc-034', 
                              'tc-035', 'tc-036', 'tc-037', 'tc-038', 'tc-039', 
                              'tc-040', 'tc-041', 'tc-042', 'tc-043', 'tc-044', 
                              'tc-045', 'tc-046', 'tc-047', 'tc-048', 'tc-049', 
                              'tc-050', 'tc-051', 'tc-052', 'tc-053', 'tc-054', 
                              'tc-055', 'tc-056', 'tc-057', 'tc-058', 'tc-059', 
                              'tc-060', 'tc-061', 'tc-062', 'tc-063', 'tc-064', 
                              'tc-065', 'tc-066', 'tc-067', 'tc-068', 'tc-069', 
                              'tc-070', 'tc-071', 'tc-072', 'tc-073', 'tc-074', 
                              'tc-075', 'tc-076', 'tc-077', 'tc-078', 'tc-079', 
                              'tc-080', 'tc-081', 'tc-082', 'tc-083', 'tc-084', 
                              'tc-085', 'tc-086', 'tc-087', 'tc-088', 'tc-089', 
                              'tc-090', 'tc-091', 'tc-092', 'tc-093', 'tc-094', 
                              'tc-095', 'tc-096', 'tc-097', 'tc-098', 'tc-099', 
                              'tc-100']),
    'db' : ('DeepBank', ['wsj00a', 'wsj01a', 'wsj02a', 'wsj03a', 'wsj04b', 
                         'wsj05a', 'wsj05e', 'wsj06d', 'wsj07d', 'wsj09b', 
                         'wsj10b', 'wsj11b', 'wsj12a', 'wsj13a', 'wsj13e', 
                         'wsj14d', 'wsj15c', 'wsj16b', 'wsj16f', 'wsj17d', 
                         'wsj18d', 'wsj19c', 'wsj20c', 'wsj21b', 'wsj00b', 
                         'wsj01b', 'wsj02b', 'wsj03b', 'wsj04c', 'wsj05b', 
                         'wsj06a', 'wsj07a', 'wsj07e', 'wsj09c', 'wsj10c', 
                         'wsj11c', 'wsj12b', 'wsj13b', 'wsj14a', 'wsj14e', 
                         'wsj15d', 'wsj16c', 'wsj17a', 'wsj18a', 'wsj18e', 
                         'wsj19d', 'wsj20d', 'wsj21c', 'wsj00c', 'wsj01c', 
                         'wsj02c', 'wsj03c', 'wsj04d', 'wsj05c', 'wsj06b', 
                         'wsj07b', 'wsj08a', 'wsj09d', 'wsj10d', 'wsj11d', 
                         'wsj12c', 'wsj13c', 'wsj14b', 'wsj15a', 'wsj15e', 
                         'wsj16d', 'wsj17b', 'wsj18b', 'wsj19a', 'wsj20a', 
                         'wsj21', ' wsj21d', 'wsj00d', 'wsj01d', 'wsj02d', 
                         'wsj04a', 'wsj04e', 'wsj05d', 'wsj06c', 'wsj07c', 
                         'wsj09a', 'wsj10a', 'wsj11a', 'wsj11e', 'wsj12d', 
                         'wsj13d', 'wsj14c', 'wsj15b', 'wsj16a', 'wsj16e', 
                         'wsj17c', 'wsj18c', 'wsj19b', 'wsj20b', 'wsj21a']),
            }


class TsdbError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class LexLookupError(Exception):
    def __init__(self, msg):
        self.msg = msg


class DerivationError(Exception):
    def __init__(self, msg):
        self.msg = msg


class TypeNotFoundError(Exception):
    def __init__(self, t):
        self.type = t

    def __str__(self):
        return "{} not found in the hierarchy.\n".format(self.type)


class AceError(Exception):
    def __init__(self, prog, msg):
        self.prog = prog
        self.msg = msg

    def __str__(self):
        return "{} returned:\n{}".format(self.prog, self.msg)


class TypeStats(object):
    
    def __init__(self):
        self.counts = 0
        self.items = 0

    def update(self, counts):
        self.items += 1
        self.counts += counts


class Treebank(object):
    def __init__(self, params):
        for param, val in params.items():
            setattr(self, param, val)       


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, ConfigGrammar):
            return obj.json()
        if isinstance(obj, Treebank):
            return obj.__dict__
        if isinstance(obj, Reading):
            data = obj.__dict__
            data['tree'] = data['json_tree']
            del data['json_tree']
            del data['grammar']
            return data
        if isinstance(obj, Tree):
            return obj.ptb()
        if isinstance(obj, Token):
            return obj.__dict__
        if isinstance(obj, Fragment):
            data = obj.__dict__
            data['grammar'] = data['grammar'].alias
            del data['log_lines']
            del data['logpath']
            return data
        if isinstance(obj, TypeStats):
            return obj.__dict__
        return json.JSONEncoder.default(self, obj)


class Fragment(object):
    def __init__(self, text, grammar, ace_path=None, dat_path=None, count=None, 
                 tnt=False, typifier=None, fragments=False, logpath=None, 
                 cache=False, lextypes=True):
        self.input = text
        self.logpath = logpath
        self.log_lines = [time.strftime("%Y-%m-%d %H:%M:%S")]

        try:
            # supplied grammar is a Grammar object
            alias = grammar.alias
            self.grammar = grammar
        except AttributeError:
            # supplied grammar was just an alias
            self.grammar = LogonGrammar(grammar)

        if dat_path is not None:
            self.grammar.dat_path = dat_path

        if ace_path is None:
            ace_path = ACEBIN

        if self.grammar.lex_entries is None:
            lextypes = False

        self.preprocess()
        self.parse(ace_path, self.grammar.dat_path, count, fragments, tnt, typifier, cache, lextypes)

        if logpath is not None:
            self.write_log()

    def parse(self, ace_path, dat_path, count, fragments, tnt, typifier, cache, lextypes):
        env = dict(os.environ)
        env['LC_ALL'] = 'en_US.UTF-8'
        args = [ace_path, '-g', dat_path]

        if tnt:
            # If we have a logon installation, set PATH and model path 
            # to use this. Otherwise use the tnt tagger packaged with grammalytics
            if os.path.exists(LOGONBIN):
                env['PATH'] = "{}:{}".format(os.environ['PATH'], LOGONBIN) 
                model_path = os.path.join(LOGONROOT, 'coli', 'tnt', 'models', 'wsj.tnt') 
            else:
                thisdir = os.path.dirname(os.path.realpath(__file__))
                taggerpath = os.path.join(thisdir, '..', 'tagger')
                taggerbin = os.path.join(taggerpath, 'bin')
                env['PATH'] = "{}:{}".format(os.environ['PATH'], taggerbin) 
                model_path = os.path.join(taggerpath, 'coli', 'tnt', 'models', 'wsj.tnt') 
            args.append('--tnt-model')
            args.append(model_path)

        if count is not None:
            args.append('-n')
            args.append(str(count))

        if self.yy_input:
            args.append('-y')
            input_str = self.yy_input
        else:
            input_str = self.input

        if not fragments:
            if self.grammar.alias.startswith('erg') or self.grammar.alias.startswith('terg'):
                args.append('-r')
                args.append('root_strict root_informal')
                
        process = Popen(args, stdout=PIPE, stderr=PIPE, stdin=PIPE, env=env)
        out, err = process.communicate(input=input_str.encode('utf8'))
        lines = out.strip().split('\n')
        status = lines[0]
        readings = lines[1:]
        self.stderr = err

        if process.returncode != 0 or out.startswith('SKIP'):
            ace_error_str = '\n'.join([status, err])
            self.log_lines.append(ace_error_str + '\n\n')
            raise AceError('ACE', ace_error_str)
        else: 
            self.log_lines.append(out)
 
        self.readings = []
        for i,reading in enumerate(readings):
            mrs, derivation = reading.split(';', 1)
            r = Reading(derivation.strip(), resultid=i, grammar=self.grammar, 
                        mrs=mrs.strip(), lextypes=lextypes, typifier=typifier, 
                        cache=cache)

            self.readings.append(r)

    def preprocess(self):
        self.yy_input = False

        if self.grammar.alias == 'jacy':
            try:
                import jpn2yy
                self.yy_input = jpn2yy.jp2yy(self.string)
            except (ImportError, RuntimeError, UnicodeDecodeError) as e:
                # if MeCab is not installed or incorrectly installed do nothing
                string = 'Error: {}\nCheck if MeCab is installed correctly.\n'
                msg = string.format(str(e))
                sys.stderr.write(msg+'\n')
                self.log_lines.append(msg)
        
    def load_supers(self, hierarchy):
        for reading in self.readings:
            reading.supers = get_supers(reading.types, hierarchy)

    @property
    def types(self):
        return set(chain.from_iterable(x.types for x in self.readings))

    @property
    def best(self):
        return self.readings[0]

    def write_log(self):
        try:
            with open(self.logpath, 'a+') as f:
                f.write('\n'.join(self.log_lines))
        except IOError:
            # In case apache does not have write permissions
            sys.stderr.write("Cannot write to {}.\n".format(self.logpath))
            pass


class Reading(object):

    def __init__(self, derivation, iid=None, resultid=None, grammar=None, 
                 mrs=None, ptokens=None, lextypes=True, dat_path=None, 
                 typifier=None, cache=False, pspans=[]):
        self.iid = iid
        self.resultid = resultid
        self.mrs = mrs

        try:
            # supplied grammar is a Grammar object
            alias = grammar.alias
            self.grammar = grammar
        except AttributeError:
            # supplied grammar was just an alias
            self.grammar = LogonGrammar(grammar)

        if dat_path is not None:
            self.grammar.dat_path = dat_path

        if cache or len(pspans) > 0:
            # if the cache option has been explicitly specified or if
            # there are phenomenon spans to align to edges, then
            # cache the derivation substrings inside Tree objects
            cache_derivations = True
        else:
            cache_derivations = False

        self.tree = parse_derivation(derivation, cache=cache_derivations)

        self.lex_entries = Counter()
        self.rules = Counter()
        self.types = Counter()       
        self.supers = [] 
        self._lextypes = None
        self.tokens = []
        self.subtrees = []
        self.root_condition = None

        # initial parse of Tree object, extract tokens and align spans
        self._process_tree(pspans, lextypes)

        # restore case to the tokens
        if ptokens is not None:
            self._restore_token_case(ptokens)

        # collect stats from tree/subtree
        if pspans:
            self._tree_stats(*self.subtrees)
        else:
            self._tree_stats(self.tree)

        # reconstruct tree/subtree and collect stats
        if typifier is not None:
            if len(pspans) > 0:
                # only reconstruct matching phenomenon spans
                for subtree in self.subtrees:
                    self._reconstruct(subtree.derivation, typifier)
            else:
                # reconstruct entire tree
                self._reconstruct(derivation, typifier)

    def _process_tree(self, pspans, lextypes):
        """Extracts tokens and aligns any spans to derivations"""
        if self.tree.start == -1:
            # Parse from PET which inculdes top level root
            # condition. Record and then discard this node of the
            # tree.
            self.root_condition = self.tree.label
            self.tree = self.tree.children[0]

        lex_lookup = self.grammar.lex_lookup if lextypes else None
        self.tokens, subtrees = self.tree.process(lex_lookup=lex_lookup)

        if len(pspans) > 0: 
            vstartchars = {}
            vendchars = {}
            for token in self.tokens:
                vstartchars[token.start] = token.from_char
                vendchars[token.end] = token.to_char

            # find closest matching trees for any pspans provided
            for start, end in pspans:
                sumdiff = lambda tree:abs(vstartchars[tree.start] - start) + abs(vendchars[tree.end] - end)
                match = min(subtrees, key=sumdiff)

                # Ensure that we're getting the highest node for this
                # span relevant for sequences of single child
                # derivation Has not been checked to see if working as
                # phenomena investigated currently doesn't tend to
                # involve singly-branching derivations.
                while True:
                    if match.parent is None:
                        break
                    elif sumdiff(match.parent) == sumdiff(match):
                        match = match.parent
                    else:
                        break

                match.diff = sumdiff(match)                  
                self.subtrees.append(match)

    def _tree_stats(self, *trees):
        """
        Process the (sub)tree we got back from the parse of the derivation.
        If lextypes is True, the lexicon is consulted to count up the lextype
        occurences.
        """
        for tree in trees:
            self._do_tree_stats(tree)

    def _do_tree_stats(self, tree):
        """
        This could be moved inside Tree. pass relevant dictionaries to
        update stats
        """
        stack = [tree]

        while len(stack) > 0:
            node = stack.pop()
            child1 = node.children[0]

            if type(child1) is Token:
                self.lex_entries[child1.lex_entry] += 1
            else:
                self.rules[node.label] += 1
                stack.extend(node.children)

    def _restore_token_case(self, ptokens):       
        ptokens = self._index_ptokens(ptokens)

        for t in self.tokens:
            ptoks = ptokens[(t.start, t.end)]
            for p in ptoks:
                if t.string.lower() != p:
                    t.string = p
                    break
            
    def _index_ptokens(self, ptokens):
        ptoks = ptokens.split(') (')

        index = defaultdict(set)
        for p in ptoks:
            bits = p.split(' ')
            start_vert = int(bits[1].strip(','))
            end_vert = int(bits[2].strip(','))
            index[(start_vert, end_vert)].add(bits[5][:-1].strip('"'))
        
        return index

    def _reconstruct(self, derivation, typifier_path):
        """
        Use the custom ACE Typifier program to reconstruct a derivation to
        its complete AVM and extract all type names. This C program can be 
        found in src/typifier.c

        This sets two instance variables: 
            self.types     -- all type names found within the complete AVM 
            self.json_tree -- a json representation of the derivation tree
                              (somewhat unrelated, but happens to be 
                              returned from the typifier program which had
                              this functionality grafted onto it.) 
        """
        env = dict(os.environ)
        env['LC_ALL'] = 'en_US.UTF-8'
        args = [typifier_path, self.grammar.dat_path]
        process= Popen(args, stdout=PIPE, stdin=PIPE, stderr=PIPE, env=env, close_fds=True)
        out, err = process.communicate(input=derivation.encode('utf8'))

        if process.returncode != 0:
            raise AceError('typifier', err)

        types, tree = out.split('\n\n')
        self.err = err
        types = [t for t in types.split() if not t.startswith('"') or 
                 (t.endswith('_rel"') and not t.endswith('unknown_rel"'))]
        self.types.update(types)

        # ACE escapes single quotes with a backslash. The json decoder
        # does not accept this as valid JSON.
        tree = tree.replace("\\'", "'")
        self.json_tree = json.loads(tree.strip())

    def _lookup_lextypes(self):
        """
        Consult the Grammar to convert all lex entries into their
        lextypes.
        """
        self._lextypes = Counter()

        for le, val in self.lex_entries.iteritems():
            try:
                lextype = self.grammar.lex_lookup(le)
                self._lextypes[lextype] += val
            except(LexLookupError) as e:
                sys.stderr.write(e.msg)

    def ptb(self):
        return self.tree.ptb()

    def latex(self):
        return self.tree.latex()

    def pprint(self, **kwargs):
        return self.tree.pprint(**kwargs)

    def draw(self):
        return self.tree.draw()

    @property
    def input(self):
        """Reconstruct input based on parsed tokens."""
        return ' '.join(t.string for t in self.tokens)

    @property
    def derivation(self):
        return self.tree.derivation

    @property
    def lextypes(self):
        """Support lazy loading of lextypes from grammar"""
        if self._lextypes is None:
            self._lookup_lextypes()

        return self._lextypes

    @property
    def unknowns(self):
        return Counter({key:val for key,val in self.lextypes.items() 
                 if key.endswith('-unk_le')})

    @property
    def generics(self):
        return Counter({key:val for key,val in self.lextypes.items() 
                 if key.endswith('-gen_le')})

    @property
    def num_nodes(self):
        return sum(self.rules.values()) + sum(self.lex_entries.values())


class Grammar(object):
    """Models a DELPH-IN grammar."""

    lex_entries = None

    def read_tdl(self, speech=False):
        """
        Read the top level tdl file of a grammar and then load lexicl
        entries and rules. If speech argument is True then also load
        lexical entries intended for spoken domains -- only relevent
        to ERG."""
        lexfiles, rulefiles = self.load_tdlfile(speech)
        self.lex_entries = {}
        self.rule_entries = {}

        for lexfile in lexfiles:
            try:
                self.read_entryfile(lexfile, self.lex_entries)
            except IOError:
                pass

        for rulefile in rulefiles:
            try:
                self.read_entryfile(rulefile, self.rule_entries)
            except IOError:
                pass

    def load_tdlfile(self, speech):
        """
        Reads the top level tdl file of a grammar, identifying files which
        contain lexial entries or rule entries.
        """
        lexfiles = []
        rulefiles = []

        if os.path.basename(self.tdlfile) == 'german.tdl':
            tdlfile = os.path.join(self.path, 'common.tdl')
        else:
            tdlfile = self.tdlfile

        with open(tdlfile) as f:
            entry_type = None
            for line in f:
                if line.startswith(';'):
                    continue
                elif line.startswith(':begin :instance :status'):
                    entry_type = line.split()[-1].strip('.')
                elif line.startswith(':end :instance'):
                    entry_type = None
                elif entry_type is not None and line.startswith(':include'): 
                    filename = line.split()[1].strip('\n."')

                    if not filename.endswith('.tdl'):
                        filename +=  '.tdl'
                    
                    filename = os.path.join(*filename.split('/'))

                    if entry_type in ('rule', 'lex-rule'):
                        rulefiles.append(filename)
                    elif entry_type in ('lex-entry', 'generic-lex-entry'):
                        lexfiles.append(filename)

        if speech:
            self.lexfiles.extend(os.path.join('speech', f) for f in 
                                   os.listdir(os.path.join(self.path, 'speech'))
                                   if f.endswith('.tdl'))

        return lexfiles, rulefiles

    def read_entryfile(self, filename, entries_dict):
        """
        Process a single tdl entry file, storing entries into a
        dictionary of the form: {entry : type inherited from}.
        """
        path = os.path.join(self.path, filename)
        with codecs.open(path, 'r', 'utf-8') as file:
            in_comment = False
            for line in file:
                if line.startswith(';'):
                    continue
                elif line.startswith('#|'):
                    in_comment = True
                elif line.startswith('|#'):
                    in_comment = False
                elif not in_comment and line.find(':=') > 0:
                    tokens = line.split(':=')
                    name = tokens[0].strip()
                    value = tokens[1].strip(' &\n')
                    entries_dict[name] = value

    def lex_lookup(self, lex_entry):
        """Lookup the lextype of a lexical entry."""
        try:
            return self.lex_entries[lex_entry]
        except KeyError, key:
            raise LexLookupError(u"Lex entry not found in lexicon: '{0}'".format(lex_entry))


class ConfigGrammar(Grammar):
    """Models grammars specified in config.py."""
    def __init__(self, params, datapath):
        for param, val in params.items():
            setattr(self, param, val)

        self.path = os.path.dirname(self.tdlfile)
        self.dat_path = os.path.join(datapath, self.alias + '.dat')
        self.types_path = os.path.join(datapath, self.alias + '.xml')
        self.pickle_path = os.path.join(datapath, self.alias + '.pickle')
                    
    def json(self):
        """Used for json serializing instances of this class."""
        attrs = ('alias', 'shortname', 'longname', 'ltdblink')
        return {attr : getattr(self, attr) for attr in attrs} 

        
class LogonGrammar(Grammar):
    """
    Models grammars found in the LOGON repository, 
    using the $LOGONROOT/etc/registry file.
    """
    def __init__(self, alias):
        self.alias = alias
        self.name = GRAMMAR_NAMES[self.alias]
        data = self.lookup_registry(alias, LOGONREGPATH)
        self.path = os.path.join(LOGONROOT, data['path'])
        self.tdlfile = os.path.join(self.path, data['tdlfile']) 
        self.grmfile = os.path.join(self.path, data['grmfile']) 
        self.desc = data['desc']        
        self.version = data['version']               
        self.dat_path = os.path.join(self.path, alias + '.dat')

    def lookup_registry(self, alias, path):
        attrs = {}
        found_alias = ''

        with open(path) as file:
            for line in file:
                char1 = line[0]
                if char1 in (';',' ','\n','t'):
                    continue
                elif char1 == '[':
                    if found_alias == alias:
                        break
                    found_alias = line.strip('[]\n')
                else:
                    if found_alias != alias:
                        continue
                    key, value = line.strip().split('=')
                    if key == 'rt':
                        attrs['path'] = value
                    elif key == 'ne':
                        attrs['desc'] = value
                    elif key == 'vn':
                        attrs['version'] = value
                    elif key == 'cp':
                        attrs['grmfile'] = value
                        attrs['tdlfile'] = value[:-4] + '.tdl'
        return attrs


class Type(object):
    """Class used to model a DELPH-IN grammar type."""
    def __init__(self, name, hierarchy, parent_names, child_names):
        self.name = name
        self.parent_names = parent_names
        self.child_names = child_names
        self.parents = []
        self.children = []
    
    def ancestors(self):
        """Returns a set of ancestor Types for this Type"""
        ancestors = set()
        stack = self.parents[:]
        while(len(stack) != 0):
            parent = stack.pop()
            ancestors.add(parent)
            for p in parent.parents:
                if p not in ancestors:
                    stack.append(p)                            
        return ancestors

    def descendants(self):
        """Returns a set of descendant Types for this Type"""
        descendants = set()
        stack = self.children[:]
        while(len(stack) != 0):
            child = stack.pop()
            descendants.add(child)
            for c in child.children:
                if c not in descendants:
                    stack.append(c)                            
        return descendants

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class TypeHierarchy(object):
    """
    A class to model a DELPH-IN grammar's type hierarchy. Uses the
    XML representation that is yielded from this lkb function:
    (lkb::types-to-xml :file file-name).
    """

    def __init__(self, xml_typefile):
        self.types = self.load_types(xml_typefile)
        self.connect_graph()
        self.find_depths(self['*top*'], 0)

    def load_types(self, xml_typefile):
        types = {}

        with open(xml_typefile) as f:
            xml_entries = f.read()

        xml_doc = "<doc>{}</doc>".format(xml_entries)
        tree = etree.fromstring(xml_doc)

        for t in tree:
            name = t.get('name')
            parents = [x.get('name') for x in t.find('parents').iter('type')]
            children = [x.get('name') for x in t.find('children').iter('type')]
            types[name] = Type(name, self, parents, children)

        return types

    def connect_graph(self):
        """
        When a hierarchy is initially read in, only the names of
        parent and child types are known.  After they're read in, we
        can reify these into actual Types.
        """
        for t in self.types.values():
            for pname in t.parent_names:
                t.parents.append(self.types[pname])

            for cname in t.child_names:
                t.children.append(self.types[cname])

            del t.parent_names
            del t.child_names
    
    def find_depths(self, xtype, depth):
        try:
            if depth < xtype.depth:
                xtype.depth = depth
            else:
                return
        except AttributeError:
            xtype.depth = depth

        for c in xtype.children:
            self.find_depths(c, depth+1)

    def get_supers(self, type_names):
        """Given a list of types, return the set of all super types."""
        supers = set()

        for name in type_names:
            try:
                supers.update(self[name].ancestors())
            except(TypeNotFoundError) as err:
                sys.stderr.write(str(err))

        return supers

    def get_children(self, type_names):
        """Give a list of types, return a set of all child types."""
        children = set()

        for name in type_names:
            try:
                children.update(self[name].descendants())
            except(TypeNotFoundError) as err:
                sys.stderr.write(str(err))

        return children

    def __getitem__(self, key):
        try:
            t = self.types[key]
        except(KeyError) as err:
            raise TypeNotFoundError(key)
        return t


class Token(object):
    def __init__(self, string, lex_entry, start, end, from_char, to_char, span=None):
        self.string = string
        self.lex_entry = lex_entry
        self.from_char = from_char
        self.to_char = to_char
        self.start = start
        self.end = end
        self.span = span


class Tree(object):
    def __init__(self, label, start, end, span=None):
        self.label = label
        self.start = start
        self.end = end
        self.span = span
        self.children = []

    def process(self, lex_lookup=None):
        """
        Initial processing of tree, extracting tokens and all nodes,
        adjusting the label of penultimate nodes to be lextypes if a
        lex_lookup funciton is specified.
        """
        nodes = []
        tokens = []
        stack = [self]       
        self.depth = 0
        self.parent = None

        while len(stack) > 0:
            node = stack.pop()
            child1 = node.children[0]
            nodes.append(node)
            child_depth = node.depth + 1
            
            if type(child1) is Token:
                child1.depth = child_depth
                child1.parent = node
                tokens.append(child1)
                if lex_lookup is not None:
                    node.label = lex_lookup(child1.lex_entry)
            else:
                for n in node.children:
                    n.parent = node
                    n.depth = child_depth
                stack.extend(node.children)

        tokens.reverse()
        return tokens, nodes 

    def ptb(self):
        """Returns a psuedo Penn Treebank style tree of the derivation.
        'Pseudo' because currently the only PTB normalization done is
        for round parentheses."""
        return self._ptb(self)

    def _ptb(self, subtree):
        if type(subtree) is Token:
            val = subtree.string.replace('(', '-LRB-')
            val = val.replace(')', '-RRB-')
            return u'{}'.format(val)
        else:
            children = (u'{}'.format(self._ptb(x)) for x in subtree.children)
            return u'({} {})'.format(subtree.label, u' '.join(children))

    def tokens(self):
        """Get the tokens of this tree."""
        tokens = []
        stack = [self]

        while len(stack) > 0:
            node = stack.pop()
            child1 = node.children[0]

            if type(child1) is Token:
                tokens.append(child1)
            else:
                stack.extend(node.children)

        tokens.reverse()
        return tokens

    def pprint(self, **kwargs):
        """Returns a representation of the tree compatible with the LaTeX
        qtree package. Requires the nltk module. See
        http://www.nltk.org/_modules/nltk/tree.html."""
        from nltk import Tree as NLTKTree
        tree = NLTKTree(self.ptb()) 
        return tree.pprint(**kwargs)

    def latex(self):
        """Returns a representation of the tree compatible with the
        LaTeX qtree package. Requires the nltk module. See 
        http://www.nltk.org/_modules/nltk/tree.html."""
        from nltk import Tree as NLTKTree
        string = self.ptb().replace('[', '\[').replace(']', '\]')
        tree = NLTKTree(string) 
        latex = tree.pprint_latex_qtree()
        return latex.replace('-LRB-', '(').replace('-RRB-', ')')

    def draw(self):
        from nltk import Tree as NLTKTree
        NLTKTree(self.ptb()).draw()

    @property
    def input(self):
        return ' '.join(t.string for t in self.tokens())

    @property
    def derivation(self):
        return self._derivation(self)        

    def _derivation(self, subtree):
        if type(subtree) is Token:
            return u'({})'.format(subtree.span)
        else:
            children = (u'{}'.format(self._derivation(x)) for x in subtree.children)
            return u'({} {})'.format(subtree.span, u' '.join(children))

            
def parse_derivation(derivation, cache=False):
    """Parse a DELPH-IN derivation string, returning a Tree object.
    If cache is true, the Tree instances will each store the 
    relevant span of the derivation string in the attribute 'span'."""
    escape_str = '__ESC__'
    der_string = derivation.replace('\\"', escape_str)
    node_re = r'("[^"]+"|[^()"]+)+'
    span_re = re.compile('\({}|\)'.format(node_re))

    # Walk through each span, updating a stack of trees. 
    # Where a span is either lparen + node or rparen.
    # The stack is a list of Trees and Tokens 
    stack = [Tree(None, None, None)]
    for match in span_re.finditer(der_string): 
        span = match.group() 

        # Leaf node 
        if span[:2] == '("': 
            if len(stack) == 1: 
                parse_error(der_string, match, '(') 
            chars = span.split('"', 2)[1]
            chunks = span.split()
            from_char = int(chunks[chunks.index('+FROM')+1].replace(escape_str, ''))
            # for multi word tokens, we need to get the *last* +TO value
            list_rindex = lambda x: len(chunks) - chunks[-1::-1].index(x) - 1
            to_char = int(chunks[list_rindex('+TO')+1].replace(escape_str, ''))
            #print chars, from_char, to_char
            lex = stack[-1]
            if cache:
                cachespan = span[1:].strip().replace(escape_str, '\\"')
            else:
                cachespan = None
            token = Token(chars, lex.label, lex.start, lex.end, from_char, 
                          to_char, span=cachespan)
            stack.append(token)

        # Beginning of a tree/subtree 
        elif span[0] == '(': 
            if len(stack) == 1 and len(stack[0].children) > 0: 
                parse_error(der_string, match, 'end-of-string') 
            
            atts = span[1:].strip().split() 

            if len(atts) > 1:
                label = atts[1]
                start = int(atts[3])
                end = int(atts[4])
                if cache:
                    cachespan = span[1:].strip().replace(escape_str, '\\"')
                else:
                    cachespan = None
                node = Tree(label, start, end, span=cachespan)                    
            elif len(atts) == 1:
                # initial root condition node, not found in ACE
                # derivations set start and end to -1 to make this
                # detectable.
                label = atts[0]
                node = Tree(label, -1, -1, span=label)
            else:
                parse_error(der_string, match, 'empty-node') 

            stack.append(node) 

        # End of a subtree 
        elif span == ')': 
            if len(stack) == 1: 
                if len(stack[0].children) == 0: 
                    parse_error(der_string, match, '(') 
                else: 
                    parse_error(der_string, match, 'end-of-string') 

            node = stack.pop() 
            stack[-1].children.append(node) 

    # check that we got exactly one complete tree. 
    if len(stack) > 1: 
        parse_error(der_string, 'end-of-string', ')') 
    elif len(stack[0].children) == 0: 
        parse_error(der_string, 'end-of-string', '(') 
    else: 
        assert stack[0].label is None 
        assert len(stack[0].children) == 1 

    return stack[0].children[0]


def parse_error(string, match, expecting):
    """Construct a basic error message."""
    if match == 'end-of-string':
        pos, span = len(string), 'end-of-string'
    else:
        pos, span = match.start(), match.group()
    msg = 'Parsing error: expected %r but got %r\n%sat index %d.' % (
        expecting, span, ' '*12, pos)

    # Add a display showing the error span itself:
    s = string.replace('\n', ' ').replace('\t', ' ')
    offset = pos
    if len(s) > pos+10:
        s = s[:pos+10]+'...'
    if pos > 10:
        s = '...'+s[pos-10:]
        offset = 13
    msg += '\n%s"%s"\n%s^' % (' '*16, s, ' '*(17+offset))
    raise DerivationError(msg) 


def load_hierarchy(xmlfile_path, save_pickle=False):
    """Load the pickled version of the hierarchy. If there is none,
    load the hierarchy and also save a pickle of it if save_pickle is
    True.""" 
    root = os.path.splitext(xmlfile_path)[0]
    try:
        with open(root+'.pickle', 'rb') as f:
            hierarchy = cPickle.load(f)
    except(IOError) as e:
        hierarchy = TypeHierarchy(xmlfile_path)
        if save_pickle:
            sys.setrecursionlimit(10000)
            cPickle.dump(hierarchy, open(root+'.pickle', 'wb'))
    return hierarchy


def lookup_hierarchy(arg):
    cwd = os.getcwd()
    hierarchy = TypeHierarchy(os.path.join(cwd, arg.hierarchy))

    with open(os.path.join(cwd, arg.types)) as f:
        candidates = [l.strip() for l in f.read().splitlines()]
        candidates = [l for l in candidates if l != '']
    
    if arg.query == "supers":
        found = hierarchy.get_supers(candidates)
    elif arg.query == "children":
        found = hierarchy.get_children(candidates)
    
    print "\n".join(str(t) for t in found)


def get_supers(types, hierarchy):
    """Given a list of types, return a set containing every ancestors to
    all the input types. GLBs are resolved using the function
    resolve_glbs."""
    supers = []
    for t in types:
        if t.startswith('"'):
            # don't bother looking up strings
            continue

        try:
            t = hierarchy[t.lstrip('^')]
        except(TypeNotFoundError) as e:
            msg = "Did not find '{}' in the type hierarchy'\n".format(t)
            sys.stderr.write(msg)
        else:
            # this needs to be outside of the try so errors
            # thrown by ancestors are not caught
            for s in t.ancestors():
                supers.append(s.name)
    return set(resolve_glbs(supers, hierarchy))


def resolve_glbs(types, hierarchy):
    """
    Given a list of types, creates and returns a set of types
    with the GLB types removed and replaced (ie added to the set)
    by their immediate non-GLB ancestors.
    """
    new_types = []
    glbs = []
    for t in types:
        if t.startswith('glb'):
            glbs.append(t)
        else:
            new_types.append(t)

    glbs = set(glbs)
    while len(glbs) > 0:
        g = glbs.pop()
        parents = (x.name for x in hierarchy[g].parents)
        for t in parents:
            if t.startswith('glb'):
                glbs.add(t)
            else:
                new_types.append(t)
    return set(new_types)


def tsdb_query(query, profile):
    """Perform a query using the tsdb commandline program. The query
    argument to this function is used as the value of the tsdb -query
    argument and the profile argument to this function is used as the
    value of the tsdb -home argument."""
    env = dict(os.environ)
    env['LC_ALL'] = 'en_US.UTF-8'
    args = ['tsdb', '-home', profile, '-query', query]
    process= Popen(args, stdout=PIPE, stderr=PIPE, env=env, close_fds=True)
    out, err = process.communicate()

    if process.returncode != 0:
        raise TsdbError(err)
    
    return out
    

def get_profile_ids(*paths):
    """Return all the i-ids found in a list of profile paths."""
    ids = []
    
    for path in paths:
        results = tsdb_query('select i-id', path)
        ids.extend(int(x) for x in results.split())
        
    ids.sort()
    return ids


def get_profile_results(paths, best=1, gold=False, cutoff=None, grammar=None, 
                        lextypes=True, typifier=None, condition=None, pspans=None,
                        cache=False):
    """Return Readings from across a series of profiles. This assumes
    unique i-ids across all profiles. Returns a dictionary which maps
    i-ids onto lists of Reading sorted by result-id (ie decreasing
    order of confidence according to the parse selection model)."""
    results_dict = defaultdict(list) 
    annotations = defaultdict(list)
   
    if gold:
        # This is for querying a thinned profile, where we can simply
        # return all all readings. Note though that we can still find
        # multiple readings in a gold profile. eg when t-active > 1.
        # This query will return all however, so if just the first is wanted, 
        # the rest need to be excuded downstream.
        query = 'select i-id result-id mrs p-tokens derivation from result where readings > 0'
    else:
        # This query is not appropriate for gold/thinned profiles as
        # the readings will have relatively arbitrary result-ids. We
        # must also restrict queries to within relevant result-ids
        # otherwise query times/memory usage explodes for large parse
        # forests.
        query = 'select i-id result-id mrs p-tokens derivation where result-id <= {}'.format(best - 1)
        
    if condition is not None:
        # NOTE: just adding 't-active=1' won't give you gold trees,
        # you'll get the best (n) trees for each item that *has* a
        # gold tree. To get gold readings, you need to thin the profile and
        # then use the gold query above.
        query += ' and {}'.format(condition)

    if pspans is not None:
        query += ' and p-id = {}'.format(pspans)
        ipquery = 'select i-id ip-author where p-id = {}'.format(pspans)

        for path in paths:
            results = tsdb_query(ipquery, path)
            for result in results.splitlines():
                bits = result.split('|')
                iid = int(bits[0])
                start, end = (int(x) for x in bits[1].split('-'))
                annotations[iid].append((start, end))

    for path in paths:
        results = tsdb_query(query, path)
        for result in results.splitlines():
            result = result.decode('utf-8')
            bits = result.split(' | ', 4)
            iid = int(bits[0].strip())
            resultid = int(bits[1].strip())
            mrs = bits[2].strip()
            ptokens = bits[3].strip()
            derivation = bits[4].strip()
            reading = Reading(derivation, iid=iid, resultid=resultid, mrs=mrs,
                              grammar=grammar, ptokens=ptokens, lextypes=lextypes, 
                              typifier=typifier, pspans=annotations[iid], 
                              cache=cache)

            results_dict[iid].append(reading)

            if cutoff is not None and len(results) >= cutoff:
                return results_dict

    return results_dict


def get_text_results(lines, grammar, best=1, cutoff=None, lextypes=True, 
                     typifier=None, cache=False):
    results_dict = defaultdict(list)

    for i, line in enumerate(lines):
        f = Fragment(line, grammar, count=best, lextypes=lextypes, typifier=typifier, 
                     cache=cache)

        for reading in f.readings:
            results_dict[i].append(reading)

        if cutoff is not None and len(results) >= cutoff:
            return results_dict

    return results_dict


# When module is imported, initialize paths from logon installation
init_paths()
