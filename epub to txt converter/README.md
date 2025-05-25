# EPUB to TXT Converter

A Python script to extract all text content from an EPUB (.epub) file and save it as a plain text (.txt) file. This is useful for reading EPUB content in environments that don't support the EPUB format directly, or for text processing tasks.

## Features

* Parses EPUB files to access their content.
* Extracts text primarily from HTML elements within the EPUB.
* Removes `<script>` and `<style>` tags to provide cleaner text output.
* Attempts to preserve basic paragraph separation using newlines.
* Simple command-line interface for specifying input EPUB and output TXT files.
* Provides console feedback during the conversion process, including success or error messages.
* Handles basic file I/O errors and EPUB parsing issues gracefully.

## Requirements

To run this script, you will need:

* Python 3.x
* The following Python libraries:
    * `ebooklib`
    * `BeautifulSoup4`

## Installation

1.  **Ensure Python 3 is installed.** You can download it from [python.org](https://www.python.org/).
2.  **Install the required libraries** using pip:
    ```bash
    pip install ebooklib beautifulsoup4
    ```
3.  **Download the script** (e.g., `epub_converter.py`) and save it to your desired location.

## Usage

Run the script from your terminal using the following command structure:

```bash
python epub_converter.py <input_epub_file_path> <output_txt_file_path>
