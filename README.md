# 🌟 Document Summarizer Web App 🔗 Live Demo

Check it here: [[https://infosummary.onrender.com](https://infosummary.onrender.com/)]🚀

💡 Overview

A powerful and user-friendly web application that allows users to upload PDFs or images and generate concise summaries. It also highlights key phrases and provides improvement suggestions, making it perfect for students, professionals, and content creators.

✨ Features

📄 **Multi-format Support** – Upload PDFs or image files (PNG, JPG, JPEG, GIF, BMP, WebP).  
📝 **Text Extraction** – Extract text from PDFs using PyMuPDF and from images using Tesseract OCR.  
⚡ **Summarization** – Generate short, medium, or long summaries using LexRank summarizer.  
🔑 **Keyword Highlighting** – Highlights top keywords in both original text and summary.  
💡 **Suggestions** – Get text improvement suggestions for clarity and readability.  
📊 **Statistics** – View word count, character count, and summary percentage.  

🛠️ Tech Stack

- **Python Flask** – Web framework  
- **PyMuPDF / PyPDF2** – PDF text extraction  
- **OpenCV / PIL** – Image preprocessing  
- **Tesseract OCR** – Text extraction from images  
- **Sumy & Rake-NLTK** – Text summarization & keyword extraction  
- **Gunicorn** – Production server for deployment  
- **Render / Heroku** – Deployment platforms  

🚀 Quick Start

- 1. Clone the repo
git clone https://github.com/Anush0104/infosummary
cd document-summarizer

- 2. Create and activate virtual environment:

python -m venv venv

venv\Scripts\activate


- 3 .Install dependencies:

pip install -r requirements.txt


- 4. Install Tesseract OCR:

Windows: Download from UB Mannheim

Linux: sudo apt install tesseract-ocr

- 5.Set Tesseract path in app.py (Windows example):

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


- 6.Run the app:

python app.py


📂 Folder Structure

document-summarizer/
│
├─ app.py
├─ requirements.txt
├─ Procfile
├─ Aptfile
├─ templates/
│   ├─ index.html
│   └─ result.html
├─ uploads/
└─ README.md


🎯 Deployment

The app can be deployed on Render or Heroku. Include Aptfile with tesseract-ocr for Linux deployment

## Screenshots



Upload Document:
![Upload Document](screenshot\Screenshot (23).png)

Summary Result:
![Summary Result](screenshot\Screenshot (26).png)
