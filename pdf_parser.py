import os
import pdfplumber


def extract_text_from_pdf(pdf_path: str, output_dir: str) -> str:
    """
    Extracts text and tables from a native PDF using pdfplumber.
    """
    print(f"Processing document: {pdf_path}...")

    markdown_lines = []

    # Open the PDF with pdfplumber
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            markdown_lines.append(f"## Page {i + 1}\n")

            # Extract tables if they exist
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    # Clean up empty cells (None) and join with pipes to create a basic markdown table
                    clean_row = [str(cell).replace('\n', ' ') if cell else "" for cell in row]
                    markdown_lines.append("| " + " | ".join(clean_row) + " |")
                markdown_lines.append("\n")

            # Extract standard text
            text = page.extract_text()
            if text:
                markdown_lines.append(text + "\n\n")

    markdown_content = "\n".join(markdown_lines)

    # Save the output
    base_name = os.path.basename(pdf_path).replace(".pdf", ".md")
    output_path = os.path.join(output_dir, base_name)
    os.makedirs(output_dir, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    print(f"Success! Fast extraction saved to: {output_path}")
    return markdown_content


if __name__ == "__main__":
    sample_pdf = "data/input_pdfs/sample_report.pdf"
    output_folder = "data/output"

    if os.path.exists(sample_pdf):
        extract_text_from_pdf(sample_pdf, output_folder)
    else:
        print(f"Please drop a PDF into {sample_pdf}")