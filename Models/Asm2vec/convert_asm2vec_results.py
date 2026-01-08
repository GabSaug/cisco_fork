#!/usr/bin/env python
# coding: utf-8

import numpy as np
import os
import pandas as pd

from scipy.spatial.distance import cosine
from tqdm import tqdm

def cosine_similarity(e1, e2):
    return 1 - cosine(e1, e2)

def compute_cosine_similarity(df_input):
    sim_list = list()
    for idx, row in tqdm(df_input.iterrows(), total=len(df_input)):

        if row['embeddings_1'] is np.nan or \
                row['embeddings_2'] is np.nan:
            print("[!] Missing value in (idx:{})".format(idx))
            sim_list.append(0)
            continue

        e1 = np.array([float(x) for x in row['embeddings_1'].split(";")])
        e2 = np.array([float(x) for x in row['embeddings_2'].split(";")])
        sim_list.append(cosine_similarity(e1, e2))
    return sim_list

def compute_embedding_similarity(df_pairs, df_asm2vec):

    df_asm2vec = df_asm2vec[['idb_path', 'fva', 'embeddings']]

    df_pairs = df_pairs.merge(df_asm2vec,
                              how='left',
                              left_on=['idb_path_1', 'fva_1'],
                              right_on=['idb_path', 'fva'])
    df_pairs.rename(columns={'embeddings': 'embeddings_1'}, inplace=True)

    df_pairs = df_pairs.merge(df_asm2vec,
                              how='left',
                              left_on=['idb_path_2', 'fva_2'],
                              right_on=['idb_path', 'fva'])
    df_pairs.rename(columns={'embeddings': 'embeddings_2'}, inplace=True)

    df_pairs['sim'] = compute_cosine_similarity(df_pairs)
    df_pairs = df_pairs[['idb_path_1','fva_1', 'func_name_1', 'idb_path_2','fva_2', 'func_name_2', 'sim']]
    return df_pairs

# ### Process Dataset-1 results

DB1_PATH = "../../DBs/Dataset-1/pairs/testing/"
EMB_FOLDER = "./asm2vec_inference_Dataset-1-testing"
embedding_path = os.path.join(EMB_FOLDER, "embeddings.csv")


    #df_pos = pd.read_csv(os.path.join(DB1_PATH, "pos_testing_Dataset-1.csv"), index_col=0)
    #df_neg = pd.read_csv(os.path.join(DB1_PATH, "neg_testing_Dataset-1.csv"), index_col=0)
    #df_pos_rank = pd.read_csv(os.path.join(DB1_PATH, "pos_rank_testing_Dataset-1.csv"), index_col=0)
    #df_neg_rank = pd.read_csv(os.path.join(DB1_PATH, "neg_rank_testing_Dataset-1.csv"), index_col=0)

    #df_pos = compute_embedding_similarity(df_pos, df_emb)
    #df_neg = compute_embedding_similarity(df_neg, df_emb)
    #df_pos_rank = compute_embedding_similarity(df_pos_rank, df_emb)
    #df_neg_rank = compute_embedding_similarity(df_neg_rank, df_emb)

    #folder = "a2v"
    #df_pos.to_csv("EMB_FOLDER/pos_testing_{}.csv".format(folder), index=False)
    #df_neg.to_csv("EMB_FOLDER/neg_testing_{}.csv".format(folder), index=False)
    #df_pos_rank.to_csv("EMB_FOLDER/pos_rank_testing_{}.csv".format(folder), index=False)
    #df_neg_rank.to_csv("EMB_FOLDER/neg_rank_testing_{}.csv".format(folder), index=False)

# ### Process Dataset-2 results

# In[7]:


#DB2_PATH = "../../DBs/Dataset-2/pairs/"
#
#for folder in [
#    'Dataset-2_asm2vec_e10',
#    'Dataset-2_pvdbow_e10',
#        'Dataset-2_pvdm_e10']:
#
#    embedding_path = os.path.join(
#        "../data/raw_results/Asm2vec/", folder, "embeddings.csv")
#    print("[D] Processing {}".format(embedding_path))
#    if not os.path.isfile(embedding_path):
#        print("[!] File not found: {}".format(embedding_path))
#        continue
#
#    df_emb = pd.read_csv(embedding_path)
#
#    df_pos = pd.read_csv(os.path.join(DB2_PATH, "pos_testing_Dataset-2.csv"), index_col=0)
#    df_neg = pd.read_csv(os.path.join(DB2_PATH, "neg_testing_Dataset-2.csv"), index_col=0)
#    df_pos_rank = pd.read_csv(os.path.join(DB2_PATH, "pos_rank_testing_Dataset-2.csv"), index_col=0)
#    df_neg_rank = pd.read_csv(os.path.join(DB2_PATH, "neg_rank_testing_Dataset-2.csv"), index_col=0)
#    
#    df_pos = compute_embedding_similarity(df_pos, df_emb)
#    df_neg = compute_embedding_similarity(df_neg, df_emb)
#    df_pos_rank = compute_embedding_similarity(df_pos_rank, df_emb)
#    df_neg_rank = compute_embedding_similarity(df_neg_rank, df_emb)
#
#    df_pos.to_csv("../data/Dataset-2/pos_testing_{}.csv".format(folder), index=False)
#    df_neg.to_csv("../data/Dataset-2/neg_testing_{}.csv".format(folder), index=False)
#    df_pos_rank.to_csv("../data/Dataset-2/pos_rank_testing_{}.csv".format(folder), index=False)
#    df_neg_rank.to_csv("../data/Dataset-2/neg_rank_testing_{}.csv".format(folder), index=False)

# Process Dataset-Muaz results

DB_PATH = "../../DBs/Dataset-Muaz/pairs/"

embedding_path = os.path.join(
    "asm2vec_inference_Dataset-Muaz-testing", "embeddings.csv")
print("[D] Processing {}".format(embedding_path))
if not os.path.isfile(embedding_path):
    print("[!] File not found: {}".format(embedding_path))
    exit(1)

df_emb = pd.read_csv(embedding_path)
df_testing = pd.read_csv(
        os.path.join(DB_PATH, "pairs_testing_Dataset-Muaz.csv"), index_col=0)
df_testing = compute_embedding_similarity(df_testing, df_emb)
df_testing.to_csv(
        "asm2vec_inference_Dataset-Muaz-testing/pairs_results_Dataset-Muaz_a2v.csv",index=False)

