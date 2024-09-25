import spacy
import torch

# Load spaCy model for advanced language understanding (trained BERT-based model)
nlp = spacy.load("./ipsee_ner_model")  # Ensure the path to your model is correct

# Expanded key phrases to detect GDPR-related terms in TOS
GDPR_KEYWORDS = {
    "data_collection": ["collect personal data", "personal information", "track user", "store personal information", "gather data"],
    "user_rights": ["right to access", "right to delete", "right to object", "right to rectification", "right to be forgotten"],
    "consent_mechanism": ["consent", "agree", "opt-in", "opt-out", "withdraw consent", "manage preferences", "privacy settings"],
    "implicit_consent": ["by using this website", "by continuing to browse", "we assume your consent"],
    "broad_data_collection": ["marketing purposes", "data analytics", "improve our services", "sell your data"],
    "third_party_sharing": ["share your data", "third-party", "sell your data", "data processors"],
    "outdated_tos": ["last updated", "effective date"],
    "cookie_duration": ["cookie expiration", "how long cookies last"],
    "deceptive_practices": ["hidden options", "only accept all", "default consent", "forced consent"]
}

# Function to analyze TOS using BERT-based model and rule-based logic
def analyze_tos_and_cookies(tos_txt, cookies_options):
    # Step 1: Use BERT-based model to analyze the TOS text
    doc = nlp(tos_txt)
    
    # Step 2: Rule-based GDPR compliance check
    gdpr_violations = []
    compliance_info = []
    transparency_info = []

    # Analyze TOS text for GDPR compliance based on key phrases
    data_collection_found = any(keyword in tos_txt.lower() for keyword in GDPR_KEYWORDS["data_collection"])
    user_rights_found = any(keyword in tos_txt.lower() for keyword in GDPR_KEYWORDS["user_rights"])
    consent_mechanism_found = any(keyword in tos_txt.lower() for keyword in GDPR_KEYWORDS["consent_mechanism"])
    implicit_consent_found = any(keyword in tos_txt.lower() for keyword in GDPR_KEYWORDS["implicit_consent"])
    broad_data_collection_found = any(keyword in tos_txt.lower() for keyword in GDPR_KEYWORDS["broad_data_collection"])
    third_party_sharing_found = any(keyword in tos_txt.lower() for keyword in GDPR_KEYWORDS["third_party_sharing"])
    outdated_tos_found = any(keyword in tos_txt.lower() for keyword in GDPR_KEYWORDS["outdated_tos"])
    cookie_duration_found = any(keyword in tos_txt.lower() for keyword in GDPR_KEYWORDS["cookie_duration"])
    deceptive_practices_found = any(keyword in tos_txt.lower() for keyword in GDPR_KEYWORDS["deceptive_practices"])

    # Print debug info for transparency
    print(f"Data Collection Found: {data_collection_found}")
    print(f"User Rights Found: {user_rights_found}")
    print(f"Consent Mechanism Found: {consent_mechanism_found}")
    print(f"Implicit Consent Found: {implicit_consent_found}")
    print(f"Broad Data Collection Found: {broad_data_collection_found}")
    print(f"Third Party Sharing Found: {third_party_sharing_found}")
    print(f"Outdated TOS Found: {outdated_tos_found}")
    print(f"Cookie Duration Found: {cookie_duration_found}")
    print(f"Deceptive Practices Found: {deceptive_practices_found}")

    # Apply advanced logic to analyze GDPR compliance
    if data_collection_found:
        transparency_info.append("The TOS mentions the collection of personal data, which should be carefully reviewed.")
    
    if user_rights_found:
        compliance_info.append("The TOS mentions GDPR user rights, such as the right to access, delete, and object, which is a positive compliance sign.")

    if consent_mechanism_found:
        compliance_info.append("The TOS describes a clear consent mechanism, allowing users to give or withdraw consent, as required by GDPR.")
    
    if implicit_consent_found:
        gdpr_violations.append("The TOS assumes implicit consent by continuing to browse, which violates GDPR's requirement for explicit consent.")

    if broad_data_collection_found:
        gdpr_violations.append("The TOS uses overly broad terms for data collection (e.g., 'marketing purposes'), which violates GDPR's transparency requirements.")

    if third_party_sharing_found:
        gdpr_violations.append("The TOS mentions sharing data with third parties without a clear explanation of user consent, violating GDPR.")

    if outdated_tos_found:
        gdpr_violations.append("The TOS appears to be outdated, potentially violating current GDPR guidelines.")

    if cookie_duration_found:
        compliance_info.append("The TOS provides information on how long cookies remain active, complying with GDPR's transparency requirements.")
    
    if deceptive_practices_found:
        gdpr_violations.append("The TOS uses deceptive practices such as hiding or obscuring cookie options, violating GDPR.")

    # Analyze cookie options
    accept_phrases = ["accept all cookies", "allow all cookies", "agree to all cookies"]
    reject_phrases = ["reject all cookies", "deny all cookies", "block all cookies"]
    
    has_accept_all = any(phrase in option.lower() for option in cookies_options for phrase in accept_phrases)
    has_reject_all = any(phrase in option.lower() for option in cookies_options for phrase in reject_phrases)

    # Scenario: Both "accept all" and "reject all" options present (Compliant)
    if has_accept_all and has_reject_all:
        compliance_info.append("The TOS provides both 'accept all' and 'reject all' options, complying with GDPR requirements for user consent.")
        return {
            "decision": "User can choose to either accept all cookies or reject all cookies.",
            "compliance": True,
            "suggestion": "Based on the analysis, it's safe to either accept all cookies or reject cookies as per your preference.",
            "summary": f"Important GDPR elements in the TOS: {', '.join(compliance_info)}",
            "explanation": "The website is GDPR compliant based on cookie options and TOS content."
        }

    # Scenario: No "reject all" option (Non-compliant)
    if has_accept_all and not has_reject_all:
        gdpr_violations.append("The TOS provides an 'accept all' option but lacks a 'reject all' option, violating GDPR's consent requirements.")

    # Scenario: Only essential cookies allowed (Compliant)
    if "essential cookies" in [option.lower() for option in cookies_options]:
        compliance_info.append("The TOS provides an option to accept only essential cookies, which complies with GDPR.")
        return {
            "decision": "User can accept only essential cookies.",
            "compliance": True,
            "suggestion": "Based on the analysis, you can safely accept only essential cookies.",
            "summary": f"Important GDPR elements in the TOS: {', '.join(compliance_info)}",
            "explanation": "The website is GDPR compliant based on cookie options and TOS content."
        }

    # Final decision for non-compliance cases
    if gdpr_violations:
        return {
            "decision": "User should reject cookies or avoid the website.",
            "compliance": False,
            "suggestion": "Based on the analysis, it's recommended to reject all cookies or avoid using this website.",
            "summary": f"Important GDPR violations in the TOS: {', '.join(gdpr_violations)}",
            "explanation": f"The website does not comply with GDPR. Reasons: {'; '.join(gdpr_violations)}"
        }

    # Default fallback decision
    return {
        "decision": "Further investigation required.",
        "compliance": False,
        "suggestion": "The website's compliance status is unclear. Further review is needed.",
        "summary": "The TOS does not provide sufficient information for compliance.",
        "explanation": "The TOS lacks critical elements to make a compliance decision."
    }

