import spacy
from spacy.training.example import Example

# Load the base spaCy model
nlp = spacy.load("en_core_web_sm")

# Updated training data with exact sentences from Demo 3 and variations
TRAIN_DATA = [
    # Demo 1: No violations (GDPR-compliant)
    ("This website uses cookies to ensure the proper functioning of our services. We do not share your data with any third parties or use cookies for tracking.",
     {"entities": []}),

    # Demo 2: Collecting personal info and sharing it with third parties (Non-compliant)
    ("We collect personal information, including name, email, and browsing history, which is shared with third-party advertisers and partners.",
     {"entities": [(11, 31, "VIOLATION"), (61, 98, "VIOLATION"), (108, 151, "VIOLATION")]}),

    # Demo 3: Exact essential cookies sentence from your TOS
    ("This website requires essential cookies for core functionality. By continuing, you agree to our Terms of Service.",
     {"entities": [(13, 30, "ESSENTIAL_COOKIE")]}),

    ("Essential Cookies Required for Functionality: This website uses essential cookies that are strictly necessary for the operation of our services.",
     {"entities": [(0, 27, "ESSENTIAL_COOKIE"), (50, 67, "ESSENTIAL_COOKIE")]}),

    # Variation 1: Essential cookies for session management
    ("Essential cookies related to session management, authentication, and secure browsing are required for core functionality.",
     {"entities": [(0, 17, "ESSENTIAL_COOKIE")]}),

    # Variation 2: Accepting essential cookies enables core features
    ("By accepting essential cookies, you enable core functionalities such as login, access to secure areas, and personalized settings.",
     {"entities": [(14, 31, "ESSENTIAL_COOKIE")]}),

    # Variation 3: Functional impact of rejecting essential cookies
    ("Without essential cookies, certain parts of the website, such as logging in, maintaining your session, or completing transactions, may not function correctly.",
     {"entities": [(8, 25, "ESSENTIAL_COOKIE")]}),

    # Demo 4: Collecting personal info, only 'Accept All' (Non-compliant with no rejection option)
    ("We collect your personal data, including browsing history and location data, for advertising purposes. You only have the option to accept all cookies.",
     {"entities": [(16, 30, "VIOLATION"), (56, 78, "VIOLATION"), (112, 135, "VIOLATION"), (99, 112, "MISLEADING_OPTION")]}),

    # Demo 5: Personal data use with compliant terms (GDPR-compliant)
    ("We collect personal data only for essential services and session management. No tracking or third-party sharing occurs.",
     {"entities": []}),

    # Demo 6: More essential cookies with session management
    ("This website uses essential cookies that are strictly necessary for session management, security, and authentication.",
     {"entities": [(13, 29, "ESSENTIAL_COOKIE")]}),

    ("Without essential cookies, we cannot ensure secure authentication or maintain your session.",
     {"entities": [(8, 25, "ESSENTIAL_COOKIE")]}),

    # Demo 7: Misuse of personal data for tracking
    ("We use personal data to track your activity across our website and partner websites to deliver targeted ads.",
     {"entities": [(7, 19, "VIOLATION"), (38, 65, "VIOLATION")]}),
]

# Helper function to align entity spans with tokens
def calculate_correct_spans(nlp, training_data):
    corrected_data = []
    for text, annotations in training_data:
        doc = nlp(text)
        entities = []
        for start, end, label in annotations["entities"]:
            span = doc.char_span(start, end, label=label)
            if span is not None:
                entities.append((span.start_char, span.end_char, label))
        corrected_data.append((text, {"entities": entities}))
    return corrected_data

# Get the NER component from the model
ner = nlp.get_pipe("ner")

# Add new labels (violations, essential cookies, and misleading options) to the NER model
for _, annotations in TRAIN_DATA:
    for ent in annotations.get("entities"):
        ner.add_label(ent[2])

# Align the entity spans with tokens
TRAIN_DATA = calculate_correct_spans(nlp, TRAIN_DATA)

# Disable other pipes and train only NER
unaffected_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]

with nlp.disable_pipes(*unaffected_pipes):
    optimizer = nlp.begin_training()
    for i in range (100):  # Continue training with more iterations
        losses = {}
        for text, annotations in TRAIN_DATA:
            doc = nlp.make_doc(text)
            example = Example.from_dict(doc, annotations)
            nlp.update([example], sgd=optimizer, drop=0.25, losses=losses)
        print(f"Iteration {i + 1}, Losses: {losses}")

# Save the fine-tuned model
nlp.to_disk("./ipsee_ner_model")

print("Fine-tuned model saved as 'ipsee_ner_model'")
