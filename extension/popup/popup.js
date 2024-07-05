document.addEventListener('DOMContentLoaded', function() {
  const toggle = document.getElementById('toggleExtension');
  const status = document.getElementById('status');

  chrome.storage.sync.get('enabled', function(data) {
    console.log('Storage get:', data);
    toggle.checked = data.enabled || false;
    status.textContent = data.enabled ? 'Extension is enabled' : 'Extension is disabled';
    status.className = data.enabled ? 'enabled' : 'disabled';
  });

  toggle.addEventListener('change', function() {
    chrome.storage.sync.set({enabled: toggle.checked}, function() {
      console.log('Storage set:', {enabled: toggle.checked});
      status.textContent = toggle.checked ? 'Extension is enabled' : 'Extension is disabled';
      status.className = toggle.checked ? 'enabled' : 'disabled';
      chrome.runtime.sendMessage({type: 'TOGGLE_EXTENSION', enabled: toggle.checked}, function(response) {
        if (chrome.runtime.lastError) {
          console.error(chrome.runtime.lastError.message);
        } else {
          console.log(response.status);
        }
      });
    });
  });
});

