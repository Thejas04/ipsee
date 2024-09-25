chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'getCookies') {
    chrome.cookies.getAll({ url: message.url }, (cookies) => {
      if (chrome.runtime.lastError) {
        console.error(`Error getting cookies: ${chrome.runtime.lastError.message}`);
        sendResponse({ success: false });
        return;
      }

      console.log('Received cookies:', cookies); // Debugging log
      sendResponse({ success: true, cookies });
    });
    return true; // Keep the message port open for async responses
  }

  if (message.action === 'report') {
    const { url, txtTos, options } = message.data;
    console.log('Sending report to backend:', { url, txtTos, options });

    fetch('https://ip-see.com/api/report', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url, txtTos, options })
    })
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        console.log('Backend response:', data);
        sendResponse({ success: true, data });
      })
      .catch(err => {
        console.error('Error submitting report:', err);
        sendResponse({ success: false, error: err.message });
      });

    return true; // Keep the message port open for async responses
  }
});




















