const analyzeCookiesAndTOS = async () => {
  const currentUrl = window.location.href;
  console.log('Analyzing cookies and TOS for:', currentUrl);

  // Step 1: Extract the TOS text and cookie options
  const extractedData = extractTosAndCookieOptions();

  if (!extractedData.tosText || !extractedData.cookieOptions) {
    console.error('Error: TOS text or cookie options are missing.');
    return;
  }

  // Normalize and sanitize the TOS text
  const normalizedTosText = extractedData.tosText.replace(/\s+/g, ' ').replace(/[^\x20-\x7E]/g, '').trim();
  const cookieOptions = extractedData.cookieOptions;

  console.log('Extracted TOS text (sanitized):', normalizedTosText);
  console.log('Extracted Cookie Options:', cookieOptions);

  // Step 2: Retrieve cookies
  chrome.runtime.sendMessage({ action: 'getCookies', url: currentUrl }, (response) => {
    if (chrome.runtime.lastError) {
      console.error(`Error retrieving cookies: ${chrome.runtime.lastError.message}`);
      return;
    }

    if (!response || !response.success || !response.cookies) {
      console.error('Error: No cookies retrieved or invalid response.');
      return;
    }

    const cookies = response.cookies;
    console.log('Cookies received:', cookies);

    // Step 3: Send the extracted data and cookies to the backend
    sendToBackend(currentUrl, normalizedTosText, cookieOptions, cookies);
  });

  return true; // Keep the message port open for asynchronous responses
};

// Helper function to show confirmation dialog before taking action
// --- START OF NEW CODE ---
const showUserNotification = (message, onConfirm, onCancel) => {
  if (confirm(message)) {
    onConfirm();
  } else {
    console.log('User canceled the action.');
    if (onCancel) onCancel(); // Call the onCancel function if provided
  }
};
// --- END OF NEW CODE ---

// Helper function to send data to the backend
const sendToBackend = (url, tosText, cookieOptions, cookies) => {
  const dataToSend = {
    url: url,
    txtTos: tosText,
    options: cookieOptions,
  };

  console.log('Data being sent to backend:', JSON.stringify(dataToSend, null, 2));

  // Send data to the backend and handle the response
  chrome.runtime.sendMessage({ action: 'report', data: dataToSend }, (response) => {
    if (chrome.runtime.lastError) {
      console.error(`Backend error: ${chrome.runtime.lastError.message}`);
      return;
    }

    if (!response || !response.success) {
      console.error('Backend Error:', response ? response.error : 'No response received');
      return;
    }

    console.log('Backend response:', response.data);

    const { compliant, violations, flagged } = response.data;

    if (flagged) {
      handleFlaggedScenario(url);
    } 
    // --- START OF NEW CODE ---
    else if (compliant) {
      console.log('TOS is GDPR compliant.');
      const essentialCookies = cookies.filter(cookie => isEssential(cookie));

      // Notify the user before accepting cookies
      showUserNotification('The site is GDPR compliant. Do you want to accept essential cookies?', () => {
        acceptCookies(essentialCookies); // onConfirm action
      }, () => {
        console.log('Action canceled by user, no cookies will be accepted.'); // onCancel action
      });
    } else {
      console.log('TOS is non-compliant. Violations found:', violations);
      const nonEssentialCookies = cookies.filter(cookie => !isEssential(cookie));

      // Notify the user before rejecting cookies
      showUserNotification('The site is non-compliant. Do you want to reject non-essential cookies?', () => {
        rejectCookies(nonEssentialCookies); // onConfirm action
      }, () => {
        console.log('Action canceled by user, no cookies will be rejected.'); // onCancel action
      });
    }
    // --- END OF NEW CODE ---

    handleCookieConsent(compliant, cookieOptions);
  });

  return true;
};

