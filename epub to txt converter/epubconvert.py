# EPUB to TXT Converter
# This script extracts all text content from an EPUB file and saves it to a TXT file.
#
# Required libraries:
# - ebooklib: For reading and parsing EPUB files.
# - BeautifulSoup4: For parsing HTML content within the EPUB.
#
# You can install these libraries using pip:
# pip install ebooklib beautifulsoup4
#
# How to run the script:
# python your_script_name.py <input_epub_file_path> <output_txt_file_path>
#
# Example:
# python epub_converter.py "My Book.epub" "My Book.txt"

import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import argparse
import os # Used for path validation

def extract_text_from_html(html_content):
    """
    Extracts plain text from HTML content using BeautifulSoup.

    Args:
        html_content (bytes): The HTML content in bytes.

    Returns:
        str: The extracted plain text.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove script and style elements
    for script_or_style in soup(["script", "style"]):
        script_or_style.decompose() # Remove the tag and its content

    # Get text, ensuring paragraphs are separated by newlines
    # and stripping leading/trailing whitespace from each line.
    text = soup.get_text(separator='\n', strip=True)
    
    # Further clean up: remove multiple consecutive newlines
    lines = [line for line in text.splitlines() if line.strip()]
    return "\n".join(lines)

def epub_to_txt(epub_path, txt_path):
    """
    Reads an EPUB file, extracts all text content from its HTML items,
    and writes the text to a TXT file.

    Args:
        epub_path (str): The path to the input EPUB file.
        txt_path (str): The path where the output TXT file will be saved.

    Returns:
        bool: True if conversion was successful, False otherwise.
    """
    if not os.path.exists(epub_path):
        print(f"Error: EPUB file not found at {epub_path}")
        return False

    try:
        # Read the EPUB file
        book = epub.read_epub(epub_path)
        print(f"Successfully opened EPUB: {os.path.basename(epub_path)}")
    except Exception as e:
        print(f"Error reading EPUB file '{epub_path}': {e}")
        return False

    all_text_content = []

    # Iterate through all items in the EPUB file
    # We are interested in items of type 'document' which are typically HTML files
    print("Extracting text from EPUB items...")
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            # ITEM_DOCUMENT usually means HTML content
            try:
                html_content = item.get_content()
                # Decode bytes to string (EPUBs usually use UTF-8)
                # decoded_html = html_content.decode('utf-8', errors='ignore')
                text = extract_text_from_html(html_content)
                if text: # Add text only if something was extracted
                    all_text_content.append(text)
                    print(f"  Extracted text from: {item.get_name()} (ID: {item.id})")
            except Exception as e:
                print(f"  Warning: Could not process item {item.get_name()} (ID: {item.id}): {e}")
    
    if not all_text_content:
        print("Warning: No text content found in the EPUB file.")
        # Still create an empty txt file as requested by the function's contract
        # or you could return False here if an empty file is not desired.

    # Join all extracted text parts with a double newline for separation
    full_text = "\n\n".join(all_text_content)

    try:
        # Write the extracted text to the output TXT file
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(full_text)
        print(f"Successfully converted EPUB to TXT: {txt_path}")
        return True
    except IOError as e:
        print(f"Error writing to TXT file '{txt_path}': {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred during file writing: {e}")
        return False

if __name__ == "__main__":
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(
        description="Convert an EPUB file to a TXT file by extracting its text content.",
        formatter_class=argparse.RawTextHelpFormatter # To allow newlines in help text
    )
    parser.add_argument(
        "epub_file", 
        help="Path to the input EPUB file (e.g., 'book.epub')"
    )
    parser.add_argument(
        "txt_file", 
        help="Path for the output TXT file (e.g., 'book.txt')"
    )

    args = parser.parse_args()

    print("Starting EPUB to TXT conversion...")
    # Call the main conversion function
    success = epub_to_txt(args.epub_file, args.txt_file)

    if success:
        print("Conversion completed successfully.")
    else:
        print("Conversion failed. Please check the error messages above.")
