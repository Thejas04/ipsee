router.post('/', async (req, res) => {
  const { url, txtTos, options } = req.body;

  try {
    const response = await axios.post('http://flask_api:5000/analyze', {
      tos_text: txtTos,
      options: options
    });

    const { compliant, violations, essentialCookiesRequired, cookieOptions } = response.data;

    const flagged = !compliant || violations.length > 0 || essentialCookiesRequired;

    if (flagged) {
      const newReport = new Report({ url, violations });
      await newReport.save();
    }

    return res.status(200).json({
      compliant,
      violations,
      essentialCookiesRequired,  // Return this to the frontend
      cookieOptions,
      flagged
    });
  } catch (error) {
    return res.status(500).json({ error: 'Error analyzing TOS' });
  }
});
