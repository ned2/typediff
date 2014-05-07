Typediff README
===============

Typediff is a tool that enables rapid exploration of the types used in
the processing of input by DELPH-IN grammars. Its intended use case is
identifying types involved in constraining specific linguistic
phenomena. Besides phenomena investigation, Typediff could also be
useful for grammar documentation, exploring unfamiliar grammars, and
comparing different versions of the same grammar. If you find Typediff
useful, feedback on your particular use case and how you used Typediff
would be very much desired.

A live installation of Typediff can be found here:
http://hum.csse.unimelb.edu.au/typediff/

The source for Typediff is available from
http://github.com/ned2/typediff

Typediff uses ACE for parsing, and should be compatible with any
DELPH-IN grammar that has been configured to work with ACE. Many
thanks to Woodley Packard for his assistance with extracting 
the required data from ACE.


How it Works
------------

Users enter any number of input items into the A items set and the B
items set. Each input item is parsed (with ACE) and then for each
selected reading, every type that appears in the full AVM is
extracted. The A and B types are then compared with either of the
functions: difference, intersection or union.

In the difference mode of operation, Typediff will return all types
used to process the A items that were not used by the B items. For
investigating phenomena, this diffing approach works best when you can
identify "minimal pairs" of sentences, as otherwise unrelated types
from the positive sentences will appear as noise in the output.

If the phenomenon you wish to investigate does not lend itself to
having such "minimal pairs", you can try adding additional sentences
to the B items to filter out noisy types from the A items.

Input to explore the right-node-raising construction might be:

    A: We relied on and hired consultants.
    B: We relied on consultants and we hired consultants.

Typediff is both a command line tool and also has a browser-based
interface. The downside to the command line tool is that you are
limited to either using the best parse returned by ACE or all of the
best N parses.  The web interface gives allows you to select which
reading(s) you wish to use.

The web interface will not work on versions of Internet Explorer < 9
and has currently only been tested on Google Chrome and Firefox.


To get running:
---------------

1. Install Typediff somewhere your web server has read and execute
   permissions. (Unless you just wish to use the command line version).

2. Move src/config_example.py to src/config.py and edit accordingly.
   Note that currently the grammar entries are not loaded into the 
   web interface 

3. Create the various grammar data required for typediff to run. This
   includes the compiled grammar .dat files used by ACE as well as XML
   dumps of the type hierarchy for each grammar. You can generate
   these yourself (see below for instructions on how to create the XML
   files) or you can run the following command from the typediff root
   directory:
 
       $ src/td-utils.py make-data

   This will create all the data required by typediff in the directory
   specified by the DATAPATH paramater in config.py.

4. Typediff uses ACE along with a couple of other binaries that use
   ACE libraries. The included versions of these programs in the
   repository have all been compiled for 64-bit machines, and the ACE
   libraries are included in the binaries, so you might be lucky
   enough that these might just all work. If not you'll have to
   compile your own version of ACE and the bundled C programs. 

   See http://sweaglesw.org/linguistics/ace/ for alternative 64bit
   binaries, or the source. Also see instructions at the top of
   typifier.c for how to compile it and dumphierarchy.c.

5. If you want segmentation for Jacy to work you'll need to install
   the Python MeCab bindings. On Ubuntu, installing the packages
   python-mecab and mecab-ipadic-utf8 should suffice.


For the web interface, you might want to double check that your
webserver is compressing application/json data, as the data that is
sent from the server can be quite bulky.


Creating the XML dumps manually:

Create XML dumps of the type hierarchies for each of the grammars you
wish to use with typediff. This can be done using the dumphierarchy
binary found in the bin directory as follows:
   
    $ dumphierarchy terg.dat > terg.xml
   
Note that this XML format targets the same format as that produced by
the following commands in the lisp prompt when the LKB and a grammar
are loaded:

    (lkb::batch-check-lexicon)
    (lkb::types-to-xml :file "~/types.xml")

Even though typediff uses ACE, the file produced by this command
should work just as well, so long as you make sure you use the same
version of the grammar as is being used by ACE. (batch-check-lexicon
is required to ensure that all lexical types are included in the
output, as 'leaf types' can be loaded on demand by the LKB).
