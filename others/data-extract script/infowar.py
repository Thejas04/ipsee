import gzip
import json
import re
import spacy
import logging
from warcio.archiveiterator import ArchiveIterator
from transformers import MarianMTModel, MarianTokenizer
import os
import torch

# Initialize logging
logging.basicConfig(filename="data_gathering.log", level=logging.INFO)

# Define output file
OUTPUT_FILE = "advanced_gdpr_training_data.json"

# GDPR Keywords for Annotations
GDPR_KEYWORDS = {
    "data_collection": ["collect personal data", "personal information", "track user", "store personal information"],
    "user_rights": ["right to access", "right to delete", "right to object", "right to rectification"],
    "consent_mechanism": ["consent", "agree", "opt-in", "opt-out", "withdraw consent"],
    "implicit_consent": ["by using this website", "by continuing to browse", "we assume your consent"],
    "broad_data_collection": ["marketing purposes", "data analytics", "improve our services"],
    "third_party_sharing": ["share your data", "third-party", "sell your data"],
    "outdated_tos": ["last updated", "effective date"],
    "cookie_duration": ["cookie expiration", "how long cookies last"],
    "deceptive_practices": ["hidden options", "only accept all", "default consent"]
}

# Cookie consent keywords (extended)
COOKIE_OPTIONS_KEYWORDS = [
    "accept all", "reject all", "essential cookies", "manage preferences",
    "deny all", "block cookies", "accept necessary", "allow all", "disable cookies"
]

# Set device to GPU if available, else CPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Initialize the spaCy model and ensure it runs on GPU if available
spacy.prefer_gpu()
nlp = spacy.load("en_core_web_trf")

# Handle large input sizes for spaCy
nlp.max_length = 2000000  # Increased to handle larger text

# Clean and preprocess the text (optional but helps with consistency)
def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

# Annotate the text with GDPR-related labels using advanced spaCy processing
def annotate_text(text):
    annotations = []
    doc = nlp(text)
    for label, keywords in GDPR_KEYWORDS.items():
        for keyword in keywords:
            start = text.lower().find(keyword)
            if start != -1:
                end = start + len(keyword)
                annotations.append({"start": start, "end": end, "label": label.upper()})
    return annotations

# Extract cookie options from TOS text
def extract_cookie_options(text):
    cookie_options = []
    for keyword in COOKIE_OPTIONS_KEYWORDS:
        if keyword in text.lower():
            cookie_options.append(keyword)
    return list(set(cookie_options))  # Remove duplicates

# Back-translation augmentation using MarianMT on GPU
def back_translate(text, source_lang="en", target_lang="fr"):
    tokenizer = MarianTokenizer.from_pretrained(f'Helsinki-NLP/opus-mt-{source_lang}-{target_lang}')
    model = MarianMTModel.from_pretrained(f'Helsinki-NLP/opus-mt-{source_lang}-{target_lang}').to(device)

    # Ensure tokenization handles long texts by truncating
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512).to(device)
    
    # Forward pass on GPU
    with torch.cuda.amp.autocast():
        translated = model.generate(**inputs)
        translation = tokenizer.decode(translated[0], skip_special_tokens=True)

    # Translate back to original language
    tokenizer_back = MarianTokenizer.from_pretrained(f'Helsinki-NLP/opus-mt-{target_lang}-{source_lang}')
    model_back = MarianMTModel.from_pretrained(f'Helsinki-NLP/opus-mt-{target_lang}-{source_lang}').to(device)

    inputs_back = tokenizer_back(translation, return_tensors="pt", padding=True, truncation=True, max_length=512).to(device)
    
    with torch.cuda.amp.autocast():
        back_translated = model_back.generate(**inputs_back)
        back_translation = tokenizer_back.decode(back_translated[0], skip_special_tokens=True)

    return back_translation

# Function to process multiple WARC files in a directory
def process_warc_files_in_directory(warc_dir):
    combined_data = []

    # Iterate over each WARC file in the directory
    for warc_file in os.listdir(warc_dir):
        if warc_file.endswith(".warc.gz"):
            file_path = os.path.join(warc_dir, warc_file)
            with gzip.open(file_path, 'rb') as f:
                logging.info(f"Processing WARC file: {warc_file}")
                for record in ArchiveIterator(f):
                    if record.rec_type == 'response':
                        try:
                            # Decode with error handling to skip invalid UTF-8 characters
                            content = record.content_stream().read().decode('utf-8', errors='ignore')
                            tos_text = clean_text(content)
                            annotations = annotate_text(tos_text)
                            cookie_options = extract_cookie_options(tos_text)
                            back_translated_text = back_translate(tos_text)

                            gdpr_compliance = {
                                "data_collection": any(keyword in tos_text.lower() for keyword in GDPR_KEYWORDS["data_collection"]),
                                "user_rights": any(keyword in tos_text.lower() for keyword in GDPR_KEYWORDS["user_rights"]),
                                "consent_mechanism": any(keyword in tos_text.lower() for keyword in GDPR_KEYWORDS["consent_mechanism"])
                            }

                            combined_data.append({
                                "text": tos_text,
                                "back_translated_text": back_translated_text,
                                "gdpr_compliance": gdpr_compliance,
                                "cookie_options": cookie_options,
                                "annotations": annotations
                            })
                        except Exception as e:
                            logging.error(f"Error processing record in {warc_file}: {e}")

    return combined_data

# Save combined data to JSON
def save_to_json(data, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    logging.info(f"Combined data saved to {output_file}")

# Main script execution
if __name__ == "__main__":
    warc_dir = "./warc_files"  # Path to the directory where WARC files are stored
    combined_data = process_warc_files_in_directory(warc_dir)

    # Save the combined data to JSON
    save_to_json(combined_data, OUTPUT_FILE)
