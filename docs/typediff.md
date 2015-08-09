# Typediff

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

Typediff uses ACE for parsing, and should be compatible with any
DELPH-IN grammar that has been configured to work with ACE. Many
thanks to Woodley Packard for his assistance with extracting 
the required data from ACE.


## How it Works

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
    B: We relied on consultants and hired consultants.

Typediff is both a command line tool and also has a browser-based
interface. The downside to the command line tool is that you are
limited to either using the best parse returned by ACE or all of the
best N parses.  The web interface gives allows you to select which
reading(s) you wish to use.

The web interface will not work on versions of Internet Explorer < 9
and has currently only been tested on Google Chrome and Firefox.


## To get running

1. Install Typediff somewhere your web server has read and execute
   permissions. (Unless you just wish to use the command line version).

2. Move src/config_example.py to src/config.py and edit accordingly.

3. Create the various grammar data required for typediff to run. This
   includes the compiled grammar .dat files used by ACE as well as XML
   dumps of the type hierarchy for each grammar. You can generate
   these yourself or you can run the following command:
 
   ```
   $ src/grammar-utils.py make-data [gram]
   ```

   This will create all the data required by typediff in the directory
   specified by the DATAPATH parameter in config.py. See
   [grammar-utils.md](grammar-utils.md) for further details.  The
   optional [gram] grammar alais parameter restricts the script to
   only generating data for the grammar specified by relevant grammar
   alias.


The above steps should hopefully be sufficient to get Typediff
running, however you may find that you need to perform further
steps...


### Suggested Apache setup on Ubuntu

Here is one way to get Typediff being served up on an Ubuntu
installation, assuming we cloned typediff into ~/typediff.

1. Install Apache:

   ```
   $ sudo apt-get install apache2
   ```

2. Create symlink to Typediff path in Ubuntu's default directory for
   serving web documents:

   ```
   $ sudo ln -s ~/typediff /var/www/html/
   ```

3. Add a Directory entry in the apache config file
   /etc/apache2/sites-enabled/000-default.conf inside the VirtualHost
   entry. You can edit this file with the following command:

   ```
   $ sudo nano /etc/apache2/sites-enabled/000-default.conf
   ```
   
   Something like the following should hopefully work:

   ```
   <Directory /var/www/html/typediff/>
        AllowOverride None
        Order allow,deny
        allow from all
        Options +ExecCGI
        AddHandler cgi-script .cgi
        DirectoryIndex index.html
    </Directory>
   ```

4. Make sure that your Apache installation has the CGI module loaded.
   There should be a symlink at the following path:
   /etc/apache2/mods-enabled/cgi.load. If not, create one like so:

   ```
   $ sudo ln -s /etc/apache2/mods-available/cgi.load /etc/apache2/mods-enabled/
   ```
   
5. Restart Apache:

   ```
   $ sudo service apache2 restart
   ```

6. If all has worked, you should be able to see Typediff up and
   running at http://localhost/typediff.

If you want to make this installation available online (not just on
your local machine) it would also be worth enabling gzip compression
by adding the following option to the Typediff Directory:


    AddOutputFilterByType DEFLATE text/html text/css text/plain application/json application/javascript


This will make the fairly sizeable serialized data that comes back
from the server *much* smaller. You may also need to create symlinks
in mods-enabled to both mods/available/deflate.conf and
mods/available/deflate.load in the same way as with cgi.load. You will
need to restart the server to activate these changes.


### Jacy Segmentation

If you want segmentation for Jacy to work you'll need to install the
MeCab and the Python MeCab bindings. On Ubuntu, the following will hopefully
get this working:

```
 $ sudo apt-get install libmecab-dev
 $ sudo apt-get install mecab mecab-ipadic-utf8
 $ sudo pip3 install mecab-python3
```

### Compiling ACE binaries

Typediff uses ACE along with a couple of other binaries that use ACE
libraries. The included versions of these programs in the repository
have all been compiled for 64-bit machines, and the ACE libraries are
included in the binaries, so you might be lucky enough that these
might just all work. If not you'll have to compile your own version of
ACE and the bundled C programs. See
http://sweaglesw.org/linguistics/ace/ for alternative 64bit binaries,
and ACE source. Instructions for how to compile the other binaries can
be found at the top of typifier.c. You'll then need to modify the various 
binary paths in config.py.


### Web server setup

For the web interface, you might want to double check that your
web server is compressing application/json data, as the data that is
sent from the server can be quite bulky.
