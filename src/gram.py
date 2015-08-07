import os

import config
from delphin import Grammar


class ConfigGrammar(Grammar):
    """Models grammars specified in config.py."""
    def __init__(self, gparams, datapath):
        for gparam, val in gparams.items():
            setattr(self, gparam, val)

        self.path = os.path.dirname(self.tdlfile)
        self.dat_path = os.path.join(datapath, self.alias + '.dat')
        self.types_path = os.path.join(datapath, self.alias + '.xml')
        self.pickle_path = os.path.join(datapath, self.alias + '.pickle')
                    
    def json(self):
        """Used for json serializing instances of this class."""
        attrs = ('alias', 'shortname', 'longname', 'ltdblink')
        return {attr : getattr(self, attr) for attr in attrs} 

        
def load_grammar(gparams):   
    """Given a grammar dictionary (ie from config.GRAMMARLIST) returns a"""
    if 'ltdb' in gparams and config.LTDBPATH is not None:
        gparams['ltdblink'] = config.LTDBPATH + '/' + gparams['ltdb']
    else:
        gparams['ltdblink'] = None

    gparams['aceconfig'] = gparams['aceconfig'].replace('${LOGONROOT}', config.LOGONROOT)
    gparams['tdlfile'] = gparams['tdlfile'].replace('${LOGONROOT}', config.LOGONROOT)
    return ConfigGrammar(gparams, config.DATAPATH)    


def get_grammar(alias):
    for gparams in config.GRAMMARLIST:
        if gparams['alias'] == alias:
            return load_grammar(gparams)
    return None


def get_grammars():
    return [load_grammar(gparams) for gparams in config.GRAMMARLIST]
