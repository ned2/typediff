import os
import sys

from . import settings

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

# default params
ACEBIN = os.path.join(ROOT_PATH, 'bin', 'ace')
TYPIFIERBIN = os.path.join(ROOT_PATH, 'bin', 'typifier')
DUMPHIERARCHYBIN = os.path.join(ROOT_PATH, 'bin', 'dumphierarchy')
LOGPATH = os.path.join('ace.log')

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
    ('sign',     'rgba(255, 0,   0,   0.65)', 'red'),
    ('synsem',   'rgba(0,   128, 0,   0.65)', 'green'),
    ('head',     'rgba(128, 0,   128, 0.65)', 'blue'),
    ('cat',      'rgba(0,   0,   255, 0.65)', 'purple'),
    ('relation', 'rgba(0,   255, 255, 0.65)', 'cyan'),
    ('predsort', 'rgba(255, 255, 0,   0.65)', 'yellow'),
    ('other',    'rgba(255, 255, 255, 1.00)', 'white'),
)


# get other values from settings any already defined above will be overridden

PARAMS = [
    'DATAPATH',
    'LOGONROOT',
    'FANGORNPATH',
    'LTDBPATH',
    'ACESRC',
    'GRAMMARLIST',
    'TREEBANKLIST',
    'PROFILELIST',
    'ACEBIN',
    'JSONPATH',
    'LOGPATH',
]

for param in PARAMS:
    if hasattr(settings, param):
        setattr(sys.modules[__name__], param, getattr(settings, param))
