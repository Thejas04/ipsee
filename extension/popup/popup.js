// Listen for messages from the content script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'flagWebsite') {
    const url = message.url;
    const visitCount = message.visitCount || 1;

    // Store the flagged website and its visit count in chrome.storage
    chrome.storage.sync.get(['flaggedWebsites', 'visitCounts'], (result) => {
      let flaggedWebsites = result.flaggedWebsites || [];
      let visitCounts = result.visitCounts || {};

      if (!flaggedWebsites.includes(url)) {
        flaggedWebsites.push(url);
        visitCounts[url] = visitCount;
      } else {
        visitCounts[url] = visitCount;
      }

      chrome.storage.sync.set({ flaggedWebsites, visitCounts }, () => {
        console.log(`Website ${url} flagged and visited ${visitCounts[url]} time(s).`);
        updatePopup();

        if (visitCounts[url] > 1) {
          showRedAlert(url, visitCounts[url]);
        }
      });
    });
  }
});

// Function to show red alert when flagged website is visited multiple times
const showRedAlert = (url, visitCount) => {
  const container = document.getElementById('alert-container');
  container.innerHTML = `
    <div class="alert">
      Warning: You've visited the flagged website <b>${url}</b> ${visitCount} time(s)!
    </div>`;
};

// Update the popup to display flagged websites and their visit counts
const updatePopup = () => {
  chrome.storage.sync.get(['flaggedWebsites', 'visitCounts'], (result) => {
    const flaggedWebsites = result.flaggedWebsites || [];
    const visitCounts = result.visitCounts || {};
    const container = document.getElementById('reported-websites');
    container.innerHTML = ''; // Clear the container before updating

    if (flaggedWebsites.length > 0) {
      const list = document.createElement('ul');
      flaggedWebsites.forEach(site => {
        const listItem = document.createElement('li');
        listItem.textContent = `${site} - Visited ${visitCounts[site] || 0} time(s)`;
        list.appendChild(listItem);
      });
      container.appendChild(list);
    } else {
      const message = document.createElement('p');
      message.textContent = 'No flagged websites';
      container.appendChild(message);
    }
  });
};

// --- START OF NEW CODE ---
// Add the user consent handling for cookie automation
document.getElementById('consent-yes').addEventListener('click', () => {
  chrome.storage.sync.set({ consent: 'yes' }, () => {
    console.log('User consented to automate cookie management.');
    document.getElementById('consent-section').style.display = 'none';
    document.getElementById('override-container').style.display = 'block'; // Show the override options
  });
});

document.getElementById('consent-no').addEventListener('click', () => {
  chrome.storage.sync.set({ consent: 'no' }, () => {
    console.log('User declined to automate cookie management.');
    document.getElementById('consent-section').style.display = 'none';
    document.getElementById('override-container').style.display = 'block'; // Show the override options
  });
});

// Handle accept and reject override buttons
document.getElementById('accept-cookies').addEventListener('click', () => {
  chrome.runtime.sendMessage({ action: 'overrideAccept' });
  console.log('User chose to accept cookies.');
});

document.getElementById('reject-cookies').addEventListener('click', () => {
  chrome.runtime.sendMessage({ action: 'overrideReject' });
  console.log('User chose to reject cookies.');
});
// --- END OF NEW CODE ---

// Report flagged websites to the backend
document.getElementById('report-flagged').addEventListener('click', () => {
  chrome.storage.sync.get(['flaggedWebsites'], (result) => {
    const flaggedWebsites = result.flaggedWebsites || [];

    flaggedWebsites.forEach((site) => {
      fetch('https://ip-see.com/db-report', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: site }),
      })
      .then(response => response.json())
      .then(data => {
        console.log(`Website ${site} reported successfully:`, data);
      })
      .catch(error => {
        console.error(`Error reporting website ${site}:`, error);
      });
    });
  });
});

// Delete flagged websites from the backend
document.getElementById('delete-flagged').addEventListener('click', () => {
  chrome.storage.sync.get(['flaggedWebsites'], (result) => {
    const flaggedWebsites = result.flaggedWebsites || [];

    flaggedWebsites.forEach((site) => {
      fetch('https://ip-see.com/db-delete', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: site }),
      })
      .then(response => response.json())
      .then(data => {
        console.log(`Website ${site} deleted successfully:`, data);

        chrome.storage.sync.remove(['flaggedWebsites', 'visitCounts'], () => {
          updatePopup();
        });
      })
      .catch(error => {
        console.error(`Error deleting website ${site}:`, error);
      });
    });
  });
});

// Clear flagged websites in chrome storage
document.getElementById('clear-storage').addEventListener('click', () => {
  chrome.storage.sync.remove(['flaggedWebsites', 'visitCounts'], () => {
    updatePopup();
  });
});

// Load flagged websites on popup open
document.addEventListener('DOMContentLoaded', () => {
  updatePopup();
});



