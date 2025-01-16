import os
from pathlib import Path
from PyPDF2 import PdfReader

def extract_text_from_pdfs(input_dir, output_dir):
    """
    Extract text from PDF files in a directory (including subdirectories)
    and save the extracted text to an output directory while preserving
    the subdirectory structure.

    Parameters:
    - input_dir (str): Path to the main input directory containing PDF files.
    - output_dir (str): Path to the main output directory to save extracted text.
    """
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)

    # Walk through all files in the input directory
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith(".pdf"):
                pdf_path = Path(root) / file  # Full path to the PDF file
                relative_path = pdf_path.relative_to(input_dir)  # Relative path from input_dir
                text_output_path = output_dir / relative_path.with_suffix(".txt")  # Text file path
                
                # Create the output directory structure
                text_output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Extract text from the PDF
                try:
                    reader = PdfReader(pdf_path)
                    extracted_text = ""
                    for page in reader.pages:
                        extracted_text += page.extract_text()
                    
                    # Save the extracted text to a file
                    with open(text_output_path, "w", encoding="utf-8") as f:
                        f.write(extracted_text)
                    
                    print(f"Processed: {pdf_path} -> {text_output_path}")
                except Exception as e:
                    print(f"Failed to process {pdf_path}: {e}")

input_directory = "/Users/akitaka/Dropbox/plastics_text_analysis/downloads"
output_directory = "/Users/akitaka/Dropbox/research_seed/INC-Plastic-Polution/tmp_data/text"
extract_text_from_pdfs(input_directory, output_directory)
