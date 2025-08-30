import os
import fitz
import pytesseract
from PIL import Image
from transformers import pipeline
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import logging
from rake_nltk import Rake
import cv2
import re

# Setup logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10MB limit
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "gif", "bmp", "webp"}

# Initialize summarizer (DistilBART for lower memory usage)
try:
    print("Loading DistilBART model... This may take a few minutes on first run.")
    summarizer = pipeline(
        "summarization",
        model="sshleifer/distilbart-cnn-12-6",
        framework="pt",
        device=-1  # use CPU
    )
    print("✅ Summarizer model loaded successfully!")
except Exception as e:
    logger.error(f"Failed to load summarizer model: {e}")
    summarizer = None


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_from_pdf(pdf_path):
    text = ""
    doc = fitz.open(pdf_path)
    for page in doc:
        text += page.get_text()
    doc.close()
    return text.strip()


def extract_text_from_image(img_path):
    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    processed_img = Image.fromarray(thresh)
    text = pytesseract.image_to_string(processed_img)
    return text.strip()


def highlight_keywords(text: str, top_n: int = 5) -> str:
    try:
        rake = Rake()
        rake.extract_keywords_from_text(text)
        keywords = [kw for _, kw in rake.get_ranked_phrases_with_scores()[:top_n]]

        highlighted = text
        for kw in keywords:
            pattern = re.compile(rf"\b{re.escape(kw)}\b", re.IGNORECASE)
            highlighted = pattern.sub(lambda m: f"<mark>{m.group(0)}</mark>", highlighted)
        return highlighted
    except Exception as e:
        logger.error(f"Keyword highlighting failed: {e}")
        return text


def generate_summary(text, length="medium"):
    if not text or len(text.strip()) < 50:
        return "Text too short for meaningful summarization."

    length_config = {
        "short": {"max_length": 60, "min_length": 20},
        "medium": {"max_length": 120, "min_length": 40},
        "long": {"max_length": 200, "min_length": 80},
    }
    config = length_config.get(length, length_config["medium"])

    chunk_size = 1000
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    summaries = []

    for chunk in chunks:
        if summarizer:
            try:
                summary = summarizer(
                    chunk,
                    max_length=config["max_length"],
                    min_length=config["min_length"],
                    do_sample=False,
                )
                summaries.append(summary[0]["summary_text"])
            except Exception as e:
                logger.error(f"Summarizer failed: {e}")
                summaries.append(create_fallback_summary(chunk, length))
        else:
            summaries.append(create_fallback_summary(chunk, length))

    return " ".join(summaries)


def create_fallback_summary(text, length="medium"):
    sentences = text.split(".")
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    length_mapping = {"short": 2, "medium": 4, "long": 6}
    num_sentences = min(length_mapping.get(length, 4), len(sentences))
    if num_sentences == 0:
        return "Unable to generate summary."
    return ". ".join(sentences[:num_sentences]) + "."


def suggest_improvements(text: str) -> str:
    suggestions = []
    if len(text.strip()) < 50:
        suggestions.append("The text is too short. Add more details for a meaningful summary.")

    sentences = [s.strip() for s in text.split(".") if s.strip()]
    long_sentences = [s for s in sentences if len(s.split()) > 25]
    if long_sentences:
        suggestions.append(f"{len(long_sentences)} sentence(s) are very long. Consider splitting them.")

    words = text.lower().split()
    repeated = {w for w in words if words.count(w) > 5 and len(w) > 3}
    if repeated:
        suggestions.append(f"Some words are repeated too often: {', '.join(list(repeated)[:5])}.")

    if not suggestions:
        suggestions.append("The text looks clear and concise. ✅")

    return "\n".join(suggestions)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/summarize", methods=["POST"])
def summarize():
    try:
        uploaded_file = request.files.get("document")
        length = request.form.get("summary_length", "medium")

        if not uploaded_file or uploaded_file.filename == "":
            return render_template("result.html", error="No file uploaded.")

        if not allowed_file(uploaded_file.filename):
            return render_template("result.html", error="Invalid file type. Please upload PDF or image files.")

        filename = secure_filename(uploaded_file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        uploaded_file.save(file_path)

        # Extract text
        if filename.lower().endswith(".pdf"):
            text = extract_text_from_pdf(file_path)
        else:
            text = extract_text_from_image(file_path)

        os.remove(file_path)

        if not text.strip():
            return render_template("result.html", error="No readable text found in the document.")

        summary_text = generate_summary(text, length)
        highlighted_summary = highlight_keywords(summary_text, top_n=5)
        improvements = suggest_improvements(summary_text)
        original_highlighted = highlight_keywords(text, top_n=10)

        total_words = len(text.split())
        total_chars = len(text)
        summary_words = len(summary_text.split())
        summary_percentage = round((summary_words / total_words) * 100, 2) if total_words else 0

        return render_template(
            "result.html",
            original=text[:2000] + "..." if len(text) > 2000 else text,
            original_highlighted=original_highlighted,
            summary=summary_text,
            highlighted_summary=highlighted_summary,
            improvements=improvements,
            length=length,
            stats={
                "total_words": total_words,
                "total_chars": total_chars,
                "summary_words": summary_words,
                "summary_percentage": summary_percentage
            }
        )

    except Exception as e:
        logger.error(f"Error in processing: {e}")
        return render_template("result.html", error=f"Error: {str(e)}")


if __name__ == "__main__":
    print("🚀 Starting Flask Document Summarizer...")
    app.run(debug=True, host="0.0.0.0", port=5000)
