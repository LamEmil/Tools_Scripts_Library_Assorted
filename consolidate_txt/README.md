# Text File Consolidator

A simple Python script with a graphical user interface (GUI) to consolidate text from multiple `.txt` files within a selected folder into a single `output.txt` file. Each input file's content is placed on a new line in the output file.

## Features ✨

* **User-Friendly GUI**: Simple interface built with Tkinter for ease of use.
* **Folder Selection**: Allows users to browse and select the folder containing their `.txt` files.
* **Automatic `.txt` File Detection**: Scans the selected folder for all files ending with the `.txt` extension.
* **Consolidated Output**: Reads the content of each `.txt` file and writes it to a new line in a single `output.txt` file.
* **Specific Output Location**: The `output.txt` file is saved in the parent directory of the folder selected by the user.
* **Ordered Processing**: `.txt` files are processed in alphabetical order (based on filename).
* **Error Handling**: Basic error messages for common issues like not selecting a folder or file read errors.
* **Avoids Self-Processing**: The script will ignore any existing `output.txt` file in the selected folder during processing.

## Prerequisites 🛠️

* **Python 3.x**: The script is written for Python 3.
* **Tkinter**: This is a standard Python library for creating GUIs and is usually included with Python installations. If it's missing (uncommon), you may need to install it separately (e.g., `sudo apt-get install python3-tk` on Debian/Ubuntu, or it might be part of a `python3-devel` or similar package on other systems).

## How to Use 📝

1.  **Save the Script**:
    * Download or save the Python script code as a `.py` file (e.g., `consolidate_txt.py`).

2.  **Run the Script**:
    * Open a terminal or command prompt.
    * Navigate to the directory where you saved the script.
    * Execute the script using the command:
        ```bash
        python consolidate_txt.py
        ```
        or
        ```bash
        python3 consolidate_txt.py
        ```
        (depending on your Python installation).

3.  **Using the Interface**:
    * **Select Folder**:
        * Click the "**Browse...**" button.
        * A dialog will open. Navigate to and select the folder that contains the `.txt` files you want to consolidate.
        * The path of the selected folder will appear in the text field next to the "Browse..." button.
    * **Run Consolidation**:
        * Click the "**Run**" button.
        * The script will process the files.
    * **Confirmation**:
        * Upon successful completion, a message box will appear indicating that `output.txt` has been created and its location.
        * If no `.txt` files are found or an error occurs, an appropriate message will be displayed.

## Output 📄

* A file named `output.txt` will be created (or overwritten if it already exists).
* **Location**: This file will be saved in the **parent directory** of the folder you selected for processing.
    * *Example*: If you select `C:\Users\YourName\Documents\MyTextFiles` as the input folder, the `output.txt` will be saved in `C:\Users\YourName\Documents\`.
* **Format**:
    * The entire text content from the first processed `.txt` file will be on the first line of `output.txt`.
    * The entire text content from the second processed `.txt` file will be on the second line of `output.txt`, and so on.
    * Any newline characters (`\n`) within the original `.txt` files are replaced by a space to ensure each original file's content remains on a single line in `output.txt`.

## Important Notes 📌

* **File Order**: The script reads `.txt` files from the selected folder in alphabetical order (based on their filenames). If you require a specific order that is not alphabetical, you will need to rename your files accordingly (e.g., `01_report.txt`, `02_data.txt`, `03_summary.txt`).
* **Overwriting `output.txt`**: If an `output.txt` file already exists in the target output location (the parent directory of the selected folder), it will be **overwritten** without warning each time the script is run.
* **Encoding**: The script attempts to read and write files using `UTF-8` encoding. If your files use a different encoding, you might encounter errors or garbled text.

---

Feel free to modify or extend this script as needed!
