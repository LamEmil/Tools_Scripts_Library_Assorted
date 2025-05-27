import os
import base64
import json
import requests
from tkinter import filedialog
from tkinter import Tk

# --- Configuration ---
OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llava:latest"
SYSTEM_PROMPT = "describe what is in this image in 1 paragraph, only respond with the description and nothing else."

def encode_image_to_base64(image_path):
    """Encodes an image file to a base64 string."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"Error: Image file not found at {image_path}")
        return None
    except Exception as e:
        print(f"Error encoding image {image_path}: {e}")
        return None

def get_image_description_from_ollama(image_base64):
    """
    Sends the image and prompt to the Ollama API and returns the description.
    """
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": MODEL_NAME,
        "prompt": "Describe this image.", # A simple prompt, as the main instruction is in the system prompt
        "system": SYSTEM_PROMPT, # [cite: 8]
        "images": [image_base64], # [cite: 8]
        "stream": False # [cite: 9]
    }

    try:
        print(f"Sending request to Ollama for model: {MODEL_NAME}...")
        response = requests.post(OLLAMA_API_URL, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        
        response_data = response.json()
        
        # Debug: Print the full response to understand its structure
        # print("Full API Response:", json.dumps(response_data, indent=2))

        # Extract the text response
        # Based on the Ollama API documentation for /api/generate:
        # The response content is in the 'response' field when stream is false. [cite: 15, 17]
        if "response" in response_data:
            return response_data["response"].strip()
        else:
            print("Error: 'response' key not found in API response.")
            print("API Response Data:", response_data)
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Ollama API: {e}")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON response from Ollama: {response.text}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def save_description_to_file(description, output_path):
    """Saves the description to a text file."""
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(description)
        print(f"Description saved to {output_path}")
    except Exception as e:
        print(f"Error saving description to {output_path}: {e}")

def process_images_in_folder(folder_path):
    """
    Processes all PNG images in the selected folder.
    """
    if not folder_path:
        print("No folder selected. Exiting.")
        return

    print(f"Processing images in folder: {folder_path}")
    processed_files = 0
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".png"):
            image_path = os.path.join(folder_path, filename)
            print(f"\nProcessing image: {image_path}")

            base64_image = encode_image_to_base64(image_path)
            if not base64_image:
                continue

            description = get_image_description_from_ollama(base64_image)
            if description:
                txt_filename = os.path.splitext(filename)[0] + ".txt"
                output_txt_path = os.path.join(folder_path, txt_filename)
                save_description_to_file(description, output_txt_path)
                processed_files += 1
            else:
                print(f"Failed to get description for {filename}")
    
    if processed_files == 0:
        print("No PNG images were found or processed in the selected folder.")
    else:
        print(f"\nFinished processing. {processed_files} PNG images were processed.")


if __name__ == "__main__":
    # --- User Interface for Folder Selection ---
    root = Tk()
    root.withdraw()  # Hide the main Tkinter window
    
    print("Please select the folder containing your PNG images.")
    selected_folder = filedialog.askdirectory(title="Select Folder with PNG Images")
    
    if selected_folder:
        process_images_in_folder(selected_folder)
    else:
        print("No folder was selected. Exiting.")
    
    root.destroy() # Clean up Tkinter root window
