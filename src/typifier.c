/*
 *
 * A program to extract the type names of all feature structures
 * within the final AVM produced for a derivation of a string by a
 * DELPH-IN grammar. Takes as input a derivation tree string produced
 * by ACE either as a file on the command line or from standard input.
 * 
 * This program makes use of ACE, the Answer Constraint Engine, a
 * processor for DELPH-IN HPSG grammars.
 * 
 * http://sweaglesw.org/linguistics/ace/
 * 
 * Many thanks to Woodley Packard, the author of ACE, for his help
 * putting this code together.
 * 
 * To compile on a system with ACE installed:
 * $ gcc -o typifier typifier.c -lace
 * 
 * To compile with ace libraries baked in:
 * $ gcc src/typifier.c -Wl,-Bstatic -lace -lrepp -lboost_regex -lstdc++ -Wl,-Bdynamic -lm -lutil -lpthread -ldl ~/logon/lingo/lkb/lib/linux.x86.64/libitsdb.a ~/logon/lingo/lkb/lib/linux.x86.64/libpvm3.a -o bin/typifier 
 * 
 * Usage:
 * $ typifier ace-dat-file-path derivation-file
 * 
 * Alternatively accepts derivation input from stdin.
 */


#include    <stdio.h>
#include    <string.h>
#include    <stdlib.h>
#include    <assert.h>

#include    <ace/reconstruct.h>
#include    <ace/dag.h>

#define MARKER 0xDEADBEEF

int GLBFLAG = -1;


char *dqescape(char *s)
{
    char *s2 = malloc(strlen(s)*2+1), *p = s2;
    while(*s)
    {
        if(*s=='\b') { *p++ = '\\'; *p++ = 'b'; s++; continue; }
        if(*s=='\f') { *p++ = '\\'; *p++ = 'f'; s++; continue; }
        if(*s=='\n') { *p++ = '\\'; *p++ = 'n'; s++; continue; }
        if(*s=='\r') { *p++ = '\\'; *p++ = 'r'; s++; continue; }
        if(*s=='\t') { *p++ = '\\'; *p++ = 't'; s++; continue; }
        // specs for json apparently say you should escape '/'...
        if(*s == '\'' || *s == '\\' || *s == '"' || *s=='/')*p++='\\';
        *p++ = *s++;
    }
    *p++ = 0;
    return s2;
}


int prefix(const char *pre, const char *str)
{
    return strncmp(pre, str, strlen(pre)) == 0;
}


void resolve_glbs_naive(struct type *t)
{
    char *name = t->name;
    if (prefix("g(", name)) { 
        int i;
        for(i=0;i<t->nparents;i++)
            resolve_glbs_naive(t->parents[i]);
    } else {
        printf("%s\n", name);
    }
}


void resolve_glbs(struct type *t, int flag)
{
	char *name = t->name;
    if (prefix("g(", name)) { 
    	int i;
		// prevent visiting the same type more than once.
		// the hierarchy gets pretty hairy in some places.
		// We need to use a different flag for each per top-level 
        // call to resolve_glbs() so as to preserve the number of 
        // times that a type appears. This is more efficient that 
        // resetting the flag every time..
		if(t->ndaughters == flag)
            return;

		t->ndaughters = flag;

        for(i=0;i<t->nparents;i++) {
            resolve_glbs(t->parents[i], flag);
        }
    } else {
        printf("%s\n", name);
    }
}


void recurse(struct dg *d)
{
    d = dereference_dg(d);

    if(d->gen == MARKER)
        return;

    d->gen = MARKER;
    resolve_glbs(d->xtype, GLBFLAG);
    GLBFLAG--;

    int i;
    struct dg **arcs = DARCS(d);

    for(i=0;i<d->narcs;i++)
        recurse(arcs[i]);
}


// This function is modelled off fprint_tree from session.c in the
// full forest treebanker.
void print_json_tree(struct tree *t)
{
    int i;
    int lexical = 0;

    if(t->ndaughters == 1 && t->daughters[0]->ndaughters == 0)lexical = 1;

    char *esc, *sesc, *resc, *lexident;
    sesc = dqescape(t->shortlabel);
    if(lexical)
    {
        // for whatever reason, grammarians prefer to see the lexical
        // type as the full-form sign for a lexical node, rather than
        // the lexeme identifier
        struct lexeme *lex = get_lex_by_name_hash(t->label);
        esc = dqescape(lex->lextype->name);
        lexident = dqescape(t->daughters[0]->label);
        printf("{\"label\": \"%s\", \"shortlabel\": \"%s\", \"rule\": false, \"from\":%d, \"to\":%d, \"lexident\": \"%s\", \"daughters\": [", esc, sesc, t->cfrom, t->cto, lexident);
    } else { 
        esc = dqescape(t->label);
        struct rule *rule = get_rule_by_name(t->label);
        if(!rule) { fprintf(stderr, "no such rule '%s'\n", t->label);}
        resc = dqescape(rule->dg->xtype->name);
        printf("{\"label\": \"%s\", \"shortlabel\": \"%s\", \"rule\": \"%s\", \"from\":%d, \"to\":%d, \"daughters\": [", esc, sesc, resc, t->cfrom, t->cto);
    }

    free(esc);
    free(sesc);
    if (!lexical)free(resc);

    if(!lexical)for(i=0;i<t->ndaughters;i++)
    {
        if(i)printf(",");
        print_json_tree(t->daughters[i]);
    }
    printf("]}");
}


void callback(struct tree *edge, struct dg *avm)
{
    /*printf("%s\n", edge->label);*/
    edge->shortlabel = label_dag(avm, "?");
    recurse(avm);
}


int main(int argc, char *argv[])
{
    FILE *input;

    if (argc > 2){
        input = fopen(argv[2], "r");
    } else {
        input = stdin;
    }
 
    ace_load_grammar(argv[1]);
    clear_slab();
    clear_mrs();
    
    assert(input || !"can't open file");
    char str[1024000];
    fread(str, 1024000, 1, input);
    struct tree *t = string_to_tree(str);

    if (!t) 
        assert(! "derivation format error");

    struct dg *avm = reconstruct_tree(t, callback);

    if(avm) {
        printf("\n");
        print_json_tree(t);
        printf("\n");
        return 0;
    } else {
        fprintf(stderr, "Failed to reconstruct AVM. Wrong grammar version?\n");
        return -1;
    }
}
