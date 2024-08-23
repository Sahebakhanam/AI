import streamlit as st
import fitz  # PyMuPDFcls

import requests
import cohere
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import os
from bs4 import BeautifulSoup

def extract_scanned_text(pdf_path):
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    output_image_folder = 'images'

    # Ensure the output directory exists
    if not os.path.exists(output_image_folder):
        os.makedirs(output_image_folder)

    # Convert PDF pages to images
    images = convert_from_path(pdf_path, 300, output_folder=output_image_folder, poppler_path=r'poppler-23.11.0\Library\bin')

    final_text = ''
    # Iterate through the images and apply OCR
    for i, image in enumerate(images):
        image_path = os.path.join(output_image_folder, f'page_{i+1}.jpg')
        image.save(image_path, 'JPEG')
        
        # Perform OCR on the image
        text = pytesseract.image_to_string(Image.open(image_path))
        final_text = final_text + '\n' + text
    return final_text

def fetch_website_content(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        # Extract all text from the website
        text = soup.get_text(separator='\n')
        return text
    except Exception as e:
        return f"Error fetching website content: {str(e)}"

# Streamlit app
def main():
    st.title("Scanned PDF Text Extractor")

    # File uploader
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    pdf_text = ""
    if uploaded_file is not None:
        with st.spinner("Extracting text from PDF..."):
            # Save the uploaded file temporarily
            with open("uploaded_file.pdf", "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Extract text from the PDF
            pdf_text = extract_scanned_text("uploaded_file.pdf")
            st.success("Text extracted from PDF")
            st.text_area("Extracted Text", pdf_text, height=300)

    # Website link input
    website_link = st.text_input("Enter a website link")

    # Input for additional text
    user_input = st.text_input("Enter your prompt")

    # Combine extracted text, website content, and user input
    combined_text = pdf_text + "\n" + website_link + "\n" + user_input

    if st.button("Call API"):
        co = cohere.Client("your api key")
        response = co.chat(
            message=combined_text
        )

        st.write("Response:", response.text)

if __name__ == "__main__":
    main()
