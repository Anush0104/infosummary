from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import os

model_dir = "./models/distilbart-cnn-12-6"
os.makedirs(model_dir, exist_ok=True)

tokenizer = AutoTokenizer.from_pretrained("sshleifer/distilbart-cnn-12-6")
tokenizer.save_pretrained(model_dir)

model = AutoModelForSeq2SeqLM.from_pretrained("sshleifer/distilbart-cnn-12-6")
model.save_pretrained(model_dir)

print("Model downloaded locally at:", model_dir)
