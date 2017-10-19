#!/usr/bin/env python3
# -* coding:utf-8 -*-

# Author: Francis Bond

import MeCab
import sys

m = MeCab.Tagger('-Ochasen')
punct = "!\"!&'()*+,-−./;<=>?@[\]^_`{|}~。！？…．　○●◎＊☆★◇◆"

def jp2yy(sent):
    """take a Japanese sentence encoded in UTF8 and convert to YY-mode
    using mecab"""
    ### (id, start, end, [link,] path+, form [surface], ipos, lrule+[, {pos p}+])
    ### set ipos as lemma (just for fun)
    ### fixme: do the full lattice
    yid = 0
    start = 0
    cfrom = 0
    cto = 0
    yy = list()
    sent_decoded = sent.decode('utf-8')

    for tok in m.parse(sent).split('\n'):
        if tok and tok != 'EOS':
            (form, p, lemma, p1, p2, p3) = tok.decode('utf-8').split('\t')
            if form in punct:
                continue
            p2 = p2 or 'n'
            p3 = p3 or 'n'
            pos = "%s:%s-%s" % (p1, p2, p3)       ## wierd format jacy requires
            cfrom = sent_decoded.find(form, cto)  ## first instance after last token
            cto = cfrom + len(form)               ## find the end
            yy.append('(%d, %d, %d, <%d:%d>, 1, "%s", %s, "null", "%s" 1.0)' % \
                (yid, start, start +1, cfrom, cto, form, 0, pos))
            yid += 1
            start += 1
    return "".join(yy).encode('utf-8')


if __name__ == "__main__":
    sent = sys.argv[1]
    print("".join(jp2yy(sent)))
