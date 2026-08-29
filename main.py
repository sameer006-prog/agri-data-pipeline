import os
import pandas as pd
from pdf_parser import extract_text_from_pdf
from llm_extractor import extract_structured_data
from data_validator import validate_extracted_data


def run_batch_pipeline(input_dir: str, output_folder: str):
    print("Starting Automated Enterprise Batch Pipeline...")

    if not os.path.exists(input_dir):
        print(f"Error: Input directory '{input_dir}' does not exist.")
        return

    os.makedirs(output_folder, exist_ok=True)

    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]

    if not pdf_files:
        print(f"No PDF files found in {input_dir}.")
        return

    print(f"Found {len(pdf_files)} PDF(s) to process: {pdf_files}")

    master_trial_records = []

    for pdf_file in pdf_files:
        pdf_path = os.path.join(input_dir, pdf_file)
        print(f"\n--- Processing Document: {pdf_file} ---")

        try:
            markdown_text = extract_text_from_pdf(pdf_path, output_folder)

            chunk_size = 4000
            file_trials = []

            for i in range(0, min(len(markdown_text), 100000), chunk_size):
                chunk = markdown_text[i:i + chunk_size]
                try:
                    extracted_data = extract_structured_data(chunk)
                    if extracted_data and extracted_data.trials:
                        file_trials.extend(extracted_data.trials)
                except Exception:
                    continue

            if file_trials:
                print(f"Extracted {len(file_trials)} records from {pdf_file}")
                for trial in file_trials:
                    record = trial.model_dump()
                    record['source_file'] = pdf_file
                    master_trial_records.append(record)
            else:
                print(f"No trial data extracted from {pdf_file}")

        except Exception as e:
            print(f"Error processing {pdf_file}: {e}")

    if master_trial_records:
        # Save raw consolidated master file
        master_df = pd.DataFrame(master_trial_records)
        master_csv_path = os.path.join(output_folder, "master_consolidated_crop_data.csv")
        master_df.to_csv(master_csv_path, index=False, encoding='utf-8')

        print(f"\n========================================")
        print(f"Extraction Phase Complete!")
        print(f"Total raw records: {len(master_df)}")
        print(f"========================================")

        # Automatically run the Quality Gate on the master output
        validate_extracted_data(master_csv_path)

    else:
        print("\nBatch finished, but no records were extracted.")


if __name__ == "__main__":
    input_directory = "data/input_pdfs"
    output_directory = "data/output"

    run_batch_pipeline(input_directory, output_directory)