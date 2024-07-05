chrome.cookies.getAll({ domain: window.location.hostname }, function(cookies) {
  const issues = [];
  cookies.forEach(cookie => {
    if (cookie.name.includes('sensitive') && !cookie.secure) {
      issues.push(`Cookie ${cookie.name} should be secure.`);
    }
  });
  if (issues.length > 0) {
    chrome.runtime.sendMessage({ type: 'COOKIE_ISSUES', issues });
  } else {
    chrome.runtime.sendMessage({ type: 'NO_ISSUES' });
  }
});
