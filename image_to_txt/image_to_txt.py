import tkinter as tk
from tkinter import filedialog, messagebox
import os

def create_text_files_for_images():
    """
    Allows the user to select a folder and creates an empty .txt file
    for each image file found in that folder.
    """
    folder_path = filedialog.askdirectory(title="Select Folder Containing Images")

    if not folder_path:
        messagebox.showinfo("Info", "No folder selected.")
        return

    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp')
    files_created_count = 0
    files_skipped_count = 0

    try:
        for filename in os.listdir(folder_path):
            # Check if the file has a common image extension
            if filename.lower().endswith(image_extensions):
                # Create the full path to the image file
                image_file_path = os.path.join(folder_path, filename)
                
                # Create the corresponding text file name
                base_filename, _ = os.path.splitext(filename)
                text_filename = base_filename + ".txt"
                text_file_path = os.path.join(folder_path, text_filename)

                # Create the empty text file
                with open(text_file_path, 'w') as f:
                    pass  # Just create an empty file
                files_created_count += 1
            else:
                files_skipped_count += 1
        
        if files_created_count > 0:
            messagebox.showinfo("Success", 
                                f"Successfully created {files_created_count} .txt file(s).\n"
                                f"{files_skipped_count} non-image file(s) were skipped.")
        elif files_skipped_count > 0 and files_created_count == 0:
             messagebox.showinfo("Info", "No image files found to process. \n"
                                 f"{files_skipped_count} non-image file(s) were skipped.")
        else:
            messagebox.showinfo("Info", "No files found in the selected folder.")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# --- Set up the GUI ---
root = tk.Tk()
root.title("Image to Text File Creator")
root.geometry("350x150") # Set a more appropriate window size

# Frame for better organization
frame = tk.Frame(root, padx=20, pady=20)
frame.pack(expand=True)

# Label
label = tk.Label(frame, text="Select a folder to create .txt files for each image:")
label.pack(pady=(0, 10)) # Add some padding below the label

# Button
select_button = tk.Button(frame, text="Select Folder & Create Files", command=create_text_files_for_images, width=25, height=2)
select_button.pack()

# Run the Tkinter event loop
root.mainloop()