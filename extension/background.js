chrome.runtime.onInstalled.addListener(() => {
  console.log("Extension installed");
});

chrome.action.onClicked.addListener((tab) => {
  chrome.scripting.executeScript({
    target: {tabId: tab.id},
    files: ['content_scripts/analyzeCookies.js']
  });
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'TOGGLE_EXTENSION') {
    console.log(`Extension enabled: ${message.enabled}`);
    // Add any additional logic needed when the extension is toggled
    sendResponse({status: 'success'});
  }
  return true; // Necessary to keep the message channel open for sendResponse
});
