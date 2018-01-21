# Using Typediff to Discover Right Node Raising ERG Types

The following documents an example of how Typediff can be used to discover
discover ERG types that are associated with a target phenomenon. The phenomenon
in question is the right node raising construction, which involves two sequences
that are parallel in structure and which do not form a complete constituent,
with a constituent immediately to the right of the sequences that functions as a
shared argument to both sequences \cite[1341]{huddleston:2002}. We only consider
coordinated sequences here, but apparently the construction is considered by at
least some (if [Wikipedia](https://en.wikipedia.org/wiki/Right_node_raising) is
to be trusted) to extend to other types of sequences. Huddleston and Pullum
refer to this construction as *right nonce-constituent coordination* (p1341).

The following are exemplars of right node raising that have been taken from the
the Redwoods treebank, with the parallel sequences sharing an argument rendered
in boldface:

1. Linguistics concerns itself with **describing** and **explaining** the nature
   of human language.
2. German is **closely related to** and **classified alongside** English and
   Dutch.
3. I **selected** and **paid for** second day delivery of my order.
4. An object is an entity which **keeps** or **stores** information in a
   database.
5. Keys are commonly used to **join** or **combine** data from two or more
   tables.
6. A database can **set** and **hold** multiple locks at the same time on the
   different level of the physical data structure.

Typediff works through ostensibly defined phenomena, so these exemplars form our
working characterisation of the phenomenon, delimiting its range to cover
constructions of the same form as these. Let's
[load exemplar 1. into Typediff](/#count=10&treebank=redwoods1214&labels=short&tagger=ace&mode=union&supers=false&fragments=false&Agrammar=erg&A=Linguistics%20concerns%20itself%20with%20describing%20and%20explaining%20the%20nature%20of%20human%20language.).

TODO: point out the total number of types

The types in the Output pane are those that have been extracted from the input
exemplar. By default, the analysis corresponding to the best parse according to
the parse selection model is used. You can click on the exemplar to choose an
alternative analysis if needed. The types are coloured according to the
framework-theoretic supertype that they correspond to (*sign*, *synsem*, *head*,
*cat*, *relation*, *predsort*) and hovering over them them will indicate which
supertype. Types that don't inherit from any of these high-level types are
considered to be *other*, and by default are excluded under the hypothesis that
these are largely foundational or "glue" types less likely to be associated
directly with the handling of grammatical phenomena.

Initially, the types are (reverse) sorted by their TF-IDF weighting. TF-IDF is
derived similarly to the standard usage in an information retrieval context, but
modified for this use case. Here term frequency (TF) is determined by the number
of exemplar items containing the type, and the document frequency (DF) is
considered to be the number of gold trees from the Redwoods Treebank containing
the type. When applied to the standard
[TF-IDF formulation](https://en.wikipedia.org/wiki/Tf%E2%80%93idf), this has the
effect of increasing the weight of types that are frequently occurring in
positive exemplars, while also reducing the weight for types that occur
frequently across a corpus. For a single item however, term frequency of a type
will always be 1, meaning that the ranking is the same as produced by simple
treebank tree coverage.

Looking at this ranking we can see that the type *right_node_raise_vp_rule* is
happily in the fourth position. The remaining types however don't appear to be
especially related, however. Let's see what else we can uncover by [adding the
remaining five exemplars](/#count=10&treebank=redwoods1214&labels=short&tagger=ace&mode=union&supers=false&fragments=false&Agrammar=erg&A=Linguistics%20concerns%20itself%20with%20describing%20and%20explaining%20the%20nature%20of%20human%20language.%7C%7C%7CKeys%20are%20commonly%20used%20to%20join%20or%20combine%20data%20from%20two%20or%20more%20tables.%7C%7C%7CGerman%20is%20closely%20related%20to%20and%20classified%20alongside%20English%20and%20Dutch.%7C%7C%7CI%20selected%20and%20paid%20for%20second%20day%20delivery%20of%20my%20order.%7C%7C%7CAn%20object%20is%20an%20entity%20which%20keeps%20or%20stores%20information%20in%20a%20database.%7C%7C%7CA%20database%20can%20set%20and%20hold%20multiple%20locks%20at%20the%20same%20time%20on%20the%20different%20level%20of%20the%20physical%20data%20structure.)

Desirably, *right_node_raise_vp_rule* has now moved to position one, and we also
have two other sign types in the next positions, *extracomp_rule* and
*hmark_e_phr_rule*, which respectively license extracted complements and the
combination of a coordinator and single verb phrase both involved in a
coordinated verb phrase (?). This is again promising as these other two types,
while not being sufficient to indicate the presence of right node raising, are
necessary for its presence (at least as we have characterised the phenomenon
here).Selectively disabling some of the exemplars (using the toggle on the exemplar
items) reveals that some smaller combinations (such as enabling only 1, 3, and
5) can be sufficient to promote the same three types to the top of the
ranking. However with smaller numbers, the ranking is more sensitive to the
selection of the items due to the surrounding phenomena that come along for the
right and their background frequencies, and it is only with the inclusion of
larger numbers do we see the ranking stabilising.

Enabling all six exemplars again, we can continue to explore the extraced types,
this type by selecting *sign* from the dropdown menu underneath the *Kind*
column in the type ranking. This causes the types to be filtered to only include
sign types. We then see...

vp_predp_coord_top_phr
vp_coord_fin_top_phr
vp_coord_nonfin_top_phr


minimal pair example

1. Linguistics concerns itself with **describing** and **explaining** the nature
   of human language.
2. Linguistics concerns itself with **describing the nature of human language**
   and **explaining the nature of human language**.