// Handle flagged scenarios
const handleFlaggedScenario = (url) => {
  const acceptAllButton = findButtonByText('Accept all cookies');
  const rejectButton = findButtonByText('Reject all cookies');

  if (acceptAllButton && !rejectButton) {
    console.log('Only "Accept All" button found, no "Reject All" option available. Flagging the website.');

    // Flagging the website as non-compliant
    flagNonCompliantWebsite(url);

    // Disable the button and notify the user
    acceptAllButton.disabled = true;
    acceptAllButton.style.backgroundColor = '#d9534f'; // Red color to indicate the button is disabled
    acceptAllButton.style.cursor = 'not-allowed';

    // Trigger alerts every 5 seconds
    const alertInterval = setInterval(() => {
      alert("Warning: This website does not comply with GDPR. It only offers 'Accept All Cookies' without a rejection option.");
    }, 5000); // 5-second interval

    // Stop alerting when the user leaves or reloads the page
    window.addEventListener('beforeunload', () => {
      clearInterval(alertInterval);
    });
  }
};

// Simplified extraction of TOS and cookie options
const extractTosAndCookieOptions = () => {
  const tosElement = document.querySelector('#tosPopup');
  const tosText = tosElement ? tosElement.textContent.replace(/\s+/g, ' ').trim() : '';

  const cookiePopupElement = document.querySelector('#cookiePopup');
  const cookieOptions = [];

  if (cookiePopupElement) {
    const buttons = cookiePopupElement.querySelectorAll('button');
    buttons.forEach(button => {
      cookieOptions.push(button.textContent.trim());
    });
  }

  return {
    tosText: tosText || 'No TOS available',
    cookieOptions: cookieOptions.join(', ') || 'No cookie options available'
  };
};

// Function to handle cookie consent actions
const handleCookieConsent = (isCompliant, cookieOptions) => {
  const rejectButton = findButtonByText('Reject');
  const acceptButton = findButtonByText('Accept essential cookies');
  const acceptAllButton = findButtonByText('Accept all cookies');

  if (isCompliant && acceptButton) {
    console.log('TOS is compliant. Accepting essential cookies.');
    acceptButton.click();
  } else if (!isCompliant && rejectButton) {
    console.log('TOS is non-compliant. Rejecting non-essential cookies.');
    rejectButton.click();
  }

  if (acceptAllButton && !isCompliant) {
    console.log('Non-compliant website with "Accept All" option. Flagging.');
    flagNonCompliantWebsite(window.location.href);
  }
};

// Helper function to find buttons by visible text
const findButtonByText = (text) => {
  const buttons = document.querySelectorAll('button');
  return [...buttons].find(button => button.textContent.trim().toLowerCase().includes(text.toLowerCase())) || null;
};

// Helper function to classify cookies as essential
const isEssential = (cookie) => cookie.name.includes('session') || cookie.name.includes('auth');

// Accept essential cookies
const acceptCookies = (cookies) => {
  cookies.forEach(cookie => {
    console.log(`Accepting essential cookie: ${cookie.name}`);
    document.cookie = `${cookie.name}=${cookie.value}; path=/; Secure; SameSite=Lax`;
  });
};

// Reject non-essential cookies
const rejectCookies = (cookies) => {
  cookies.forEach(cookie => {
    console.log(`Rejecting non-essential cookie: ${cookie.name}`);
    document.cookie = `${cookie.name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; Secure; SameSite=Lax`;
  });
};

// Function to flag non-compliant websites and count visits
const flagNonCompliantWebsite = (url) => {
  chrome.storage.sync.get(['flaggedWebsites', 'visitCounts'], (result) => {
    let flaggedWebsites = result.flaggedWebsites || [];
    let visitCounts = result.visitCounts || {};

    if (!flaggedWebsites.includes(url)) {
      flaggedWebsites.push(url);
      visitCounts[url] = 1;
    } else {
      visitCounts[url] = visitCounts[url] ? visitCounts[url] + 1 : 1;
    }

    chrome.storage.sync.set({ flaggedWebsites, visitCounts }, () => {
      console.log(`Website ${url} flagged for non-compliance and visited ${visitCounts[url]} time(s).`);

      chrome.runtime.sendMessage({
        action: 'updateVisitCount',
        url: url,
        visitCount: visitCounts[url]
      });

      if (visitCounts[url] > 1) {
        chrome.runtime.sendMessage({
          action: 'triggerRedAlert',
          url: url
        });
      }
    });
  });
};

// Start the analysis of cookies and TOS
analyzeCookiesAndTOS();
