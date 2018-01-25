# Using Typediff to Discover Right Node Raising ERG Types

The following documents an example of how Typediff can be used to discover
discover ERG types that are associated with a target phenomenon. The phenomenon
in question is the right node raising construction, which involves two sequences
that are parallel in structure and which do not form a complete constituent,
with a constituent immediately to the right of the sequences that functions as a
shared argument to both sequences (Huddleston and Pullum 2002:1341). We only
consider coordinated sequences here, but apparently the construction is
considered by at least some (if
[Wikipedia](https://en.wikipedia.org/wiki/right_node_raising) is to be trusted)
to extend to other types of sequences. Huddleston and Pullum refer to this
construction as *right nonce-constituent coordination* (p1341).

The following are exemplars of right node raising that have been taken from the
the redwoods treebank, with the parallel sequences that share an argument
rendered in boldface:

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
[load exemplar 1 into typediff](/#count=10&treebank=redwoods1214&labels=short&tagger=ace&mode=union&supers=false&fragments=false&Agrammar=erg&A=Linguistics%20concerns%20itself%20with%20describing%20and%20explaining%20the%20nature%20of%20human%20language.).

The types in the output pane are those that have been extracted from the input
exemplar. By default, the analysis corresponding to the best parse according to
the parse selection model is used. You can click on the exemplar to choose an
alternative analysis if needed (unless working with items reconstructed from a
thinned profile). The types are coloured according to the high-level supertype
that they correspond to (*sign*, *synsem*, *head*, *cat*, *relation*,
*predsort*) and hovering over them them will indicate which supertype. Types
that don't inherit from any of these are considered to be *other*, and by
default are filtered from view under the hypothesis that these are largely
foundational or "glue" types less likely to be associated directly with the
handling of grammatical phenomena. For this exemplar, we can see that a total of
324 types have been extracted, which has been filtered down to 126 once *other*
types have been removed.

## Type Weighting

Initially, the types are (reverse) sorted by their TF-IDF weighting. TF-IDF is
derived similarly to the standard usage in an information retrieval context, but
modified for this use case. Here term frequency (TF) is determined by the number
of exemplar items containing the type, and the document frequency (DF) is
considered to be the number of gold trees from the redwoods treebank containing
the type. When applied to the
[standard TF-IDF formulation](https://en.wikipedia.org/wiki/tf%e2%80%93idf),
this has the effect of increasing the weight of types that are frequently
occurring in positive exemplars, while also reducing the weight for types that
occur frequently across a corpus. When a single exemplar is used however, term
frequency of a type will always be 1, meaning that the ranking is the same as
produced by just treebank tree coverage.

Looking at this ranking we can see that the type *right_node_raise_vp_rule* is
happily in the fourth position. The remaining types however don't appear to be
especially related, however. Let's see what else we can uncover by
[adding the remaining five exemplars](/#count=10&treebank=redwoods1214&labels=short&tagger=ace&mode=union&supers=false&fragments=false&Agrammar=erg&A=Linguistics%20concerns%20itself%20with%20describing%20and%20explaining%20the%20nature%20of%20human%20language.%7c%7c%7cGerman%20is%20closely%20related%20to%20and%20classified%20alongside%20English%20and%20Dutch.%7c%7c%7cI%20selected%20and%20paid%20for%20second%20day%20delivery%20of%20my%20order.%7c%7c%7cAn%20object%20is%20an%20entity%20which%20keeps%20or%20stores%20information%20in%20a%20database.%7c%7c%7cKeys%20are%20commonly%20used%20to%20join%20or%20combine%20data%20from%20two%20or%20more%20tables.%7c%7c%7cA%20database%20can%20set%20and%20hold%20multiple%20locks%20at%20the%20same%20time%20on%20the%20different%20level%20of%20the%20physical%20data%20structure.).

Desirably, *right_node_raise_vp_rule* has now moved to position one, and we also
have two other sign types in the next two positions, *extracomp_rule* and
*hmark_e_phr_rule*, which respectively license extracted complements and the
combination of a coordinator and verb phrase that are involved in a coordinated
verb phrase. This is again promising as these other two types, while not being
sufficient to indicate the presence of right node raising, are necessary for its
presence (at least as we have characterised the phenomenon here). Selectively
disabling some of the exemplars (using the toggle on the exemplar items) reveals
that some smaller combinations (such as 1, 3, and 5) can be sufficient to
promote the same three types to the top of the ranking. However with smaller
numbers of input exemplars, the ranking is more sensitive to the selection of
the items due to the varying background frequencies of surrounding phenomena
that come along for the ride, and it is only with the inclusion of larger
numbers do we see the ranking stabilising.

Enabling all six exemplars again, we can continue to explore the extracted
types, this type by selecting *sign* from the dropdown menu underneath the
*Kind* column in the type ranking. This causes the ranked types to be filtered
to only include sign types. We then see three more types near the top of the
ranking: *vp_predp_coord_top_phr*, *vp_coord_fin_top_phr*,
*vp_coord_nonfin_top_phr*, each occurring in a third of the input exemplars. Due
to the naming conventions of the erg we might guess these to be mutually
exclusive, handling different variations of the same construction. We can
confirm this by simply hovering over them and seeing which exemplars become
highlighted (clicking on the name of the toggles this highlighting to be locked
on/off for the respective type). Alternatively, we could use an additional
feature, which is to exclude exemplars from being used that do not have a
specific type, by hovering over one of aforementioned sign types and selecting
the white filter. The resultant types come from just the two exemplars left
after this, and when re-filtered to sign types, we can see that the other two
types are no longer present.

Another useful feature is filtering out exemplars that do have a certain
type. This is useful for removing a specific type in order to determine how the
TF-IDF weighting ranks types from the exemplars that do not involve a specific
type. This allows us to determine divisions in the phenomenon space (at least
according to the
ranking). [For example](/#count=10&treebank=redwoods1214&labels=short&tagger=ace&mode=union&supers=false&fragments=false&Agrammar=erg&A=linguistics%20concerns%20itself%20with%20describing%20and%20explaining%20the%20nature%20of%20human%20language.%7c%7c%7ckeys%20are%20commonly%20used%20to%20join%20or%20combine%20data%20from%20two%20or%20more%20tables.%7c%7c%7cgerman%20is%20closely%20related%20to%20and%20classified%20alongside%20english%20and%20dutch.%7c%7c%7ci%20selected%20and%20paid%20for%20second%20day%20delivery%20of%20my%20order.%7c%7c%7can%20object%20is%20an%20entity%20which%20keeps%20or%20stores%20information%20in%20a%20database.%7c%7c%7ca%20database%20can%20set%20and%20hold%20multiple%20locks%20at%20the%20same%20time%20on%20the%20different%20level%20of%20the%20physical%20data%20structure.&excludetypes=vp_predp_coord_top_phr,vp_coord_nonfin_top_phr),
excluding exemplars that include either *vp_predp_coord_top_phr* or
*vp_coord_nonfin_top_phr*, produces a ranking with *vp_coord_fin_top_phr*
immediately below *right_node_raise_vp*_rule at the top of the ranking.


## Type Difference

The previous strategy for performing discovery involved locating a sufficient
number of positive exemplars for the TF-IDF weighting function to reliably
promote potentially salient types to the top of the ranking. Another approach is
to identify a single positive exemplar and a corresponding negative exemplar
that as close as possible but without containing the target phenomenon. This is
reminiscent of the notion of a minimal pair, but pertaining to syntactic
constructions, and most likely *not* involving a meaning change. Here is an
example of such a pair for the right node raising construction:

1. Linguistics concerns itself with **describing** and **explaining** the nature
   of human language.
2. Linguistics concerns itself with **describing the nature of human language**
   and **explaining the nature of human language**.

We can leverage such pairs by taking the types extracted from the positive
exemplar and subtracting from them the types extracted from the negative
exemplar. This hopefully has the effect of masking the types in the positive
exemplar not strictly associated with the target phenomenon. If we
[load Typediff](/#count=10&treebank=redwoods1214&labels=short&tagger=ace&mode=difference&supers=false&fragments=false&Agrammar=erg&A=Linguistics%20concerns%20itself%20with%20describing%20and%20explaining%20the%20nature%20of%20human%20language.&Bgrammar=erg&B=Linguistics%20concerns%20itself%20with%20describing%20the%20nature%20of%20human%20language%20and%20explaining%20the%20nature%20of%20human%20language.)
with this pair of A and B sentences (which Typediff defaults to treating as A -
B), we can see that we have reduced the 126 candidate types from the positive
exemplar down to only 19 through this masking process. Furthermore, both
*right_node_raise_vp_rule* and *extracomp_rule* are are the top of the ranking.

This approach to phenomenon discovery has two benefits. 1) It can potentially
triangulate in upon relevant types with fewer exemplars than the type weighting
approach, and 2) it has given us an additional piece of information, which is
that *extracomp_rule* may be considered somehow more characteristic of right
node raising than *hmark_e_phr_rule*, which has been masked.

A limitation of this approach is that that not every construction can be
rendered as a minimal pair, as there may not be a single sentence that captures
all the material we might consider to be indicative of a negative instance. In
these situations one could try adding additional sentences to the B items to
mask further types, however this can become circular as you ultimately don't
necessarily know what you want to find to begin with. Furthermore, the masking
approach is fairly crude, not being sensitive to where in the sentence a type
originates from. This can be ameliorated by trying to keep exemplars as small as
possible, however it is still possible that types from the negative sentence
that are introduced due to an unrelated phenomenon elsewhere in the sentence may
mask types in the positive sentence that should be considered to be associated
with the target phenomenon. 

These two approaches to type discovery are therefore perhaps best considered to
be complementary, being useful in different contexts, and potentially offering
alternative lenses upon grammar types that might be associated with the target
phenomenon.

