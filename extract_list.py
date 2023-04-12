import os
import argparse
import random
import filelist
import re
import collections

parser = argparse.ArgumentParser()

parser.add_argument("--model", type=str, required=True)
parser.add_argument("--val_ratio", type=int, default=1)
parser.add_argument("--min_len", type=int, default=3)
parser.add_argument("--min_set", type=int, default=3)

args = parser.parse_args()

all_list_path = filelist.get_all_list_path(args)
train_list_path = filelist.get_train_list_path(args)
val_list_path = filelist.get_val_list_path(args)
with open(train_list_path, 'w', encoding='utf-8') as train_list_file, \
     open(val_list_path, 'w', encoding='utf-8') as val_list_file, \
     open(all_list_path, 'r', encoding='utf-8') as all_list_file:
    strs = [(path, line.strip()) for path, line in map(lambda s: s.split('|'), all_list_file.readlines())]
    strs = sorted(strs, key=lambda x: x[1])
    filtered = []
    for f, l in strs:
        counter = collections.Counter(l)
        if len(l) < args.min_len or len(counter) < args.min_set:
            print('filtered out: %s:%s' % (f, l))
            continue
        filtered.append('%s|%s\n' % (f, l))
    strs = filtered
    cnt = len(strs)
    random.shuffle(strs)
    val_cnt = cnt // 100 * args.val_ratio
    for s in strs[:val_cnt]:
        val_list_file.write(s)
    for s in strs[val_cnt:]:
        train_list_file.write(s)