// YtdlpGUI Downloader: ส่งลิงก์ไปให้แอป YtdlpGUI ที่เปิดอยู่ในเครื่อง แล้วเริ่มโหลดทันที
// Sends links to the YtdlpGUI app running on this computer and starts downloading.
//
// ตั้งแต่ 1.1.0: เฝ้าดูด้วยว่าหน้าที่เปิดอยู่ขอไฟล์วิดีโออะไรบ้าง (m3u8/mp4/mpd) แบบเดียวกับที่ IDM ทำ
// กดปุ่มแล้วส่งลิงก์นั้นเข้าแอปตรงๆ ใช้ได้กับเว็บที่แอปแกะโครงสร้างเองไม่ได้
const API = "http://127.0.0.1:47777";

// ไฟล์วิดีโอที่ควรดัก / คำที่บอกว่าเป็นคลิปตัวอย่างหรือโฆษณา ไม่ต้องเอา
const MEDIA_RE = /\.(m3u8|mpd|mp4|m4v)(\?|$)|\/hls\/|\/manifest(\?|$)/i;
const SKIP_RE = /preview|trailer|sample|thumb|sprite|\/ads?\/|vast|doubleclick|googlevideo\.com\/generate/i;
const KEEP_PER_TAB = 12;

const sniffed = new Map(); // tabId -> [{url, referer, title, when}]
const ignore = () => {};

function setBadge(tabId, text, color) {
  chrome.action.setBadgeBackgroundColor({ color, tabId }).catch(ignore);
  chrome.action.setBadgeText({ text, tabId }).catch(ignore);
}

function flash(tabId, ok) {
  setBadge(tabId, ok ? "✓" : "!", ok ? "#219E54" : "#D93025");
  setTimeout(() => showCount(tabId), 1200);
}

function showCount(tabId) {
  const list = sniffed.get(tabId) || [];
  setBadge(tabId, list.length ? String(list.length) : "", "#2574EB");
}

function notify(message) {
  chrome.notifications.create({ type: "basic", iconUrl: "icons/icon128.png", title: "YtdlpGUI", message })
    .catch(ignore);
}

// ---------- ดักลิงก์วิดีโอที่หน้าเว็บขอ ----------
chrome.webRequest.onSendHeaders.addListener(
  (d) => {
    if (d.tabId < 0 || !MEDIA_RE.test(d.url) || SKIP_RE.test(d.url)) return;
    const head = (n) => (d.requestHeaders || []).find((h) => h.name.toLowerCase() === n)?.value || "";
    const list = sniffed.get(d.tabId) || [];
    if (list.some((m) => m.url === d.url)) return;
    list.push({ url: d.url, referer: head("referer") || d.initiator || "", when: Date.now() });
    sniffed.set(d.tabId, list.slice(-KEEP_PER_TAB));
    showCount(d.tabId);
  },
  { urls: ["http://*/*", "https://*/*"] },
  ["requestHeaders"]
);

// เปลี่ยนหน้า = เริ่มนับใหม่ (ลิงก์ของหน้าเก่าหมดอายุเร็ว ใช้ไม่ได้แล้ว)
chrome.tabs.onUpdated.addListener((tabId, info) => {
  if (info.status === "loading" && info.url) {
    sniffed.delete(tabId);
    showCount(tabId);
  }
});
chrome.tabs.onRemoved.addListener((tabId) => sniffed.delete(tabId));

// เรียงลิงก์ที่ดักได้: playlist ตัวแม่ก่อน แล้วค่อย m3u8 อื่น แล้วค่อย mp4
function rank(m) {
  if (/master|playlist|index/i.test(m.url)) return 0;
  if (/\.m3u8|\.mpd|\/hls\//i.test(m.url)) return 1;
  return 2;
}

// ---------- ส่งเข้าแอป ----------
async function post(body, tabId) {
  try {
    const r = await fetch(`${API}/add`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-YtdlpGUI": "1" },
      body: JSON.stringify(body),
    });
    const j = await r.json();
    if (!r.ok || !j.ok) throw new Error(j.error || r.status);
    flash(tabId, true);
    return true;
  } catch (e) {
    flash(tabId, false);
    console.error("YtdlpGUI:", e);
    notify(`Could not send to YtdlpGUI (${e.message || e}). Make sure the app is open. / ` +
           "ส่งเข้าแอปไม่ได้ เช็คว่าเปิดแอป YtdlpGUI อยู่");
    return false;
  }
}

function sendUrls(urls, tabId) {
  urls = urls.filter((u) => /^https?:\/\//i.test(u || ""));
  if (!urls.length) {
    flash(tabId, false);
    notify("This page has no http(s) link to download. / หน้านี้ไม่มีลิงก์ที่ส่งได้");
    return;
  }
  post({ urls, start: true }, tabId);
}

async function sendSniffed(tab) {
  const list = (sniffed.get(tab.id) || []).slice().sort((a, b) => rank(a) - rank(b) || b.when - a.when);
  if (!list.length) return false;
  const best = list[0];
  const ok = await post({
    media: [{ url: best.url, referer: best.referer || tab.url, title: (tab.title || "").slice(0, 150) }],
    start: true,
  }, tab.id);
  if (ok) notify(`Sent the video this page is playing / ส่งวิดีโอที่หน้านี้กำลังเล่นเข้าแอปแล้ว:\n${best.url.slice(0, 120)}`);
  return true;
}

// กดปุ่ม: ถ้าดักวิดีโอของหน้านี้ได้ ส่งตัวนั้น (ตรงและเร็วกว่า) ถ้าไม่ได้ ส่งลิงก์หน้าเว็บให้แอปไปแกะเอง
chrome.action.onClicked.addListener(async (tab) => {
  if (await sendSniffed(tab)) return;
  sendUrls([tab.url], tab.id);
});

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.removeAll(() => {
    chrome.contextMenus.create({ id: "link", title: "Download link with YtdlpGUI", contexts: ["link"] });
    chrome.contextMenus.create({ id: "page", title: "Download this page with YtdlpGUI", contexts: ["page", "video", "frame"] });
    chrome.contextMenus.create({
      id: "sniffed",
      title: "Send the video this page is playing / ส่งวิดีโอที่หน้านี้กำลังเล่น",
      contexts: ["page", "video", "frame"],
    });
  });
});

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (info.menuItemId === "sniffed") {
    if (!(await sendSniffed(tab))) {
      notify("No video captured yet - press play first, then try again. / " +
             "ยังไม่เจอวิดีโอ ลองกดเล่นในหน้าเว็บก่อนแล้วค่อยกดใหม่");
      flash(tab && tab.id, false);
    }
    return;
  }
  const url = info.menuItemId === "link" ? info.linkUrl : info.frameUrl || info.pageUrl;
  sendUrls([url], tab && tab.id);
});
