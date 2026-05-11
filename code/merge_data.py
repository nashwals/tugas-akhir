#!/usr/bin/env python3
"""
Data Merge Utility
==================
Merges original training data with new submissions collected from the web app.
Use this before retraining the model.
"""

import pandas as pd
import os
from datetime import datetime

def merge_data():
    """Merge original and new submission data"""
    
    print("\n" + "="*80)
    print("DATA MERGE UTILITY")
    print("="*80 + "\n")
    
    # File paths
    original_candidates = [
        'data/submissions.csv',
        'data/burnout_submissions.csv'
    ]
    candidate_new_files = [
        'data/new_contributions.csv',
        'data/new_submissions.csv'
    ]
    original_file = None
    for candidate in original_candidates:
        if os.path.exists(candidate):
            original_file = candidate
            break

    if original_file is None:
        print(f"❌ Error: Original file not found: {original_candidates[0]}")
        return

    original_stem = os.path.splitext(os.path.basename(original_file))[0]
    output_file = f'data/{original_stem}_merged_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    # Check if files exist
    new_file = None
    for candidate in candidate_new_files:
        if os.path.exists(candidate):
            new_file = candidate
            break

    if not new_file:
        print(f"⚠️  No new submissions found yet: {candidate_new_files[0]}")
        print("   Web app hasn't collected any data yet.")
        return
    
    # Load data
    print(f"Loading data...")
    df_original = pd.read_csv(original_file)
    df_new = pd.read_csv(new_file)
    
    print(f"✓ Original data: {len(df_original)} samples")
    print(f"✓ New submissions: {len(df_new)} samples")
    
    # Remove metadata columns from new submissions
    meta_columns = [
        'predicted_score',
        'submission_date',
        'submission_timestamp',
        'model_used',
        'model_version',
        'model_r2'
    ]
    df_new_clean = df_new.drop(columns=[col for col in meta_columns if col in df_new.columns])
    
    # Ensure same columns
    missing_cols = set(df_original.columns) - set(df_new_clean.columns)
    extra_cols = set(df_new_clean.columns) - set(df_original.columns)
    
    if missing_cols:
        print(f"\n⚠️  Warning: New data missing columns: {missing_cols}")
        for col in missing_cols:
            df_new_clean[col] = None
    
    if extra_cols:
        print(f"\n⚠️  Warning: New data has extra columns: {extra_cols}")
        df_new_clean = df_new_clean[df_original.columns]
    
    # Merge data
    df_merged = pd.concat([df_original, df_new_clean], ignore_index=True)
    
    # Save merged data
    df_merged.to_csv(output_file, index=False)
    
    print(f"\n✅ Merged data saved: {output_file}")
    print(f"   Total samples: {len(df_merged)}")
    print(f"   Increase: +{len(df_new)} samples ({len(df_new)/len(df_original)*100:.1f}% growth)")
    
    print(f"\n{'='*80}")
    print("NEXT STEPS")
    print(f"{'='*80}")
    print(f"\n1. Review the merged file: {output_file}")
    print(f"2. If it looks good, replace original file:")
    print(f"   cp {output_file} {original_file}")
    print(f"3. Retrain models:")
    print(f"   python train_model.py")
    print(f"4. Restart web app to use new model\n")
    
    # Show some statistics
    print(f"{'='*80}")
    print("DATA STATISTICS")
    print(f"{'='*80}")
    print(f"\nStress score distribution:")
    print(df_merged['skor_total'].describe())
    

if __name__ == '__main__':
    merge_data()
