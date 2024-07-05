fetch(window.location.href)
  .then(response => response.text())
  .then(data => {
    fetch('http://localhost:5000/api/analyze-tos', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: data })
    })
    .then(response => response.json())
    .then(result => {
      const issues = [];
      if (!result.includes('opt-out')) {
        issues.push('No opt-out option found.');
      }
      chrome.runtime.sendMessage({ type: 'TOS_ISSUES', result, issues });
    });
  });
