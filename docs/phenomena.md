# Phenomenon Annotated Profiles Available in Typediff

## H&P Relative Constructions

This profile is made up of exemplars extracted from chapter 12 of Huddleston and
Pullum's Cambridge Grammar of the English Language (H&P). It includes 417
exemplars extracted from the portion of chapter 12 that deals with relative
constructions. Of these, 333 are both marked as grammatical and being an
instance of a relative construction. These 333 are further annotated based on
different properties identified by H&P as being salient to their analysis of
relative constructions.

Each exemplar is annotated with three orthogonal categories. Within H&P the
exemplars typically only illustrate a value of one of these categories, however
each item has been manually annotated with values for all three categories. The
categories are:

1. **Formal:** The characteristic form that the relative construction takes 
2. **Relational:** Distinguishes the relation of the relative construction to the
   larger structure that contains it.
3. **Grammatical Function:** The grammatical function of the constituent that is
   being relativised

The values that each of these categories can take are included below. See the
noted page numbers of H&P for more information about these phenomenon
categories.


### Formal (p1034 and p1036-1044)

* **that**
* **bare**
* **wh-simple**
* **wh-complex-1**    | from complement of preposition to PP (*behind which*)
* **wh-complex-2**    | from PP complement of noun to NP (*the result of which*)
* **wh-complex-3**    | from PP to AdjP (*prominent among which*)
* **wh-complex-4**    | from NP to infinitivals - supplementary only (*to refute which*)
* **wh-complex-5**    | from NP to gerund-participials - supplementary only (*passing which*)
* **wh-complex-6**    | from genitive whose to NP (*whose essay*)
* **wh-complex-7**    | from determinative which to NP (*which suggestion*)
* **wh-complex-8**    | recursive application of more than one type


### Relational (p1034)

* **integrated-non-infinitival**
* **integrated-infinitival**
* **supplementary**
* **cleft**
* **fused**


### Grammatical function (p1044)

* **subject**
* **object**
* **predicative-complement**
* **complement-of-prep**
* **adjunct**
* **genitive-subject-determiner**
* **complement-of-aux-verb**
* **other**


### Implied classes

The labels from the above three categories make up the entire annotation schema,
however in some case they represent fine-grain categories that divide up a
superordinate category that is not explicitly represented in the annotation
scheme. The following implied labels have therefore been derived from the
annotation scheme and applied as additional annotations:


* **\*** :arrow_right: **relative**
* **integrated-\*** :arrow_right: **integrated**
* **wh-complex-\*** :arrow_right: **wh-complex**
* **that**|**bare** :arrow_right: **non-wh**
* **wh-\*** :arrow_right: **wh**


### Descriptions of the Phenomena

This is a summarised version of the descriptions in H&P chapter 12. See above
for relevant page numbers.

#### Formal

The formal category is divided up into **wh** relatives, those that use
relativising words such as *who*, *whom*, *whose*, *which* etc (1), and
**non-wh** relatives that are divided into **bare** and **that** relatives,
depending on whether they use *that* as a relative word (2) or have a gap (3).
 

1. He'll be glad to take the toys [which you don't want].
2. He'll be glad to take the toys [that you don't want].
3. He'll be glad to take the toys [you don't want].

The *wh* relatives are also divided into **wh-simple** and **wh-complex**
relatives. Simple relative phrases consist of a relative word on its own (4),
whereas a complex relative consists of a relative word with other
material. Complex relative phrases are broken down into different subtypes
(5-11), corresponding to how how the additional material in the relative phrase
"percolate" up from the subordinate clause. These complex types can be stacked,
with multiple types of percolations applying to the same relative phrase (eg 12,
which involves wh-complex-4 + wh-complex-1). In our coding scheme, these have
all been collapsed into a single label corresponding to the recursive
application of multiple complex types (wh-complex-8). The different categories
along with the corresponding percolations are:

* **wh-complex-1** (5) complement of preposition :arrow_right: PP
* **wh-complex-2** (6) PP complement of noun:arrow_right: NP
* **wh-complex-3** (7) PP :arrow_right: AdjP
* **wh-complex-4** (8) NP :arrow_right: infinitival (supplementary only)
* **wh-complex-5** (9) NP :arrow_right: gerund-participial (supplementary only)
* **wh-complex-6** (10) genitive whose :arrow_right: NP
* **wh-complex-7** (11) determinative which :arrow_right: to NP
* **wh-complex-8** (12) recursive application of more than one type

4.  I can't find the book [*which* he recommended].
5.  the curtain [*behind which* Kim was hiding]
6.  She's just sat her final exam, [*the result of which*, we expect next week].
7.  The many varieties of mammalian skin secretions perform a wide range of functions, [*prominent among which* is sexual attraction].
8.  I became disturbed by a 'higher criticism' of the Bible, [*to refute which* I felt the need of a better knowledge of Hebrew and archaeology].
9.  They take a rigorous examination, [*passing which* confers on the student a virtual guarantee of a place at the university].
10. the student [*whose essay* he plagiarised]
11. I said that it might be more efficient to hold the meeting on Saturday morning, [*which suggestion* they all enthusiastically endorsed].
12. Here is Dr Van Buren, [*in order to interview whom* Phelps says he was prepared to fly to Copenhagen].


#### Relational

These categories are distinguished from each other by the relation of the relative
construction to the larger containing structure.

**Integrated** relatives (13) typically function as a modifier within a nominal
constituent and are integrated into the containing structure both prosodically
and in terms of their informational content, prototypically restricting the
denotation of the head nominal it modifies (often referred to as a *restricted
relative*). Since integrated relatives are the only relational category that can
occur with infinitival forms, to simplify annotation, this category is divided
into the two sub categories of **integrated-non-infinitival** and
**integrated-infinitival**.


**Supplementary** relatives (14) add extra information about the antecedent that
is not fully integrated into the structure of the surrounding clause and not
required to constrain the reference of the antecedent. It is characteristically
marked through prosody or punctuation as being separate from the surrounding
structure.

A **cleft** relative (15) is the clause that occurs after the foregrounded
element in an *it*-cleft construction.

**Fused** relatives, which are always of the *wh* type, are characterised by the
antecedent being fused together with the relative clause. 

13. The boys [who defaced the statue] were expelled.
14. My father, [who retired last year], now lives in Florida.
15. It was Kim [who wanted Pat as treasurer].
16. [What you say] is quite right.


#### Grammatical Function

These categories code the grammatical function of the constituent that is being
relativised. Our labels are the possible values identified by H&P plus
**other** as a catchall for any other observed grammatical function.

* (24) **subject**
* (25) **object**
* (26) **predicative-complement**
* (27) **complement-of-prep**
* (28) **adjunct**
* (29) **genitive-subject-determiner**
* (30) **complement-of-aux-verb**
* (31) **other**

17. The **man** [*who* came to dinner] turned out to be from my home town.
18. This is the *letter* [that she received \_\_\_ from the Governor].
19. Her book displays the fine sceptical intelligence of the *scholar* [she is \_\_\_].
20. The *penknife* [that he was trying to cut it with \_\_\_] was blunt.
21. Do you remember the *day* [we met Kim at the races \_\_\_]?
22. One cannot tailor a suit for a *client* [*whose* measurements remain unknown].
23. He told me to *design it myself*, [which I simply can't \_\_\_].


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


