# Image to PNG Converter GUI

A simple Python script with a graphical user interface (GUI) to convert all supported image files within a selected folder to the PNG format.

## Features

* **User-Friendly GUI**: Easy-to-use interface built with Tkinter.
* **Folder Selection**: Allows users to browse and select an input folder containing images.
* **PNG Conversion**: Converts images from various formats (JPEG, GIF, BMP, TIFF, WEBP) to PNG.
* **Organized Output**: Saves converted PNG files into a new subfolder named `png_converted` within the selected input folder, leaving original files untouched.
* **Status Updates**: Provides real-time feedback during the conversion process.
* **Conversion Summary**: Displays a summary of successful conversions, failures, and unsupported files upon completion.

## Prerequisites

Before running the script, ensure you have the following installed:

* **Python 3**: The script is written for Python 3.x. You can download it from [python.org](https://www.python.org/downloads/).
* **Pillow (PIL Fork)**: The Python Imaging Library is used for image manipulation.

## Installation

1.  **Clone the repository or download the script:**
    If this script is part of a Git repository:
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```
    Otherwise, simply download the `image_converter_gui.py` file.

2.  **Install Pillow:**
    Open your terminal or command prompt and run:
    ```bash
    pip install Pillow
    ```

## How to Use

1.  **Run the Script:**
    Navigate to the directory where you saved the script and run it from your terminal:
    ```bash
    python image_converter_gui.py
    ```
    (Or `python3 image_converter_gui.py` depending on your Python installation).

2.  **Select Folder:**
    * The application window will appear.
    * Click the "**Browse...**" button.
    * A file dialog will open. Navigate to the folder containing the images you want to convert and select it.
    * The path to the selected folder will appear in the text box next to "Image Folder:".

3.  **Convert Images:**
    * Click the "**Convert to PNG ✨**" button.
    * The script will begin processing the images in the selected folder.
    * The status label at the bottom of the window will show the current file being processed or the overall progress.

4.  **View Results:**
    * Once the conversion is complete, a message box will pop up displaying a summary:
        * Number of successfully converted images.
        * Number of failed or corrupted images.
        * Number of unsupported files.
        * Total files processed.
        * The location of the converted files.
    * The converted PNG images will be saved in a new subfolder named `png_converted` inside the folder you originally selected. Your original images will remain unchanged.

## Supported Input Formats

The script attempts to convert the following common image formats:

* JPEG (`.jpg`, `.jpeg`)
* GIF (`.gif`)
* BMP (`.bmp`)
* TIFF (`.tiff`, `.tif`)
* WebP (`.webp`)

Other formats might work if supported by your Pillow installation, but the script explicitly checks for these extensions.

## Notes

* **Original Files**: Your original image files are **not** modified or deleted.
* **Output Location**: All converted PNG files are stored in a subfolder named `png_converted` within the source directory. If this subfolder doesn't exist, it will be created.
* **Error Handling**: The script includes basic error handling for files that Pillow cannot open (e.g., non-image files or corrupted images). Details of such failures might be printed to the console/terminal where you launched the script.

## Troubleshooting

* **`ModuleNotFoundError: No module named 'PIL'` or `'tkinter'`**:
    * If you see `No module named 'PIL'`, ensure you have installed Pillow: `pip install Pillow`.
    * Tkinter is usually included with standard Python installations. If it's missing (common in some Linux minimal installs), you might need to install it separately (e.g., `sudo apt-get install python3-tk` on Debian/Ubuntu).
* **Script doesn't run / No GUI appears**:
    * Ensure you are running the script with Python 3.
    * Check the terminal for any error messages that might indicate what went wrong.

---

Feel free to modify or extend this script to suit your needs!