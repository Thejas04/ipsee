import spacy

# Load the fine-tuned AI model
nlp = spacy.load("./ipsee_ner_model")  # Adjust path as per your directory

# Demo 2 TOS for testing (Personal Data Collection Scenario)
tos_text_demo2 = """
We use cookies to enhance your browsing experience and share data with third-party partners. By continuing, you agree to our Terms of Service.

Realistic TOS for Personal Data Collection:
This website uses cookies to track your behavior and collect personal data such as your IP address, location data, browsing history, and personal preferences.
We share this data with third-party advertising networks, marketing agencies, and social media platforms for the purpose of targeted advertising. This data may also be used to create user profiles and deliver personalized ads across multiple websites.
Some cookies are essential for website functionality, but others are used to collect information for performance analysis and marketing campaigns. These non-essential cookies are shared with third parties, and your personal data may be stored outside the European Economic Area (EEA), which could be in violation of GDPR.
By accepting all cookies, you agree to share your personal information with third-party partners and permit cross-site tracking. You also consent to the possibility of data transfer to non-GDPR-compliant regions.
If you do not wish to share your personal data, you can choose to reject all non-essential cookies. However, essential cookies necessary for website functionality cannot be disabled.
"""

# Process the TOS text using the fine-tuned model
doc = nlp(tos_text_demo2)

# Analyze the results for violations
violations = []
for ent in doc.ents:
    if ent.label_ == "VIOLATION":
        violations.append(ent.text)

# Output the analysis results
if violations:
    print(f"Non-compliant TOS found! Violations: {violations}")
else:
    print("TOS is GDPR compliant.")

