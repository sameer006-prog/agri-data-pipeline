import os
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

# This loads the key from your hidden .env file
load_dotenv()

# --- 2. Define the Validation Rules (Pydantic Schema) ---
class CropTrialResult(BaseModel):
    variety_name: str = Field(description="The name of the seed variety (e.g., 'Picard', 'DK Expansion').")
    crop_type: str = Field(description="The type of crop (e.g., 'Winterraps', 'Winterweizen').")
    trial_year: Optional[int] = Field(description="The year the trial was conducted.", default=None)
    relative_yield_score: Optional[float] = Field(description="The yield score (usually a number between 1-9).",
                                                  default=None)
    oil_content_percentage: Optional[float] = Field(description="The oil content as a percentage, if available.",
                                                    default=None)
    disease_resistance_rating: Optional[int] = Field(description="Resistance score to common diseases (usually 1-9).",
                                                     default=None)


class ExtractionOutput(BaseModel):
    trials: List[CropTrialResult] = Field(description="A list of extracted crop trial results.")


def extract_structured_data(markdown_text: str) -> ExtractionOutput:
    """
    Sends the parsed markdown to Groq to extract validated, structured data.
    """
    # Clean up weird Windows carriage returns and stray escape characters
    clean_text = markdown_text.replace("\r", " ").replace("\n", " ")

    print("Initializing Groq LLM extraction pipeline...")

    llm = ChatGroq(model="qwen/qwen3.8-27b", temperature=0, max_tokens=4000)
    structured_llm = llm.with_structured_output(ExtractionOutput)

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are an expert agricultural data engineer. Extract crop variety trial results from the provided markdown document, which originated from a German agricultural PDF (Bundessortenamt). Extract the variety name, crop type, trial year, yield score, oil content, and disease resistance. If a value is missing, return null."),
        ("human", "Here is the markdown document:\n\n{document}")
    ])

    chain = prompt | structured_llm

    print("Analyzing document and extracting entities...")

    # Pass the sanitized text string
    result = chain.invoke({"document": clean_text})

    return result


if __name__ == "__main__":
    sample_md = "data/output/sample_report.md"

    if os.path.exists(sample_md):
        with open(sample_md, "r", encoding="utf-8") as f:
            md_content = f.read()

        # Process the first 5000 characters for the test
        short_md = md_content[:5000]

        extracted_data = extract_structured_data(short_md)

        print("\n🎉 Extraction Successful! Here is the clean, validated data:")
        for trial in extracted_data.trials:
            print(trial.model_dump())
    else:
        print(f"Could not find {sample_md}. Make sure you run pdf_parser.py first!")