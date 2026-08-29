# Agricultural PDF Data Pipeline: Unstructured to ERP-Ready

## Overview
In enterprise logistics and data migration projects—such as transitioning to SAP S/4HANA—unstructured vendor documents often create massive bottlenecks. This project is an automated, AI-driven data extraction pipeline that ingests dense, unstructured German agricultural reports (e.g., Bundessortenamt PDFs), parses the text, and extracts strict, structured records using a local LLM.

Instead of manual data entry, the pipeline processes documents in batch and automatically passes the extracted data through a Pandas-based quality gate, ensuring only validated, perfectly formatted data reaches the target database.

## Architecture & Tech Stack
*   **Language:** Python
*   **LLM Orchestration:** Groq API (`qwen/qwen3.8-27b`) for high-speed, local-equivalent extraction.
*   **Data Validation:** Pandas for strict boundary enforcement and automated sorting.
*   **Schema Enforcement:** Pydantic to guarantee consistent data structures.
*   **Document Parsing:** PyMuPDF / Markdown conversion.

## Key Features
*   **Automated Batch Processing:** Drop any number of PDF reports into the input directory; the pipeline will iterate through all of them, extract the data via chunking, and consolidate the results into a single master dataset.
*   **LLM Entity Extraction:** Uses a customized AI prompt to identify and pull specific entities (variety name, crop type, trial year, yield score, disease resistance, oil content) from dense tables and paragraphs.
*   **Automated Quality Gate:** Extracted records are instantly evaluated against business logic rules using Pandas. Validated records are routed to `validated_ready_for_erp.csv`, while anomalies (e.g., missing identifiers or out-of-bounds yield scores) are flagged and isolated for human review.
*   **Error Resiliency:** Built-in exception handling safely skips malformed text chunks during LLM generation without crashing the pipeline, preserving all valid data.

## Directory Structure
```text
agri_data_pipeline/
├── data/
│   ├── input_pdfs/          # Place raw vendor PDFs here
│   └── output/              # Generated markdown, raw CSVs, and validated CSVs
├── .env                     # API keys (Groq)
├── main.py                  # Batch processing orchestration
├── pdf_parser.py            # Converts PDFs to clean Markdown
├── llm_extractor.py         # Handles Groq LLM prompting and Pydantic schemas
├── data_validator.py        # Pandas-based quality gate
└── requirements.txt         # Project dependencies