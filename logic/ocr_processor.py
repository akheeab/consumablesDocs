# Used for peel test doc
import ocrmypdf
from PyPDF2 import PdfReader

# Used for microbiological test doc
import fitz
import easyocr

import os

def perform_ocr_peel_test(input_pdf_path):

    output_pdf_path = "resources/temp/searchable_" + os.path.basename(input_pdf_path)
    try:
        # Convert the scanned PDF to a searchable PDF
        print("OCR Started")
        print("-"*20)
        ocrmypdf.ocr(input_pdf_path, output_pdf_path, deskew=True)
        print(f"OCR completed. Searchable PDF saved at: {output_pdf_path}")
        print("-"*20)

        # Read the text from the searchable PDF
        reader = PdfReader(output_pdf_path)
        content = "\n".join(page.extract_text() for page in reader.pages)
        # print(content)

        return content
    except Exception as e:
        print(f"Error during Peel Test OCR processing: {e}")

def perform_ocr_microbiologica_test(input_pdf_path):

    try:
        doc = fitz.open(input_pdf_path) # opening PDF file
        reader = easyocr.Reader(['en'], gpu=False, recog_network= 'latin_g2') # Object for OCR engine
        zoom = 4

        # Converting the PDF files pages to images
        mat = fitz.Matrix(zoom, zoom) # zoom x and y axes
        # Count variable is to get the number of pages in the pdf
        count = 0
        content = [] # List to hold OCR output
        for p in doc:
            count += 1
            img_dest = f"resources/temp/image_{count}.png"
            page = doc.load_page(count - 1) # get page
            pix = page.get_pixmap(matrix=mat) # convert page to pixels map
            pix.save(img_dest) # save image
        
            # Performing OCR on the image
            content = content + reader.readtext(f"resources/temp/image_{count}.png", detail=0, text_threshold= 0.4)
        doc.close()

        # with open("output.txt", "w") as file:
        #     file.writelines(str(line) + "\n" for line in content)
        
        return content

    except Exception as e:
        print(f"Error during Microbiological Test OCR processing: {e}")
