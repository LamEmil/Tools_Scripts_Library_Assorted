# Ollama Image Describer

This Python script uses the Ollama API with a multimodal model (specifically `llava:latest` by default) to generate descriptions for PNG images in a user-selected folder. For each image, it saves the generated description into a new text file with the same name as the image.

## Features

* Prompts the user to select a folder containing PNG images.
* Iterates through each PNG image in the selected folder.
* Encodes images to base64 for API transmission.
* Sends images one by one to a running Ollama instance.
* Uses a specific system prompt to instruct the model to describe the image in a single paragraph.
* Saves the textual description from the API response into a `.txt` file.
* The output `.txt` file is stored in the same directory as the original image and shares its name (e.g., `photo.png` -> `photo.txt`).

## Prerequisites

1.  **Python 3.x:** Ensure you have Python 3 installed.
2.  **Ollama:** You need Ollama running on your system. You can download it from [ollama.ai](https://ollama.com/).
3.  **Llava Model:** The script is configured to use the `llava:latest` model. You need to have this model pulled in your Ollama instance. If not, run:
    ```bash
    ollama pull llava:latest
    ```
4.  **Requests Library:** The script uses the `requests` library to make HTTP calls to the Ollama API. Install it via pip:
    ```bash
    pip install requests
    ```
5.  **Tkinter:** This script uses `tkinter` for the folder selection dialog, which is usually included with standard Python installations. If it's missing (common in some minimal Linux installs), you might need to install it separately (e.g., `sudo apt-get install python3-tk` on Debian/Ubuntu).

## Configuration

The script has a few configurable constants at the top:

* `OLLAMA_API_URL`: The URL for your Ollama API's generation endpoint. Defaults to `http://localhost:11434/api/generate`. [cite: 5, 14]
* `MODEL_NAME`: The Ollama model to use for descriptions. Defaults to `llava:latest`. [cite: 8, 35]
* `SYSTEM_PROMPT`: The system instruction given to the model for generating the description. Defaults to `"describe what is in this image in 1 paragraph, only respond with the description and nothing else."`.

You can modify these directly in the script if needed.

## How to Use

1.  **Save the Script:** Save the Python code provided in the previous response to a file (e.g., `ollama_image_describer.py`).
2.  **Ensure Ollama is Running:** Start your Ollama application and confirm that the `llava:latest` (or your configured model) is available.
3.  **Run from Terminal:** Open your terminal or command prompt, navigate to the directory where you saved the script, and run:
    ```bash
    python ollama_image_describer.py
    ```
4.  **Select Folder:** A file dialog will appear. Use it to navigate to and select the folder that contains the PNG images you want to process.
5.  **Processing:** The script will begin processing the images. You'll see console output indicating which image is being processed and the status of API calls and file saving.
6.  **Check Output:** Once completed, look in the selected folder. For each PNG image, there should be a corresponding `.txt` file containing the image's description.

## API Interaction Details

The script sends a `POST` request to the `/api/generate` endpoint of the Ollama API. [cite: 5] Key parameters used in the payload include:
* `model`: The name of the model to use (e.g., `llava:latest`). [cite: 8]
* `prompt`: A general prompt for the task (e.g., "Describe this image.").
* `system`: A more specific instruction to the model about the desired output format and content. [cite: 8]
* `images`: A list containing the base64-encoded image data. [cite: 8]
* `stream`: Set to `false` to receive the full response in a single JSON object rather than a stream. [cite: 9, 17]

The script expects a JSON response, from which it extracts the `response` field containing the textual description. [cite: 15]

## Error Handling

* The script includes basic error handling for:
    * Image file not found or encoding errors.
    * Network issues or errors connecting to the Ollama API.
    * Errors in the API response (e.g., missing 'response' key, JSON decoding errors).
    * File saving errors.
* Error messages will be printed to the console.

## Example Flow

1.  You run `python ollama_image_describer.py`.
2.  You select a folder `/path/to/your/images/`.
3.  The folder contains `cat.png` and `dog.png`.
4.  The script processes `cat.png`:
    * Encodes `cat.png` to base64.
    * Sends it to Ollama with the prompt.
    * Receives a description like "A fluffy cat is sitting on a windowsill."
    * Saves this description to `/path/to/your/images/cat.txt`.
5.  The script processes `dog.png` similarly, creating `dog.txt`.

---

Feel free to modify or extend this script to suit your needs!
