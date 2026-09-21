// YtdlpGUI Downloader: ส่งลิงก์ไปให้แอป YtdlpGUI ที่เปิดอยู่ในเครื่อง แล้วเริ่มโหลดทันที
// Sends links to the YtdlpGUI app running on this computer and starts downloading.
const API = "http://127.0.0.1:47777";

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({ id: "link", title: "Download link with YtdlpGUI", contexts: ["link"] });
  chrome.contextMenus.create({ id: "page", title: "Download this page with YtdlpGUI", contexts: ["page", "video", "frame"] });
});

function badge(tabId, ok) {
  chrome.action.setBadgeBackgroundColor({ color: ok ? "#219E54" : "#D93025", tabId });
  chrome.action.setBadgeText({ text: ok ? "✓" : "!", tabId });
  setTimeout(() => chrome.action.setBadgeText({ text: "", tabId }), 3000);
}

function notify(message) {
  chrome.notifications.create({ type: "basic", iconUrl: "icons/icon128.png", title: "YtdlpGUI", message });
}

async function send(urls, tabId) {
  urls = urls.filter((u) => /^https?:\/\//i.test(u || ""));
  if (!urls.length) {
    badge(tabId, false);
    notify("This page has no http(s) link to download.");
    return;
  }
  try {
    const r = await fetch(`${API}/add`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-YtdlpGUI": "1" },
      body: JSON.stringify({ urls, start: true }),
    });
    const j = await r.json();
    if (!r.ok || !j.ok) throw new Error(j.error || r.status);
    badge(tabId, true);
  } catch (e) {
    badge(tabId, false);
    notify("YtdlpGUI is not running. Open YtdlpGUI.exe first, then try again. / เปิดแอป YtdlpGUI ก่อน แล้วลองใหม่");
  }
}

chrome.action.onClicked.addListener((tab) => send([tab.url], tab.id));

chrome.contextMenus.onClicked.addListener((info, tab) => {
  const url = info.menuItemId === "link" ? info.linkUrl : info.frameUrl || info.pageUrl;
  send([url], tab && tab.id);
});
