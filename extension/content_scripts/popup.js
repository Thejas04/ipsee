document.addEventListener('DOMContentLoaded', function() {
  const toggle = document.getElementById('toggleExtension');
  const status = document.getElementById('status');

  chrome.storage.sync.get('enabled', function(data) {
    toggle.checked = data.enabled;
    status.textContent = data.enabled ? 'Extension is enabled' : 'Extension is disabled';
  });

  toggle.addEventListener('change', function() {
    chrome.storage.sync.set({enabled: toggle.checked}, function() {
      status.textContent = toggle.checked ? 'Extension is enabled' : 'Extension is disabled';
      chrome.runtime.sendMessage({type: 'TOGGLE_EXTENSION', enabled: toggle.checked});
    });
  });

  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === 'COOKIE_ISSUES' || message.type === 'TOS_ISSUES') {
      displayPopup(message.issues.join('\n'));
    } else if (message.type === 'NO_ISSUES') {
      displayPopup('No issues found. The site is safe.');
    }
  });

  function displayPopup(message) {
    const popup = document.createElement('div');
    popup.className = 'privacy-popup';
    popup.innerText = message;
    document.body.appendChild(popup);

    setTimeout(() => { popup.remove(); }, 5000);
  }
});
