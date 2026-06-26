import sys
import os
import glob
import data_vectorisation

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <pdf_folder_path>")
        sys.exit(1)

    pdf_dir = sys.argv[1]

    if not os.path.isdir(pdf_dir):
        print(f"Error: '{pdf_dir}' is not a valid directory")
        sys.exit(1)

    pdf_files = sorted(glob.glob(os.path.join(pdf_dir, "*.pdf")))

    if not pdf_files:
        print(f"No PDF files found in '{pdf_dir}'")
        sys.exit(1)

    for pdf_path in pdf_files:
        data_vectorisation.build_and_save_vector_store(pdf_path)

    print(f"Ingestion complete: {len(pdf_files)} file(s) indexed.")

main()
