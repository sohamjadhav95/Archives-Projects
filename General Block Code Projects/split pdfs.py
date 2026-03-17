from pypdf import PdfReader, PdfWriter
import os

# ==============================
# CONFIGURATION
# ==============================
input_file = r"C:\Users\soham\Downloads\Current Affairs_rotated.pdf"
output_folder = r"C:\Users\soham\Downloads\Split_Output"
pages_per_split = 5
# ==============================

os.makedirs(output_folder, exist_ok=True)

reader = PdfReader(input_file)
total_pages = len(reader.pages)

for start in range(0, total_pages, pages_per_split):
    end = min(start + pages_per_split, total_pages)

    writer = PdfWriter()
    for page_num in range(start, end):
        writer.add_page(reader.pages[page_num])

    # 1-based page numbers for the filename
    chunk_start = start + 1
    chunk_end = end

    output_filename = f"{chunk_start}_{chunk_end}.pdf"
    output_path = os.path.join(output_folder, output_filename)

    with open(output_path, "wb") as f:
        writer.write(f)

    print(f"Created: {output_filename}")

print("Splitting completed successfully.")