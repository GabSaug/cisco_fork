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
    # Ensure we only have the columns we need from the embeddings
    df_asm2vec = df_asm2vec[['idb_path', 'fva', 'embeddings']].copy()

    # First merge for the first function in the pair
    df_pairs = df_pairs.merge(df_asm2vec,
                              how='left',
                              left_on=['idb_path_1', 'fva_1'],
                              right_on=['idb_path', 'fva'])
    
    # Drop the redundant columns from the right dataframe and rename the embedding
    df_pairs.drop(columns=['idb_path', 'fva'], inplace=True)
    df_pairs.rename(columns={'embeddings': 'embeddings_1'}, inplace=True)

    # Second merge for the second function in the pair
    df_pairs = df_pairs.merge(df_asm2vec,
                              how='left',
                              left_on=['idb_path_2', 'fva_2'],
                              right_on=['idb_path', 'fva'])
    
    # Drop the redundant columns again
    df_pairs.drop(columns=['idb_path', 'fva'], inplace=True)
    df_pairs.rename(columns={'embeddings': 'embeddings_2'}, inplace=True)

    # Compute similarity
    df_pairs['sim'] = compute_cosine_similarity(df_pairs)
    
    # Define the final columns we want to keep
    cols_to_keep = ['idb_path_1', 'fva_1', 'func_name_1', 'idb_path_2', 'fva_2', 'func_name_2', 'sim']
    
    # Filter only if they exist to avoid the KeyError
    existing_cols = [c for c in cols_to_keep if c in df_pairs.columns]
    df_pairs = df_pairs[existing_cols]
    
    return df_pairs

# ### Process Dataset-1 results

DB_PATH = "../../DBs/Dataset-Muaz/pairs/"

embedding_path = os.path.join(
    "asm2vec_inference_Dataset-Muaz-testing", "embeddings.csv")
print("[D] Processing {}".format(embedding_path))
if not os.path.isfile(embedding_path):
    print("[!] File not found: {}".format(embedding_path))
    exit(1)

df_emb = pd.read_csv(embedding_path)
df_testing = pd.read_csv(
        os.path.join(DB_PATH, "pairs_testing_Dataset-Muaz.csv"), index_col=0).reset_index()
df_testing = compute_embedding_similarity(df_testing, df_emb)
df_testing.to_csv(
        "asm2vec_inference_Dataset-Muaz-testing/pairs_results_Dataset-Muaz_a2v.csv",index=False)

