#!/usr/bin/env python
import json
import pandas as pd
from tqdm import tqdm
from collections import defaultdict
import os
import argparse
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(description="Clean and structure dataset pairs for model testing.")
    parser.add_argument("selected_pairs_path", help="Path to CSV containing pairs of interest")
    parser.add_argument("flowchart_path", help="Path to flowchart CSV containing function features")
    parser.add_argument("output_pairs_testing", help="Path for the output pairs CSV")
    parser.add_argument("output_selected_json", help="Path for the output JSON (IDA analysis limit)")
    parser.add_argument("output_testing_csv", help="Path for the output features CSV")
    
    parser.add_argument("--name", default="Dataset-Muaz", help="Name of the dataset")
    parser.add_argument("--description", default="No description provided", help="Description for description.json")
    parser.add_argument("--n_bb", "-n", default=5, type=int, help="Min number of basic blocks per function")
    return parser.parse_args()

def main():
    args = parse_args()
    
    # 1. Load Data
    print(f"[*] Loading flowchart from {args.flowchart_path}...")
    flowchart_file = pd.read_csv(args.flowchart_path)
    
    selected_columns = ['idb_path', 'fva', 'func_name', 'hashopcodes', 'bb_num']
    df_features = flowchart_file[selected_columns].copy()
    
    # --- FIX START: Ensure unique keys for the dictionary lookup ---
    # We drop duplicates based on the primary key (idb_path, func_name)
    print("[*] Ensuring unique function entries...")
    df_features = df_features.drop_duplicates(subset=['idb_path', 'func_name'])
    # --- FIX END ---
    
    df_features['key'] = list(zip(df_features.idb_path, df_features.func_name))
    lookup = df_features.set_index('key').to_dict('index')

    # 2. Process Pairs
    print(f"[*] Processing pairs from {args.selected_pairs_path}...")
    selected_pairs = pd.read_csv(args.selected_pairs_path)
    
    valid_pairs = []
    skipped_count = 0
    small_count = 0
    
    for _, row in tqdm(selected_pairs.iterrows(), total=len(selected_pairs)):
        t1 = (row["idb_path_1"], row["func_name_1"])
        t2 = (row["idb_path_2"], row["func_name_2"])
        
        if t1 not in lookup or t2 not in lookup:
            skipped_count += 1
            continue
            
        if lookup[t1]['bb_num'] < args.n_bb or lookup[t2]['bb_num'] < args.n_bb:
            small_count += 1
            continue
            
        record = {f"{k}_1": v for k, v in lookup[t1].items()}
        record.update({f"{k}_2": v for k, v in lookup[t2].items()})
        valid_pairs.append(record)

    print(f"[!] Skipped (Missing): {skipped_count} | Skipped (Small): {small_count}")

    # 3. Structure Testing DataFrame
    if not valid_pairs:
        print("[!] Error: No valid pairs found. Check your input CSVs.")
        return

    testing_df = pd.DataFrame(valid_pairs)
    testing_df['db_type'] = 'XM'
    
    cols_to_drop = ['hashopcodes_1', 'hashopcodes_2', 'key_1', 'key_2']
    testing_df = testing_df.drop(columns=[c for c in cols_to_drop if c in testing_df.columns])
    
    testing_df.sort_values(by=['idb_path_1', 'fva_1', 'idb_path_2', 'fva_2'], inplace=True)
    testing_df.drop_duplicates(inplace=True)
    
    # 4. Generate JSON for IDA Analysis
    unique_funs_df = pd.concat([
        testing_df[['idb_path_1', 'fva_1']].rename(columns={'idb_path_1': 'path', 'fva_1': 'fva'}),
        testing_df[['idb_path_2', 'fva_2']].rename(columns={'idb_path_2': 'path', 'fva_2': 'fva'})
    ]).drop_duplicates()

    selected_json = defaultdict(list)
    for _, row in unique_funs_df.iterrows():
        try:
            val = int(str(row['fva']), 16)
            selected_json[row['path']].append(val)
        except ValueError:
            continue

    # 5. Filter Flowchart for CSV Output
    valid_set = set(zip(unique_funs_df.path, unique_funs_df.fva))
    mask = flowchart_file.apply(lambda x: (x['idb_path'], x['fva']) in valid_set, axis=1)
    dataset_csv = flowchart_file[mask].copy()
    
    if 'bb_list' in dataset_csv.columns:
        dataset_csv.drop(columns=['bb_list'], inplace=True)

    # 6. Save Files
    testing_df.to_csv(args.output_pairs_testing, index=False)
    dataset_csv.to_csv(args.output_testing_csv, index=False)
    
    with open(args.output_selected_json, "w") as f:
        json.dump(selected_json, f)

    # 7. Generate description.json
    out_dir = Path(args.output_selected_json).parent
    description_data = {
        "name": args.name,
        "size": f"{len(dataset_csv)} functions",
        "description": args.description,
        "nbr_pairs": len(testing_df),
        "nbr_functions": len(unique_funs_df),
        "size_train": 0,
        "size_testing": len(testing_df),
        "size_validation": 0,
        "pairs_path": os.path.join("./pairs/", os.path.basename(args.output_pairs_testing)),
        "testing_path": os.path.basename(args.output_testing_csv)
    }
    
    with open(out_dir / "description.json", "w") as f:
        json.dump(description_data, f, indent=4)

    print(f"[*] Done. Created {len(testing_df)} pairs.")
    print(f"[*] Metadata saved to {out_dir}/description.json")

if __name__ == "__main__":
    main()
