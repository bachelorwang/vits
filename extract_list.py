import os
import argparse
import random
import common

parser = argparse.ArgumentParser()

parser.add_argument("--model", type=str, required=True)
parser.add_argument("--val_ratio", type=int, default=1)
parser.add_argument("--min_len", type=int, default=4)
parser.add_argument("--min_set", type=int, default=4)

args = parser.parse_args()

all_list_path = common.get_all_list_path(args)
with open('filelists/train_%s.txt' % args.model, 'w', encoding='utf-8') as train_list_file, \
     open('filelists/val_%s.txt' % args.model, 'w', encoding='utf-8') as val_list_file, \
     open(all_list_path, 'r', encoding='utf-8') as all_list_file:
    strs = [(path, idx, line.strip()) for path, idx, line in map(lambda s: s.split('|'), all_list_file.readlines())]
    strs = sorted(strs, key=lambda x: x[2])
    filtered = []
    for f, i, l in strs:
        if len(l) < args.min_len or len(set(l)) < args.min_set:
            print('filtered out: %s:%s' % (f, l))
            continue
        filtered.append('%s|%s|%s\n' % (f, i, l))
    strs = filtered
    cnt = len(strs)
    random.shuffle(strs)
    val_cnt = cnt // 100 * args.val_ratio
    for s in strs[:val_cnt]:
        val_list_file.write(s)
    for s in strs[val_cnt:]:
        train_list_file.write(s)