# Image to Text File Creator

A simple Python script with a graphical user interface (GUI) that allows users to select a folder. For each image file found within that folder, the script creates an empty text file (`.txt`) with the same name.

## Features

* **User-Friendly GUI:** Uses Tkinter for an easy-to-use interface.
* **Folder Selection:** Allows users to browse and select a target folder.
* **Image Detection:** Identifies common image file types (e.g., `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`, `.webp`).
* **Text File Creation:** Creates a corresponding `.txt` file for each detected image, matching the original image's base filename.
* **User Feedback:** Provides success or error messages to the user.

## Requirements

* **Python 3:** The script is written for Python 3.
* **Tkinter:** This is usually included with standard Python installations. If not, you may need to install it separately depending on your Python distribution and operating system (e.g., `sudo apt-get install python3-tk` on Debian/Ubuntu).

## How to Use

1.  **Download/Save the Script:**
    * Save the Python code provided as a `.py` file (e.g., `image_to_txt_creator.py`).

2.  **Run the Script:**
    * Open a terminal or command prompt.
    * Navigate to the directory where you saved the script.
    * Execute the script using the command:
        ```bash
        python image_to_txt_creator.py
        ```

3.  **Use the Application:**
    * A small window titled "Image to Text File Creator" will appear.
    * Click the "**Select Folder & Create Files**" button.
    * A folder selection dialog will open. Browse to and select the folder containing your images.
    * Click "Select Folder" (or the equivalent button for your OS).

4.  **Processing:**
    * The script will scan the selected folder for image files.
    * For each image found (e.g., `example.jpg`), it will create an empty text file in the *same folder* (e.g., `example.txt`).
    * Non-image files will be skipped.

5.  **Confirmation:**
    * Once completed, a message box will appear indicating the number of `.txt` files successfully created and the number of non-image files skipped. If no images are found or an error occurs, an appropriate message will be displayed.

## Example

If your selected folder contains:
* `photo1.jpg`
* `image_002.png`
* `document.pdf`

After running the script, the folder will contain:
* `photo1.jpg`
* `photo1.txt` (empty)
* `image_002.png`
* `image_002.txt` (empty)
* `document.pdf` (untouched)

## Notes

* The script currently creates *empty* text files. The content of these text files is not populated from the images.
* The list of recognized image extensions is: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`, `.webp`. This can be modified in the script if needed.
* If a text file with the same name already exists, it will be overwritten without warning.

## License

This project is open-source and can be used freely. Consider attributing if used in a larger project. (You can specify a license like MIT if you wish).