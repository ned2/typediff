#!/usr/bin/env python2

from __future__ import division


import sys
import os
import argparse
from collections import Counter, defaultdict

import delphin
import config
import stats


def argparser():
    ap = argparse.ArgumentParser()
    ap.add_argument("pid", type=int, metavar="P-ID", help="p-id of phenomenon being evaluated")
    ap.add_argument("results", metavar="RESULTS_FILE", help="Path to results file")
    ap.add_argument("profile", metavar="PROFILE", help="Path to profile")
    return ap


def get_predicted_iids(results_file):
    with open(results_file) as f:
        lines = f.readlines()
        iids = set(int(x.strip().split()[0]) for x in lines)
    return iids


def evaluate(predicted_iids, gold_iids, tot):
    intersection = predicted_iids.instersection(gold_iids)
    precision = len(intersection)/tot
    recall = len(intersection)/len(gold_iids)
    return precision, recall


def main():
    arg = argparser().parse_args()
    
    query = "select i-id where p-id = {}".format(arg.pid)
    tsdb_results = delphin.tsdb_query(query, arg.profile)
    gold_iids = set(int(x) for x in tsdb_results.split())
    all_iids = delphin.get_profile_ids(arg.profile):
    predicted_iids = get_predicted_iids(arg.results)
    print evaluate(predicted_iids, gold_iids, len(all_iids)) 


if __name__ == "__main__":
    sys.exit(main())

