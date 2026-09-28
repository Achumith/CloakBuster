/**
 * CloakBuster Background Service Worker
 * Intercepts navigation events and queries CloakBuster Inspection API.
 */

const API_ENDPOINT = "http://127.0.0.1:8000/api/v1/analyze";

chrome.webNavigation.onBeforeNavigate.addListener(async (details) => {
  // Only inspect main frame navigations
  if (details.frameId !== 0) return;

  const targetUrl = details.url;

  // Ignore internal extension or local safe endpoints
  if (targetUrl.startsWith("chrome://") || targetUrl.startsWith("chrome-extension://")) {
    return;
  }

  try {
    const response = await fetch(API_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: targetUrl })
    });

    if (response.ok) {
      const result = await response.json();

      // If CloakBuster risk score >= 70, block access and redirect to warning page
      if (result.risk_score >= 70.0) {
        console.warn(`[CloakBuster Shield] Blocking suspicious URL (${result.risk_score}/100): ${targetUrl}`);
        
        const warningUrl = chrome.runtime.getURL("blocked.html") + 
          `?url=${encodeURIComponent(targetUrl)}` +
          `&score=${result.risk_score}` +
          `&reason=${encodeURIComponent(result.risk_level)}`;

        chrome.tabs.update(details.tabId, { url: warningUrl });
      }
    }
  } catch (err) {
    console.error("[CloakBuster Shield] Inspection API query failed:", err);
  }
});
