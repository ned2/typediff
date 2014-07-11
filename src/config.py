import os
from delphin import ConfigGrammar


"""
This file contains configuration information that typediff needs to
run, as well as options which can be customized.
"""

# The path to the src directory in the typediff program. Needed for
# other defaults. You no not need to change this.
_SRC_PATH = os.path.dirname(os.path.realpath(__file__))


# Directory where dat, xml and pickle files are kept.
# You'll want to change this if you don't want to store
# large amounts of data in the installation directory.
DATAPATH  = os.path.join(_SRC_PATH, '..', 'grammar-data')


# Path to the directory where ace was compiled.  Optionally used to
# build the ERG image from so that unknown word handling is enabled.
ACESRC = '/home/nejl/phd/delphin/ace-trunk'


# URL prefix of other apps Typediff can interface with
FANGORNPATH = '/ts'
LTDBPATH = '/ltdb/cgi-bin'


# Path where ACE output will be logged to. This is useful to change if
# your web server does not have write access to the typediff
# directory. 
LOGPATH = os.path.join(_SRC_PATH, '..', 'ace.log')


# For setting the LOGONROOT with apache, specify it here.  Note that
# this is not actually required for running the typediff interface and
# can be left blank.
LOGONROOT = '/home/nejl/logon'


# Grammars configured for use with typediff. The string '${LOGONROOT}'
# Will be replaced with the value of the LOGONROOT environment
# variable.
GRAMMARLIST = (
    {
        'alias'     : 'erg',
        'shortname' : 'ERG 1212',
        'longname'  : 'The LinGO English Resource Grammar (1212 release)',
        'aceconfig' : '${LOGONROOT}/lingo/erg/ace/config.tdl',
        'tdlfile'   : '${LOGONROOT}/lingo/erg/english.tdl',
        'ltdb'      : 'ERG_1212',
    },
    {
        'alias'     : 'terg',
        'shortname' : 'Trunk ERG (2014-07-11)',
        'longname'  : 'The LinGO English Resource Grammar (trunk 2014-07-11)',
        'aceconfig' : '${LOGONROOT}/lingo/terg/ace/config.tdl',
        'tdlfile'   : '${LOGONROOT}/lingo/terg/english.tdl',
        'ltdb'      : 'ERG_trunk',
    }, 
    {
        'alias'     : 'jacy',
        'shortname' : 'Jacy',
        'longname'  : 'Jacy Japanese Grammar',
        'aceconfig' : '${LOGONROOT}/dfki/jacy/ace/config.tdl',
        'tdlfile'   : '${LOGONROOT}/dfki/jacy/japanese.tdl',
        'ltdb'      : 'Jacy_1301'
    }, 
    {
        'alias'     : 'gg',
        'shortname' : 'GG',
        'longname'  : 'GG (German Grammar)',
        'aceconfig' : '${LOGONROOT}/dfki/gg/ace/config.tdl',
        'tdlfile'   : '${LOGONROOT}/dfki/gg/german.tdl',
    }, 
    {
        'alias'     : 'hag',
        'shortname' : 'HaG',
        'longname'  : 'HaG (Hausa Grammar)',
        'aceconfig' : '${LOGONROOT}/llf/hag/ace/config.tdl',
        'tdlfile' : '${LOGONROOT}/llf/hag/hausa.tdl'
    }, 
    {
        'alias'     : 'norsource',
        'shortname' : 'NorSource',
        'longname'  : 'NorSource (Norwegian Grammar)',
        'aceconfig' : '/home/nejl/phd/delphin/grammars/norsource_1.0/ace/norsource_config.tdl',
        'tdlfile'   : '/home/nejl/phd/delphin/grammars/norsource_1.0/norsk.tdl',
    }, 
    {
        'alias'     : 'erg-speech',
        'shortname' : 'ERG 1212 (speech)',
        'longname'  : 'The LinGO English Resource Grammar for speech applications (1212 release)',
        'aceconfig' : '${LOGONROOT}/lingo/erg/ace/config-speech.tdl',
        'tdlfile'   : '${LOGONROOT}/lingo/erg/speech.tdl',
    },
    {
        'alias'     : 'erg-wsj',
        'shortname' : 'ERG 1212 WSJ',
        'longname'  : 'The LinGO English Resource Grammar (WSJ)',
        'aceconfig' : '${LOGONROOT}/lingo/erg/ace/config-wsj.tdl',
        'tdlfile'   : '${LOGONROOT}/lingo/erg/english.tdl',
        'ltdb'      : 'ERG_1212',
    }, 
    {
        'alias'     : 'terg-wsj',
        'shortname' : 'Trunk ERG WJS (2013-11-26)',
        'longname'  : 'The LinGO English Resource Grammar (trunk 2014-04-14 WSJ)',
        'aceconfig' : '${LOGONROOT}/lingo/terg/ace/config-wsj.tdl',
        'tdlfile'   : '${LOGONROOT}/lingo/terg/english.tdl',
        'ltdb'      : 'ERG_trunk',
    }, 
)


