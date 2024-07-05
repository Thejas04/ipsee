chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'TOS_ISSUES' || message.type === 'COOKIE_ISSUES') {
    message.issues.forEach(issue => highlightText(issue));
  }
});

function highlightText(text) {
  const regex = new RegExp(text, 'gi');
  document.body.innerHTML = document.body.innerHTML.replace(regex, match => `<span style="background-color: yellow;">${match}</span>`);
}
