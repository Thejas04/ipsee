@app.route('/analyze', methods=['POST'])
def analyze_tos():
    data = request.get_json()
    tos_text = data.get('tos_text', '')
    options = data.get('options', '')

    if not tos_text.strip():
        return jsonify({"error": "tos_text is required"}), 400

    doc = nlp(tos_text)
    violations = []
    essentialCookiesRequired = False
    misleading_option_detected = False

    # Log detected entities for debugging
    for ent in doc.ents:
        if ent.label_ == "VIOLATION":
            violations.append(ent.text)
        if ent.label_ == "ESSENTIAL_COOKIE":
            essentialCookiesRequired = True
        if ent.label_ == "MISLEADING_OPTION":
            misleading_option_detected = True

    compliant = len(violations) == 0

    # Ensure the essential cookies flag is checked and handled
    cookieOptions = "Accept Essential Cookies" if essentialCookiesRequired else (
        "Reject All Cookies" if misleading_option_detected or ("Accept All" in options and violations) else 
        "Accept All Cookies" if compliant else "Reject All Cookies"
    )

    return jsonify({
        "compliant": compliant,
        "violations": violations,
        "essentialCookiesRequired": essentialCookiesRequired,  # Ensure this is returned
        "cookieOptions": cookieOptions,
        "misleadingOptionDetected": misleading_option_detected
    }), 200
