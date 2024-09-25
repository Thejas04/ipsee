import spacy

# Load the fine-tuned model
model_path = "./ipsee_ner_model"  # Ensure this points to your fine-tuned model
nlp = spacy.load(model_path)

# Input TOS from Demo 1
tos_text = """
We use cookies to ensure the proper functioning of our website. By accepting, you agree to our Terms of Service.

Terms of Service:
By using this website, you agree to our use of cookies for essential website functionality only. No personal data is collected for marketing or advertising purposes.
Essential cookies are required for the basic functionality of the website, such as session management and login functions. No tracking or advertising cookies are used.
We value your privacy and ensure that no personal data is shared with third parties.
If you do not agree with these terms, please do not use this website. Continued use of this site signifies your agreement to these terms.
"""

# Process the TOS text through the model
doc = nlp(tos_text)

# Check for violations
violations = []
for ent in doc.ents:
    if ent.label_ == 'VIOLATION':
        violations.append(ent.text)

# Output the result
if violations:
    print("TOS is non-compliant. Violations found:")
    for violation in violations:
        print(f" - {violation}")
else:
    print("TOS is GDPR compliant. No violations found.")
