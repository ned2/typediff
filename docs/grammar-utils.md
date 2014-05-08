# grammar-utils.py

This script currently only performs one function, which is to create
the various data files needed for the running of the tools found in
the grammalytics toolkit.  Other functions may be added in the future.


## How to run

    $ grammar-utils.py make-data [GRAMMARS ...]

If one or more grammar-alias is provided, data for just those grammar
will be generated, otherwise data for all grammars configured in
config.py will be generated.

This requires that DATAPATH in config.py is set to an appropriate
value, specifying where the files will be stored. This command will
produce the following sets of files for each grammar:

* grammar.dat
* grammar.xml
* grammar.pickle

.dat files are the compiled grammar file that ACE uses for parsing;
.xml files are XML dumps of the grammar's type hierarchy (see below);
and .pickle files are pickled versions of the type hierarchy used to
speedup the loading if the hierarchy.


## Notes on data produced by grammar-utils.py

### Type hierarchy XML dumps

Typediff uses an XML dump of a grammar's type hierarchy. This is
created automatically when you run `src/grammar-utils.py make-data`
but can also be run manually. This can be done using the dumphierarchy
binary found in the bin directory as follows:
   
    $ bin/dumphierarchy terg.dat > terg.xml
   
Note that this XML format targets that produced by the following
commands in the lisp prompt when the LKB and desired grammar are
loaded:

    (lkb::batch-check-lexicon)
    (lkb::types-to-xml :file "~/types.xml")

Even though Typediff uses ACE, the file produced by this command
should work just as well, so long as you make sure you use the same
version of the grammar as is being used by ACE. (batch-check-lexicon
is required to ensure that all lexical types are included in the
output, as 'leaf types' can be loaded on demand by the LKB).


