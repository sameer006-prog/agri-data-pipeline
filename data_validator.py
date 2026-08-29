import pandas as pd
import os


def validate_extracted_data(csv_path: str):
    print(f"🔍 Initializing data quality checks on {csv_path}...")

    if not os.path.exists(csv_path):
        print(f"Error: Could not find {csv_path}")
        return

    # Load the extracted AI data
    df = pd.read_csv(csv_path)

    # Initialize our quality tracking columns
    df['validation_status'] = 'PASS'
    df['error_reason'] = ''

    # --- Rule 1: Yield Score Boundaries ---
    # Agricultural yield scores are typically 1 to 9. Anything else is an AI hallucination.
    if 'relative_yield_score' in df.columns:
        invalid_yield = (df['relative_yield_score'] < 1) | (df['relative_yield_score'] > 9)
        df.loc[invalid_yield, 'validation_status'] = 'FAIL'
        df.loc[invalid_yield, 'error_reason'] += 'Yield score out of bounds (must be 1-9). '

    # --- Rule 2: Missing Critical Identifiers ---
    # We cannot migrate a record if we don't know the variety name or crop type.
    missing_critical = df['variety_name'].isna() | df['crop_type'].isna()
    df.loc[missing_critical, 'validation_status'] = 'FAIL'
    df.loc[missing_critical, 'error_reason'] += 'Missing variety name or crop type. '

    # Split the dataset based on the quality checks
    passed_df = df[df['validation_status'] == 'PASS'].copy()
    failed_df = df[df['validation_status'] == 'FAIL'].copy()

    # Define output paths
    output_dir = os.path.dirname(csv_path)
    clean_path = os.path.join(output_dir, "validated_ready_for_erp.csv")
    review_path = os.path.join(output_dir, "failed_human_review.csv")

    # Export the split data
    passed_df.drop(columns=['error_reason']).to_csv(clean_path, index=False, encoding='utf-8')
    failed_df.to_csv(review_path, index=False, encoding='utf-8')

    print(f"\n Quality Gate Complete!")
    print(f"🟢 Clean records saved to: validated_ready_for_erp.csv ({len(passed_df)} rows)")
    if len(failed_df) > 0:
        print(f" Flagged records saved to: failed_human_review.csv ({len(failed_df)} rows)")
    else:
        print("  Zero errors found! All data passed validation.")


if __name__ == "__main__":
    # Point this at the CSV your pipeline just generated
    target_csv = "data/output/final_crop_data.csv"
    validate_extracted_data(target_csv)