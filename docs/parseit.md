#Parseit

A flexible tool for converting and extracting information from
DELPH-IN grammar derivations. Supports reading stored derivations 
from DELPH-IN profiles as well as on the fly parsing from text files
and standard input.


## Features

* Converting to PTB style bracketed derivations.
* Drawing trees (pretty printing, latex output, GUI visualization).
  These require the NLTK package to be installed.
* Extracting attributes from derivations for use in ML tasks. 
  Supported attrbutes: lextypes and rule names
* Counting occurrences of attributes across parse results
* Comparing attribute sets using KL Divergence and Jenson 
  Shannon Divergence (from two or more different sets of profiles)


## To get running

1. Move src/config_example.py to src/config.py and edit according to
   suit your environment. In particular, you'll want to ensure that
   the grammar(s) you wish to use has an entry in the GRAMMARLIST
   variable and has the correct parameters. 

2. If you want to use the 'draw' modes, you'll need to install the
   Python Natural Language Toolkit. See
   http://www.nltk.org/install.html.

3. In order for parseit to parse with ACE or extract attributes which
   require access to the type hierachy (such as using the descendents
   option when extracting types) you will need to generate a couple of
   grammar data files. See
   [grammar-utils.md](grammar-utils.md) for further details.
   
