#!/usr/bin/env python3

import sys
import os
import argparse
from collections import Counter, defaultdict

from .delphin import tsdb_query, get_profile_ids


def argparser():
    ap = argparse.ArgumentParser()
    ap.add_argument("pid", type=int, metavar="P-ID", help="p-id of phenomenon being evaluated")
    ap.add_argument("profile", metavar="PROFILE", help="Path to profile")
    ap.add_argument("results", nargs='?', metavar="RESULTS_FILE", help="Path to results file")
    return ap


def get_predicted_iids(arg):
    if arg.results is not None:
        f = open(arg.results)
    else:
        f = sys.stdin

    lines = f.readlines()
    iids = set(int(x.strip().split()[0]) for x in lines if not x.startswith('#'))
    f.close()
    return iids


def evaluate(predicted_iids, gold_iids, tot):
    intersection = predicted_iids.intersection(gold_iids)
    precision = len(intersection)/tot
    recall = len(intersection)/len(gold_iids)
    return precision, recall


def main():
    arg = argparser().parse_args()
    query = "select i-id where p-id = {}".format(arg.pid)
    tsdb_results = tsdb_query(query, arg.profile)
    gold_iids = set(int(x) for x in tsdb_results.split())
    all_iids = get_profile_ids(arg.profile)
    predicted_iids = get_predicted_iids(arg)
    print(evaluate(predicted_iids, gold_iids, len(all_iids)))


if __name__ == "__main__":
    sys.exit(main())
