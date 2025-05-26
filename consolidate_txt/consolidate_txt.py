import tkinter as tk
from tkinter import filedialog, messagebox
import os

def process_files():
    """
    Processes .txt files in the selected folder and writes their content
    to an output.txt file, each on a new line.
    """
    folder_selected = folder_path_var.get()
    if not folder_selected:
        messagebox.showerror("Error", "Please select a folder first.")
        return

    txt_files = []
    for filename in sorted(os.listdir(folder_selected)): # Sort to ensure consistent order
        if filename.endswith(".txt") and filename.lower() != "output.txt":
            txt_files.append(os.path.join(folder_selected, filename))

    if not txt_files:
        messagebox.showinfo("No Files", "No .txt files found in the selected folder.")
        return

    # Determine the path for output.txt (parent directory of the selected folder)
    parent_folder = os.path.dirname(folder_selected)
    output_file_path = os.path.join(parent_folder, "output.txt")

    try:
        with open(output_file_path, 'w', encoding='utf-8') as outfile:
            for i, filepath in enumerate(txt_files):
                try:
                    with open(filepath, 'r', encoding='utf-8') as infile:
                        content = infile.read().replace('\n', ' ') # Replace newlines within a file with spaces
                        outfile.write(content)
                        if i < len(txt_files) - 1: # Add newline for next file's content
                            outfile.write('\n')
                except Exception as e:
                    messagebox.showwarning("File Read Error", f"Could not read file: {filepath}\nError: {e}")
        
        messagebox.showinfo("Success", f"Successfully created output.txt at:\n{output_file_path}")
        folder_path_var.set("") # Clear the selected folder path

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while writing output.txt:\n{e}")

def select_folder():
    """Opens a dialog to select a folder and updates the entry field."""
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        folder_path_var.set(folder_selected)

# --- GUI Setup ---
root = tk.Tk()
root.title("Text File Consolidator")

# Folder selection
folder_path_var = tk.StringVar()

tk.Label(root, text="Select Folder:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
folder_entry = tk.Entry(root, textvariable=folder_path_var, width=50, state="readonly")
folder_entry.grid(row=0, column=1, padx=10, pady=10)
select_button = tk.Button(root, text="Browse...", command=select_folder)
select_button.grid(row=0, column=2, padx=10, pady=10)

# Run button
run_button = tk.Button(root, text="Run", command=process_files, width=15)
run_button.grid(row=1, column=0, columnspan=3, pady=20)

# Center the window
root.eval('tk::PlaceWindow . center')

root.mainloop()
