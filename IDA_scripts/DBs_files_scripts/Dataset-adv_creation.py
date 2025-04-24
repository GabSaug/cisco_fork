import json
from os.path import join
from sklearn.model_selection import train_test_split
import numpy as np
import os
import pandas as pd
import random
import shutil
import argparse

from collections import Counter
from collections import defaultdict
from itertools import chain
from itertools import compress
from tqdm import tqdm

pdcsv = lambda x: pd.read_csv(x, index_col=0)


parser = argparse.ArgumentParser()
parser.add_argument("selected_pairs_path")
parser.add_argument("flowchart_path")
parser.add_argument("-o", "--output", default="../../DBs/Dataset-adv/")
parser.add_argument("--n_bb", "-n", default=5, help="Min nb of bb for a function", type=int)
args = parser.parse_args()

OUTPUT_DIR = args.output

if not os.path.isdir(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
    print(f"[D] DIR created: {OUTPUT_DIR}")

for dirname in ['validation']:
    tmp_path = os.path.join(OUTPUT_DIR, "pairs", dirname)
    if not os.path.isdir(tmp_path):
        os.makedirs(tmp_path)
        print(f"[D] DIR created: {tmp_path}")

for dirname in ['training', 'validation']:
    tmp_path = os.path.join(OUTPUT_DIR, "features", dirname)
    if not os.path.isdir(tmp_path):
        os.makedirs(tmp_path)
        print(f"[D] DIR created: {tmp_path}")

# **Read the flowchart CSV**

flowchart_file = pd.read_csv(args.flowchart_path)
print(flowchart_file.shape)

selected_columns = ['idb_path', 'fva', 'func_name', 'hashopcodes', 'bb_num', 'start_ea']
df = flowchart_file[selected_columns]
df.reset_index(inplace=True)
print("Flowchart selected columns df shape {}".format(df.shape))


# **Functions of interest**

file_pairs = open(args.selected_pairs_path, 'r')

flowchart_dict = dict()  # used to make the pairs, fast
flowchart_bb = dict()  # used to make the pairs, fast
for i, row in tqdm(df.iterrows(), total=len(df)):
    flowchart_dict[(row["idb_path"], row["func_name"])] = i
    flowchart_bb[(row["idb_path"], row["func_name"])] = row["bb_num"]
df = df.drop('index', axis=1)

pairs=list()
selected_pairs = pd.read_csv(file_pairs)
print("Selected pairs df shape {}".format(selected_pairs.shape))
skipped_funs = set()
small_funs = set()

for i, row in tqdm(selected_pairs.iterrows(), total=len(selected_pairs)):
    t1 = (row["idb_path_1"], row["func_name_1"])
    t2 = (row["idb_path_2"], row["func_name_2"])
    if t1 not in flowchart_dict.keys():
        skipped_funs.add(t1)
        continue
    elif t2 not in flowchart_dict.keys():
        skipped_funs.add(t2)
        continue
    index_1 = flowchart_dict[t1]
    index_2 = flowchart_dict[t2]
    if flowchart_bb[t1] < args.n_bb:
        small_funs.add(t1)
        continue
    if flowchart_bb[t2] < args.n_bb:
        small_funs.add(t2)
        continue
    pairs.append((index_1,index_2))

print("Skipped functions pairs from selected_pairs.csv that do not appear in flowchart_dict : {}".format(len(skipped_funs)))
print(f"Skipped {len(small_funs)} functions pairs from selected_pairs.csv that are too small (< {args.n_bb} bb)")

# skip df functions that do not appear in selected_pairs:
# Extract all (bin, fun) pairs from df_pairs
pairs_1 = set(zip(selected_pairs['idb_path_1'], selected_pairs['func_name_1']))
pairs_2 = set(zip(selected_pairs['idb_path_2'], selected_pairs['func_name_2']))
all_pairs = pairs_1.union(pairs_2)

# Create (bin, fun) tuples in df_funcs
df['pair'] = list(zip(df['idb_path'], df['func_name']))

# Filter based on whether the pair exists in all_pairs
df = df[df['pair'].isin(all_pairs)].drop(columns=['pair'])

print(f"Filtered flowchart: {df.shape}")

# Create training and validation split

df_training, df_validation = train_test_split(df, test_size=0.2, random_state=42, shuffle=True)

print(f"Train size: {len(df_training)}, Validation size: {len(df_validation)}")

df_training.reset_index(inplace=True, drop=True)
#df_validation.reset_index(inplace=True, drop=True)

# Create pairs for validation dataset

def create_pos_neg_validation(pairs, df_validation):
    pos_pairs_list, neg_pairs_list = list(), list()
    i=0
    for f1,f2 in tqdm(set(pairs)):
        i+=1
        if f1 in df_validation.index and f2 in df_validation.index:
            fun1 = df_validation.loc[f1]
            fun2 = df_validation.loc[f2]
            if fun1["func_name"] == fun2["func_name"]:
                pos_pairs_list.append(list(df_validation.loc[f1]) + list(df_validation.loc[f2]))
            else:
                neg_pairs_list.append(list(df_validation.loc[f1]) + list(df_validation.loc[f2]))

    # Create a new DataFrame
    columns = [x + "_1" for x in selected_columns ] + [x + "_2" for x in selected_columns ]
    pos_validation_pairs = pd.DataFrame(pos_pairs_list, columns=columns)
    neg_validation_pairs = pd.DataFrame(neg_pairs_list, columns=columns)
    print(f"Pos validation df size: {pos_validation_pairs.shape}, neg: {neg_validation_pairs.shape}")

    # Add the db_type column for compatibility reasons
    pos_validation_pairs['db_type'] = ['XM'] * pos_validation_pairs.shape[0]
    neg_validation_pairs['db_type'] = ['XM'] * neg_validation_pairs.shape[0]

    # Sort the rows
    pos_validation_pairs.sort_values(by=['idb_path_1', 'fva_1', 'idb_path_2', 'fva_2'], inplace=True)
    pos_validation_pairs.reset_index(inplace=True, drop=True)
    neg_validation_pairs.sort_values(by=['idb_path_1', 'fva_1', 'idb_path_2', 'fva_2'], inplace=True)
    neg_validation_pairs.reset_index(inplace=True, drop=True)

    # Remove hashopcodes columns
    del pos_validation_pairs['hashopcodes_1']
    del pos_validation_pairs['hashopcodes_2']
    del neg_validation_pairs['hashopcodes_1']
    del neg_validation_pairs['hashopcodes_2']

    # Save the DataFrame to file
    pos_validation_pairs.to_csv(join(OUTPUT_DIR, "pairs", "validation", "pos_validation_Dataset-adv.csv"))
    neg_validation_pairs.to_csv(join(OUTPUT_DIR, "pairs", "validation", "neg_validation_Dataset-adv.csv"))


create_pos_neg_validation(pairs, df_validation)
# Save the "selected functions" to a JSON.
# This is useful to limit the IDA analysis to some functions only.
df_list = [df_training, df_validation]
split_list = ["training", "validation"]

for split, df_t in zip(split_list, df_list):

    fset = set([tuple(x) for x in df_t[['idb_path', 'fva']].values])
    print("{}: {} functions".format(split, len(fset)))

    selected_functions = defaultdict(list)
    for t in fset:
        selected_functions[t[0]].append(int(t[1], 16))

    # Test
    assert(sum([len(v) for v in selected_functions.values()]) == len(fset))

    # Save to file
    with open(os.path.join(OUTPUT_DIR, "features", split, "selected_{}_Dataset-adv.json".format(split)), "w") as f_out:
        json.dump(selected_functions, f_out)

# Save the "selected functions" to a CSV.
# This will be useful to post-process the results.

df_validation.to_csv(os.path.join(OUTPUT_DIR, "validation_Dataset-adv.csv"))
df_training.to_csv(os.path.join(OUTPUT_DIR, "training_Dataset-adv.csv"))
