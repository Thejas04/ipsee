import spacy
import torch
import json
import numpy as np
import wandb
import logging
from spacy.training.example import Example
from transformers import AutoModel, AutoTokenizer
from sklearn.model_selection import KFold
from torch.optim.lr_scheduler import ReduceLROnPlateau
from torch.nn.utils import clip_grad_norm_
from torch.optim import AdamW

# Set up logging for debugging and tracking
logging.basicConfig(filename="training.log", level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

# Initialize Weights & Biases logging
wandb.init(project="ipsee_ner_training", config={
    "epochs": 100,
    "batch_size": 8,
    "learning_rate": 1e-4
})

# Load Hugging Face transformer model (e.g., BERT Large) and tokenizer
model_name = "bert-large-uncased"
transformer_model = AutoModel.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Enable mixed precision for faster and memory-efficient training
scaler = torch.amp.GradScaler()

# Fine-tune only the last two layers of the transformer
for param in transformer_model.parameters():
    param.requires_grad = False
for param in transformer_model.encoder.layer[-2:].parameters():
    param.requires_grad = True

# Load spaCy transformer model
spacy.prefer_gpu()
nlp = spacy.load("en_core_web_trf")

# Load training data from external JSON file with validation and error handling
def load_training_data(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        valid_data = []
        for entry in data:
            if all(k in entry for k in ['file_name', 'cookie_options', 'tos', 'gdpr_compliance']):
                valid_data.append(entry)
            else:
                logging.warning(f"Invalid entry detected in {file_path}, skipping: {entry}")
        return valid_data
    except FileNotFoundError as e:
        logging.error(f"Training data file not found: {file_path}. Error: {e}")
        raise e

TRAIN_DATA = load_training_data("training_data.json")

# Prepare training data
def prepare_training_data(nlp, training_data):
    prepared_data = []
    for entry in training_data:
        try:
            if 'tos' in entry and 'content' in entry['tos']:
                text = " ".join(entry['tos']['content'])
                doc = nlp(text)
                prepared_data.append((text, {}))
            else:
                logging.warning(f"Missing 'tos' content in entry: {entry}")
        except Exception as e:
            logging.error(f"Error preparing data: {e}")
            continue
    return prepared_data

TRAIN_DATA = prepare_training_data(nlp, TRAIN_DATA)

# Cross-validation setup with KFold
n_folds = 2
kf = KFold(n_splits=n_folds, shuffle=True)

# Separate PyTorch optimizer for the transformer model
params = [
    {"params": transformer_model.encoder.layer[:6].parameters(), "lr": 1e-5},
    {"params": transformer_model.encoder.layer[6:].parameters(), "lr": 5e-5},
    {"params": transformer_model.pooler.parameters(), "lr": 5e-5},
]
transformer_optimizer = AdamW(params)
scheduler = ReduceLROnPlateau(transformer_optimizer, 'min', factor=0.5, patience=2)

# Get the spaCy optimizer
spacy_optimizer = nlp.resume_training()

# Early stopping parameters
best_loss = float('inf')
patience = 5
trigger_times = 0

# Cross-validation loop
for fold, (train_idx, val_idx) in enumerate(kf.split(TRAIN_DATA)):
    print(f"Training Fold {fold+1}/{n_folds}...")
    train_data = np.array(TRAIN_DATA)[train_idx]
    val_data = np.array(TRAIN_DATA)[val_idx]

    for epoch in range(wandb.config.epochs):
        losses = {}
        batch_size = wandb.config.batch_size
        for batch in spacy.util.minibatch(train_data, size=batch_size):
            texts, _ = zip(*batch)
            examples = [Example.from_dict(nlp.make_doc(text), {}) for text in texts]

            # Update the spaCy model (NER)
            nlp.update(examples, sgd=spacy_optimizer, drop=0.25, losses=losses)

            # Update the transformer model (PyTorch)
            with torch.amp.autocast(device_type='cuda'):
                clip_grad_norm_(transformer_model.parameters(), max_norm=1.0)
                transformer_optimizer.step()

        scheduler.step(sum(losses.values()))
        current_loss = sum(losses.values())
        wandb.log({"loss": current_loss, "epoch": epoch + 1, "fold": fold + 1})

        if current_loss < best_loss:
            best_loss = current_loss
            trigger_times = 0
        else:
            trigger_times += 1
            if trigger_times >= patience:
                logging.info(f"Early stopping at epoch {epoch + 1} on fold {fold + 1}.")
                break

        print(f"Epoch {epoch + 1}/{wandb.config.epochs}, Loss: {current_loss}")

# Save the fine-tuned model
nlp.to_disk("./ipsee_ner_model")
logging.info("Fine-tuned model saved as 'ipsee_ner_model'")
print("Model saved successfully!")
