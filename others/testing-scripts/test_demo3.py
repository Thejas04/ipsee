import spacy

# Load the fine-tuned model
model_path = "./ipsee_ner_model"  # Ensure this points to your fine-tuned model
nlp = spacy.load(model_path)

# Input TOS from Demo 3
tos_text = """
This website requires essential cookies for core functionality. By continuing, you agree to our Terms of Service.

Terms of Service:
This website uses essential cookies that are strictly necessary for the operation of our services. These include cookies related to session management, authentication, and secure browsing, which allow you to navigate the website and use its features.
Without these essential cookies, certain parts of the website may not function correctly, such as logging in, maintaining your session, or completing transactions.
By accepting essential cookies, you enable core functionalities such as the ability to log in, access secure areas, and use personalized settings. Essential cookies do not track your browsing behavior for marketing purposes.
"""

# Process the TOS text through the model
doc = nlp(tos_text)

# Check for violations and essential cookies
violations = []
essential_cookies = []
for ent in doc.ents:
    if ent.label_ == 'VIOLATION':
        violations.append(ent.text)
    elif ent.label_ == 'ESSENTIAL_COOKIE':
        essential_cookies.append(ent.text)

# Output the result
if violations:
    print("TOS is non-compliant. Violations found:")
    for violation in violations:
        print(f" - {violation}")
elif essential_cookies:
    print("This website requires essential cookies to function properly. Essential cookies found:")
    for cookie in essential_cookies:
        print(f" - {cookie}")
else:
    print("TOS is GDPR compliant. No violations or essential cookies found.")
