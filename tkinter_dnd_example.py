#!/usr/bin/env python3
import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD

def drop(event):
    # This function will be called when files are dropped onto the label
    files = event.data
    # Convert the string of file paths to a list (handles multiple files)
    file_paths = files.split() if isinstance(files, str) else files
    # Update the label to show the dropped file paths
    drop_label.config(text=f"Dropped: {file_paths[0]}\n" + 
                     (f"and {len(file_paths)-1} more files" if len(file_paths) > 1 else ""))

# Initialize the TkinterDnD window
root = TkinterDnD.Tk()
root.title("TkinterDnD2 Example")
root.geometry("400x200")

# Create a frame to hold our content
frame = tk.Frame(root)
frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

# Create a label with instructions
title_label = tk.Label(
    frame, 
    text="TkinterDnD2 Successfully Imported!", 
    font=("Helvetica", 14, "bold")
)
title_label.pack(pady=(0, 10))

# Create a label that can receive dropped files
drop_label = tk.Label(
    frame,
    text="Drag and drop files here",
    bg="#e0e0e0",
    font=("Helvetica", 12),
    relief="ridge",
    height=4
)
drop_label.pack(fill=tk.BOTH, expand=True)

# Register the label as a drop target
drop_label.drop_target_register(DND_FILES)
drop_label.dnd_bind('<<Drop>>', drop)

# Run the application
if __name__ == "__main__":
    root.mainloop()

