from __future__ import division

import math
import itertools
from collections import Counter

"""These functions assume that a probability distribution is
represented by a sequence of values which form... a probability
distribution. Functions that compare more than one distribution
require that the sequence have the same ordering of events.
""" 


def counts2dist(*counters):
    """Converts a list of Counters into probability distributions."""
    keys = set(itertools.chain.from_iterable(c.iterkeys() for c in counters))
    dists = []

    for c in counters:
        tot = sum(c.itervalues())
        dists.append([c[k]/tot for k in keys])
    
    return dists


def entropy(dist, base=math.e):
    """Return the entropy of a distribution."""
    return -sum([p * math.log(p, base) for p in dist if p != 0])


def js_divergence(*dists):
    """Calculates the Jenson Shannon Divergence of multiple probability
    distributions"""
    weight = 1/len(dists)
    js_left = [0]*len(dists[0])
    js_right = 0    

    for pd in dists:
        for i,p in enumerate(pd):
            js_left[i] += p*weight
        js_right += weight*entropy(pd, math.e)

    return entropy(js_left) - js_right


def js_divergence2(dista, distb):
    """Calculates the Jenson Shannon Divergence of two probability
    distributions"""
    func = lambda x, y: 0 if x == 0 else x*math.log(x/y) 
    AM = sum(func(a, 0.5*(a+b)) for a,b in itertools.izip(dista, distb))
    BM = sum(func(b, 0.5*(a+b)) for a,b in itertools.izip(dista, distb))
    return 0.5*AM + 0.5*BM


def kl_divergence(dista, distb):
    """Calculates the KL divergence of two probabiliy distributions.
    Note that KL is techundefined when Pr(a) = 0."""
    def func(a, b):
        if a == 0 or b == 0:
            # Avoid dividing by zero/ 
            # taking log of zero
            return 0
        else:
            return b*math.log(b/a) 
    return sum(func(a,b) for a,b in itertools.izip(dista, distb))
