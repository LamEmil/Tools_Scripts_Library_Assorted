import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import os

def select_folder():
    """Opens a dialog to select a folder and populates the folder_path entry."""
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        folder_path.set(folder_selected)
        status_text.set(f"Selected folder: {folder_selected}")
    else:
        status_text.set("No folder selected.")

def convert_images_to_png():
    """Converts all supported images in the selected folder to PNG format."""
    input_folder = folder_path.get()
    if not input_folder:
        messagebox.showerror("Error", "Please select a folder first.")
        return

    # Create a subfolder for PNGs if it doesn't exist
    output_folder = os.path.join(input_folder, "png_converted")
    os.makedirs(output_folder, exist_ok=True)

    converted_count = 0
    failed_count = 0
    unsupported_count = 0
    original_files = []

    status_text.set("Starting conversion...")
    root.update_idletasks() # Update UI

    for filename in os.listdir(input_folder):
        if os.path.isfile(os.path.join(input_folder, filename)): # Ensure it's a file
            original_files.append(filename)
            try:
                img_path = os.path.join(input_folder, filename)
                # Attempt to open the image to check if it's a valid image format
                # and not already a PNG (to avoid re-saving PNGs unnecessarily unless intended)
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp')):
                    img = Image.open(img_path)
                    # Create new filename with .png extension
                    base, ext = os.path.splitext(filename)
                    new_filename = f"{base}.png"
                    save_path = os.path.join(output_folder, new_filename)

                    # Convert and save as PNG
                    img.save(save_path, "PNG")
                    converted_count += 1
                    status_text.set(f"Converting: {filename} -> {new_filename}")
                    root.update_idletasks() # Update UI
                elif not filename.lower().endswith(('.png')): # Avoid counting already PNG files as unsupported if we are skipping them
                    unsupported_count += 1

            except IOError:
                # This exception will catch files that PIL cannot open (e.g., non-image files)
                # or corrupted images.
                failed_count += 1
                print(f"Could not convert {filename}. It might be corrupted or not a supported image format.")
            except Exception as e:
                failed_count += 1
                print(f"An unexpected error occurred with {filename}: {e}")


    summary_message = f"Conversion Complete!\n\n"
    summary_message += f"Successfully converted: {converted_count}\n"
    summary_message += f"Failed or corrupted: {failed_count}\n"
    summary_message += f"Unsupported (or already PNG if skipping): {unsupported_count}\n"
    summary_message += f"Total files processed: {len(original_files)}\n\n"
    summary_message += f"Converted PNG files are saved in:\n{output_folder}"

    status_text.set(f"Converted: {converted_count}, Failed: {failed_count}, Unsupported: {unsupported_count}")
    messagebox.showinfo("Conversion Summary", summary_message)

# --- GUI Setup ---
root = tk.Tk()
root.title("Image to PNG Converter 🖼️➡️📄")
root.geometry("550x250") # Adjusted size for better layout

folder_path = tk.StringVar()
status_text = tk.StringVar()
status_text.set("Select a folder to start.")

# Folder Selection Frame
frame_folder = tk.Frame(root, pady=10)
frame_folder.pack(fill=tk.X)

lbl_folder = tk.Label(frame_folder, text="Image Folder:")
lbl_folder.pack(side=tk.LEFT, padx=5)

entry_folder = tk.Entry(frame_folder, textvariable=folder_path, width=50, state='readonly')
entry_folder.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

btn_browse = tk.Button(frame_folder, text="Browse...", command=select_folder)
btn_browse.pack(side=tk.LEFT, padx=5)

# Action Button Frame
frame_action = tk.Frame(root, pady=10)
frame_action.pack()

btn_convert = tk.Button(frame_action, text="Convert to PNG ✨", command=convert_images_to_png, font=("Arial", 12, "bold"), bg="#4CAF50", fg="white")
btn_convert.pack(pady=10, padx=20, ipadx=10, ipady=5)

# Status Label Frame
frame_status = tk.Frame(root, pady=10)
frame_status.pack(fill=tk.X)

lbl_status = tk.Label(frame_status, textvariable=status_text, wraplength=500) # Wraplength for longer messages
lbl_status.pack(pady=5)

# Center the window on the screen
root.eval('tk::PlaceWindow . center')

root.mainloop()