# Example input for testing the final model
tos_example_compliant = """
This website uses cookies to enhance user experience. You can choose to accept all cookies or reject all cookies. 
We only collect essential data and describe how you can withdraw consent.
"""
cookie_options_compliant = ["Accept All", "Reject All", "Manage Preferences"]

tos_example_non_compliant = """
This website uses cookies to enhance user experience. By using this website, you agree to allow all cookies. 
We collect personal data for marketing purposes, but no option to reject cookies is provided. 
By continuing to browse, we assume your consent.
"""
cookie_options_non_compliant = ["Accept All", "Manage Preferences"]

# Analyze the TOS and cookie options for compliant case
result_compliant = analyze_tos_and_cookies(tos_example_compliant, cookie_options_compliant)
print(f"Decision: {result_compliant['decision']}")
print(f"Compliance with GDPR: {result_compliant['compliance']}")
print(f"Suggestion: {result_compliant['suggestion']}")
print(f"Summary: {result_compliant['summary']}")
print(f"Explanation: {result_compliant['explanation']}")

# Analyze the TOS and cookie options for non-compliant case
result_non_compliant = analyze_tos_and_cookies(tos_example_non_compliant, cookie_options_non_compliant)
print(f"Decision: {result_non_compliant['decision']}")
print(f"Compliance with GDPR: {result_non_compliant['compliance']}")
print(f"Suggestion: {result_non_compliant['suggestion']}")
print(f"Summary: {result_non_compliant['summary']}")
print(f"Explanation: {result_non_compliant['explanation']}")
