/*
 *
 * A program to generate an XML dump of the type hierarchy of a
 * DELPH-IN grammar. This XML format matches that produced by the 
 * command  (lkb::types-to-xml :file "~/types.xml") in the LKB.
 * The hierarchy is printed to standard output.
 * 
 * This program makes use of ACE, the Answer Constraint Engine, a
 * processor for DELPH-IN HPSG grammars.
 *
 * http://sweaglesw.org/linguistics/ace/
 * 
 * Many thanks to Woodley Packard, the author of ACE, for his help
 * putting this code together.
 *
 * Usage: 
 * $ dumphierchary grammar-image > types.xml
 * 
 */


#include	<stdio.h>
#include	<string.h>
#include	<stdlib.h>

#include	<assert.h>
#include	<ace/type.h>


int prefix(const char *pre, const char *str)
{
    return strncmp(pre, str, strlen(pre)) == 0;
}


char *convert_glb(char *str)
{
    if (prefix("g(", str)) {
        int num;
        char *new = (char *)malloc(sizeof(char)*10);
        sscanf(str, "g(%d)", &num);
        sprintf(new, "glbtype%d", num); 
        return new;
    } else {
        return str;
    }
}


int main(int argc, char	*argv[])
{
	ace_load_grammar(argv[1]);
	clear_slab();
	clear_mrs();

	struct type_hierarchy *th = default_type_hierarchy();

	int i, j;
    char *name;
	for(i=0;i<th->ntypes;i++)
	{
		struct type	*t = th->types[i];

        name = convert_glb(t->name);
		printf("<type name=\"%s\">\n", name);
        if (strncmp(name, t->name, strlen(name)) != 0) free(name);

		printf("  <parents>\n");        
		for(j=0;j<t->nparents;j++){
            name = convert_glb(t->parents[j]->name);
			printf("    <type name=\"%s\"/>\n", name);
            if (strncmp(name, t->parents[j]->name, strlen(name)) != 0) free(name);
        }
		printf("  </parents>\n");        

		printf("  <children>\n");        
		for(j=0;j<t->ndaughters;j++){
            name = (char *)malloc(sizeof(char)*10);
            name = convert_glb(t->daughters[j]->name);
			printf("    <type name=\"%s\"/>\n", name);
            if (strncmp(name, t->daughters[j]->name, strlen(name)) != 0) free(name);
        }
		printf("  </children>\n");        
		printf("</type>\n");        
	}

	return 0;
}
