import os


"""
This file contains configuration information that typediff needs to
run, as well as options which can be customized.
"""

# Directory where dat, xml and pickle files are kept.
# You'll want to change this if you don't want to store
# large amounts of data in the installation directory.
DATAPATH  = '/home/nejl/data/grammar-data'


# Required for running grammar-utils.py make-data command.
LOGONROOT = None


# URL prefix of other apps Typediff can interface with
FANGORNPATH = None
LTDBPATH = None

# Path to ACE source directory which has been compiiled. Optionally
# used to build the ERG image so that unknown word handling is
# enabled.
ACESRC = None


# The path to the directory of the typediff program. Needed for other
# defaults. You should not need to change this.
TYPEDIFF_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')


# Path where ACE output will be logged to. This is useful to change if
# your web server does not have write access to the typediff
# directory. 
LOGPATH = os.path.join(TYPEDIFF_PATH, 'ace.log')


# Grammars configured for use with typediff. The string '${LOGONROOT}'
# Will be replaced with the value of the LOGONROOT environment
# variable.
GRAMMARLIST = (
    {
        'alias'     : 'erg',
        'shortname' : 'ERG 1214',
        'longname'  : 'The LinGO English Resource Grammar (1214 release)',
        'aceconfig' : '${LOGONROOT}/lingo/erg/ace/config.tdl',
        'tdlfile'   : '${LOGONROOT}/lingo/erg/english.tdl',
        'ltdb'      : 'ERG_1212',
    },
    {
        'alias'     : 'terg',
        'shortname' : 'ERG trunk',
        'longname'  : 'The LinGO English Resource Grammar',
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
        'tdlfile'   : '${LOGONROOT}/llf/hag/hausa.tdl'
    }, 
)


TREEBANKLIST = (
    {
        'alias'    : 'redwoods1214',
        'name'     : 'LinGO Redwoods 1214',
        'grammars' : ('erg', 'erg-wsj', 'erg-speech', 'terg','terg-wsj', 'terg-speech'),
        'version'  : 'ERG 1212',
        'trees'    : 39519,
        'json'     : 'redwoods_1214.json'
    },
    {
        'alias'    : 'redwoods1212',
        'name'     : 'LinGO Redwoods 1212',
        'grammars' : ('erg1212', 'erg1212-wsj', 'erg1212-speech'),
        'version'  : 'ERG 1212',
        'trees'    : 39592,
        'json'     : 'redwoods_1212.json'
    },
    {
        'alias'    : 'deepbank1.1',
        'name'     : 'DeepBank 1.1',
        'grammars' : ('erg', 'erg-wsj', 'erg-speech'),
        'version'  : '1.1',
        'trees'    : 38730,
        'json'     : 'deepbank_1_1.json'
    },
    {
        'alias'    : 'deepbank1',
        'name'     : 'DeepBank 1.0',
        'grammars' : ('erg1212', 'erg1212-wsj', 'erg1212-speech'),
        'version'  : '1.0',
        'trees'    : 38511,
        'json'     : 'deepbank_1.json'
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
    ('head',     'purple',  'rgba(128, 0,   128, 0.65)'),
    ('synsem',   'green',   'rgba(0,   128, 0,   0.65)'),
    ('cat',      'blue',    'rgba(0,   0,   255, 0.65)'),
    ('relation', 'cyan',    'rgba(0,   255, 255, 0.65)'),
    ('predsort', 'yellow',  'rgba(255, 255, 0,   0.65)'),
    ('other',    'white',   'rgba(255, 255, 255, 1.00)'),
)


# These should only need to be changed if you needed to compile
# thebinaries for your own environment. 
TYPIFIERBIN = os.path.join(TYPEDIFF_PATH, 'bin', 'typifier')
DUMPHIERARCHYBIN = os.path.join(TYPEDIFF_PATH, 'bin', 'dumphierarchy')
ACEBIN = os.path.join(TYPEDIFF_PATH, 'bin', 'ace')
JSONPATH = 'www/json'
