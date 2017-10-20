import os
import sys

from . import config

root_dir = os.path.dirname(os.path.abspath(__file__))

# default params
ACEBIN = os.path.join(root_dir, 'bin', 'ace')
TYPIFIERBIN = os.path.join(root_dir, 'bin', 'typifier')
DUMPHIERARCHYBIN = os.path.join(root_dir, 'bin', 'dumphierarchy')
JSONPATH = os.path.join(root_dir, 'www', 'json')
LOGPATH = os.path.join('ace.log')


# update any values from user config if set

params = [
    'ACEBIN',
    'JSONPATH',
    'LOGPATH',
]

for param in params:
    if hasattr(config, param):
        value = getattr(config, param)
        setattr(sys.modules[__name__], param, value)
