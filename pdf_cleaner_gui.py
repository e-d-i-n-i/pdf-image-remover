import fitz  # PyMuPDF
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os


def is_valid_font(font_name):
    """Check if font is one of the built-in PDF fonts"""
    valid_fonts = {
        "helvetica", "helvetica-bold", "helvetica-oblique",
        "times-roman", "times-bold", "times-italic",
        "courier", "courier-bold", "courier-oblique",
        "symbol", "zapfdingbats"
    }
    return font_name.lower() in valid_fonts


def process_pdf(input_path, output_path):
    try:
        doc = fitz.open(input_path)
        new_doc = fitz.open()

        total_pages = len(doc)
        progress['maximum'] = total_pages

        for page_num in range(total_pages):
            page = doc.load_page(page_num)
            new_page = new_doc.new_page(width=page.rect.width, height=page.rect.height)

            blocks = page.get_text("dict").get("blocks", [])

            for block in blocks:
                if block["type"] == 0:  # text block
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            # Use default font if unsupported
                            font = span["font"] if is_valid_font(span["font"]) else "helvetica"

                            new_page.insert_text(
                                (span["bbox"][0], span["bbox"][1]),
                                span["text"],
                                fontsize=span["size"],
                                color=(0, 0, 0),  # black
                                fontname=font,
                                rotate=span.get("rotate", 0)
                            )

            # Remove commit_contents() if not supported
            # new_page.commit_contents()

            progress.step(1)
            root.update_idletasks()

        new_doc.save(output_path)
        new_doc.close()
        doc.close()

    except Exception as e:
        raise e


def select_input_file():
    path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if path:
        input_path_var.set(path)
        filename = os.path.splitext(os.path.basename(path))[0]
        output_filename_var.set(f"{filename}_black.pdf")


def select_output_folder():
    path = filedialog.askdirectory()
    if path:
        output_folder_var.set(path)


def start_processing():
    input_path = input_path_var.get()
    output_folder = output_folder_var.get()
    output_filename = output_filename_var.get()

    if not input_path or not output_folder or not output_filename:
        messagebox.showwarning("Missing Info", "Please fill in all fields.")
        return

    output_path = os.path.join(output_folder, output_filename)

    try:
        process_pdf(input_path, output_path)
        messagebox.showinfo("Success", f"File saved at:\n{output_path}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred:\n{str(e)}")


# GUI Setup
root = tk.Tk()
root.title("PDF Text Color Fixer")
root.geometry("600x300")
root.resizable(False, False)

# Input File Selection
input_path_var = tk.StringVar()
ttk.Label(root, text="Input PDF File:").pack(anchor="w", padx=10, pady=(10, 0))
ttk.Entry(root, textvariable=input_path_var, width=50).pack(side="top", padx=10, fill="x")
ttk.Button(root, text="Browse", command=select_input_file).pack(pady=5)

# Output Folder Selection
output_folder_var = tk.StringVar()
ttk.Label(root, text="Output Folder:").pack(anchor="w", padx=10)
ttk.Entry(root, textvariable=output_folder_var, width=50).pack(side="top", padx=10, fill="x")
ttk.Button(root, text="Select Folder", command=select_output_folder).pack(pady=5)

# Output Filename
output_filename_var = tk.StringVar()
ttk.Label(root, text="Output File Name:").pack(anchor="w", padx=10)
ttk.Entry(root, textvariable=output_filename_var, width=50).pack(padx=10, pady=(0, 10))

# Progress Bar
progress = ttk.Progressbar(root, orient="horizontal", mode="determinate")
progress.pack(padx=10, pady=5, fill="x")

# Start Button
ttk.Button(root, text="Process PDF", command=start_processing).pack(pady=10)

# Run App
root.mainloop()