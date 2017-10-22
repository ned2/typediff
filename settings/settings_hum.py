"""
This file contains configuration information that typediff needs to
run, as well as options which can be customized.
"""

# Directory where dat, xml and pickle files are kept.
# You'll want to change this if you don't want to store
# large amounts of data in the installation directory.
DATAPATH  = '/home/nejl/data/grammar-data'


# Path to the directory where ace was compiled.  Optionally used to
# build the ERG image from so that unknown word handling is enabled.
ACESRC = None


# URL prefix of other apps Typediff can interface with
FANGORNPATH = '/ts'
LTDBPATH = '/ltdb/cgi-bin'


# For setting the LOGONROOT with apache, specify it here.  Note that
# this is not actually required for running the typediff interface and
# can be left blank.
LOGONROOT = ''


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
        'ltdb'      : 'ERG_1214',
    },
    {
        'alias'     : 'terg',
        'shortname' : 'ERG trunk (2015-03-11)',
        'longname'  : 'The LinGO English Resource Grammar (trunk 2015-06-20)',
        'aceconfig' : '${LOGONROOT}/lingo/terg/ace/config.tdl',
        'tdlfile'   : '${LOGONROOT}/lingo/terg/english.tdl',
    }, 
    {
        'alias'     : 'erg1212',
        'shortname' : 'ERG 1212',
        'longname'  : 'The LinGO English Resource Grammar (1212 release)',
        'aceconfig' : '${LOGONROOT}/lingo/erg1212/ace/config.tdl',
        'tdlfile'   : '${LOGONROOT}/lingo/erg1212/english.tdl',
        'ltdb'      : 'ERG_1212',
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
    {
        'alias'     : 'norsource',
        'shortname' : 'NorSource',
        'longname'  : 'NorSource (Norwegian Grammar)',
        'aceconfig' : '/home/nejl/delphin/grammars/norsource_1.0/ace/norsource_config.tdl',
        'tdlfile'   : '/home/nejl/delphin/grammars/norsource_1.0/norsk.tdl',
    }, 
    {
        'alias'     : 'indra',
        'shortname' : 'INDRA',
        'longname'  : 'INDRA (Indonesian Grammar)',
        'aceconfig' : '/home/nejl/delphin/grammars/INDRA/ace/config.tdl',
        'tdlfile'   : '/home/nejl/delphin/grammars/INDRA/indonesian.tdl',
    }, 
    {
        'alias'     : 'zhs',
        'shortname' : 'Zhong (zhs)',
        'longname'  : 'Zhong (Sinplified Mandarin Chinese)',
        'aceconfig' : '/home/nejl/phd/delphin/grammars/zhong/cmn/zhs/ace/config.tdl',
        'tdlfile'   : '/home/nejl/phd/delphin/grammars/zhong/cmn/zhs/zhs.tdl',
    },
    {
        'alias'     : 'zht',
        'shortname' : 'Zhong (zht)',
        'longname'  : 'Zhong (Traditional Mandarin Chinese)',
        'aceconfig' : '/home/nejl/phd/delphin/grammars/zhong/cmn/zht/ace/config.tdl',
        'tdlfile'   : '/home/nejl/phd/delphin/grammars/zhong/cmn/zht/zht.tdl',
    },
    {
        'alias'     : 'yue',
        'shortname' : 'Zhong (yue)',
        'longname'  : 'Zhong (Cantonese Chinese)',
        'aceconfig' : '/home/nejl/phd/delphin/grammars/zhong/cmn/zht/ace/config.tdl',
        'tdlfile'   : '/home/nejl/phd/delphin/grammars/zhong/cmn/zht/zht.tdl',
    },
    {
        'alias'     : 'erg-wsj',
        'shortname' : 'ERG 1214 WSJ',
        'longname'  : 'The LinGO English Resource Grammar (WSJ)',
        'aceconfig' : '${LOGONROOT}/lingo/erg/ace/config-wsj.tdl',
        'tdlfile'   : '${LOGONROOT}/lingo/erg/english.tdl',
        'ltdb'      : 'ERG_1214',
    }, 
    {
        'alias'     : 'erg-speech',
        'shortname' : 'ERG 1214 (speech)',
        'longname'  : 'The LinGO English Resource Grammar for speech applications (1214 release)',
        'aceconfig' : '${LOGONROOT}/lingo/erg/ace/config-speech.tdl',
        'tdlfile'   : '${LOGONROOT}/lingo/erg/speech.tdl',
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
