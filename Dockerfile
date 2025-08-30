# Use a lightweight Python image
FROM python:3.11-slim

# Install system dependencies like Tesseract OCR and Poppler utils
RUN apt-get update && \
    apt-get install -y tesseract-ocr libtesseract-dev libleptonica-dev pkg-config poppler-utils && \
    rm -rf /var/lib/apt/lists/*

# Set working directory inside container
WORKDIR /app

# Copy all project files to the container
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port (Render uses PORT environment variable)
ENV PORT=10000

# Command to run the Flask app with Gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:$PORT"]
