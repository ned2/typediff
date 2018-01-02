# Phenomenon Annotated Profiles Available in Typediff

## The Phenomenal Corpus

This profile contains the 477 lines from section08 of the WSJ component of the
PTB, and was taken from DeepBank version 1.1.

The profile was annotated with instances three phenomena. These are outlined and
briefly described below included below. For a more detailed description, see
[the annotation guidelines](guidelines.pdf) that were given to annotators.

1. **Passive clauses**: A subordinate clause which serves to restrict or
elaborate on a referent in the higher clause.

2. **Relative clauses**: A valence-modifying construction, which yields the
patient role occupying the subject position and the agent being found in an
optional prepositional phrase.

3. **Complement clauses**: Subordinate clause which functions as the argument to
a verbal predicate and itself possesses the constituent structure of a clause.


## H&P Relative Constructions

This profile is made up of exemplars extracted from chapter 12 of Huddleston and
Pullum's Cambridge Grammar of the English Language. It includes 417 exemplars
extracted from the portion of chapter 12 that deals with relative
construction. Of these, 333 are both marked as grammatical and being an instance
of a relative construction. These 333 are further annotated based on different
properties identified by H&P as being salient to their analysis of relative
constructions.

Each exemplar is annotated with three different orthogonal phenomenon
categories. These are:

1. **Formal:** the characteristic form that the relative construction takes 
2. **Relational** distinguishes the relation of the relative construction to the
   larger structure that contains it.
3. **Grammatical Function:** The grammatical function of the constituent that is
   being relativised

The values that each of these categories can take are included below. See the
noted page numbers of H&P for more information about these phenomenon
categories.


### formal (p1034 and p1036-1044)

* that
* bare
* wh-simple
* wh-complex-1    | from complement of preposition to PP (behind which)
* wh-complex-2    | from PP complement of noun to NP (the result of which)
* wh-complex-3    | from PP to AdjP (prominent among which)
* wh-complex-4    | from NP to infinitivals -- supplementary only (to refute which)
* wh-complex-5    | from NP to gerund-participials -- supplementary only (passing which)
* wh-complex-6    | from genitive whose to NP (whose essay)
* wh-complex-7    | from determinative which to NP (which suggestion)
* wh-complex-8    | recursive application of more than one type


### relational (p1034)

* integrated-non-infinitival
* integrated-infinitival
* supplementary
* cleft 
* fused


### grammatical function (p1044)

* subject
* object
* predicative-complement
* complement-of-prep
* adjunct
* genitive-subject-determiner
* complement-of-aux-verb
* other


### implied classes

Additionally, the following high order classes have also been derived:

* _*_ => relative
* integrated-* => integrated
* wh-complex-* => wh-complex
* that|bare => non-wh
* wh-* => wh