TREEBANKLIST = (
    {
        'alias'    : 'redwoods1212',
        'name'     : 'LinGO Redwoods 1212',
        'grammars' : ('erg', 'terg', 'terg-wsj', 'erg-speech'),
        'version'  : 'ERG 1212',
        'trees'    : 50489,
        'json'     : 'redwoods1212.json'
    },
    {
        'alias'    : 'deepbank1',
        'name'     : 'DeepBank 1.0',
        'grammars' : ('erg', 'terg', 'terg-wsj', 'erg-speech'),
        'version'  : '1.0',
        'trees'    : 42648,
        'json'     : 'deepbank1.json'
    },
    {
        'alias'    : 'tanaka',
        'name'     : 'Tanaka Corpus (best 1)',
        'grammars' : ('jacy'),
        'version'  : 'December 2013',
        'trees'    : 118879,
        'json'     : 'tanaka.json',
    }
)


# The order types are to be displayed in the output list and their
# color value for terminal output and web interface output
# repectively.  
# 
# format = (super_type_name, terminal_color, web_color)
# 
# terminal_color must be one of {white, cyan, purple, blue,
# yellow, green, red}
# 
# web_color can be any valid CSS color string
TYPES = (
    ('sign',     'red',     'rgba(255, 0,   0,   0.65)'),
    ('synsem',   'green',   'rgba(0,   128, 0,   0.65)'),
    ('head',     'purple',  'rgba(128, 0,   128, 0.65)'),
    ('cat',      'blue',    'rgba(0,   0,   255, 0.65)'),
    ('relation', 'cyan',    'rgba(0,   255, 255, 0.65)'),
    ('predsort', 'yellow',  'rgba(255, 255, 0,   0.65)'),
    ('other',    'white',   'rgba(255, 255, 255, 1.00)'),
)


# These should only need to be changed if you needed to compile
# thebinaries for your own environment. 
TYPIFIERBIN = os.path.join(_SRC_PATH, '..', 'bin', 'typifier')
DUMPHIERARCHYBIN = os.path.join(_SRC_PATH, '..', 'bin', 'dumphierarchy')
ACEBIN = os.path.join(_SRC_PATH, '..', 'bin', 'ace')
JSONPATH = 'json'


def _load_grammar(g):   
    if 'ltdb' in g:
        g['ltdblink'] = LTDBPATH + '/' + g['ltdb']
    else:
        g['ltdblink'] = None

    g['aceconfig'] = g['aceconfig'].replace('${LOGONROOT}', LOGONROOT)
    g['tdlfile'] = g['tdlfile'].replace('${LOGONROOT}', LOGONROOT)
    return ConfigGrammar(g, DATAPATH)    


def get_grammar(alias):
    for g in GRAMMARLIST:
        if g['alias'] == alias:
            return _load_grammar(g)
    return None


def get_grammars():
    return [_load_grammar(g) for g in GRAMMARLIST]
        
