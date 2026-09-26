// YtdlpGUI Downloader: ส่งลิงก์ไปให้แอป YtdlpGUI ที่เปิดอยู่ในเครื่อง แล้วเริ่มโหลดทันที
// Sends links to the YtdlpGUI app running on this computer and starts downloading.
//
// 1.1.0: เฝ้าดูว่าหน้าที่เปิดอยู่ขอไฟล์วิดีโออะไรบ้าง (m3u8/mp4/mpd) แบบเดียวกับที่ IDM ทำ
// 1.2.0: กดไอคอนแล้วเลือกได้ว่าจะโหลดลิงก์ไหน ความละเอียดเท่าไร (หน้าต่าง popup)
const API = "http://127.0.0.1:47777";

// ไฟล์วิดีโอที่ควรดัก / คำที่บอกว่าเป็นคลิปตัวอย่างหรือโฆษณา ไม่ต้องเอา
const MEDIA_RE = /\.(m3u8|mpd|mp4|m4v)(\?|$)|\/hls\/|\/manifest(\?|$)/i;
const SKIP_RE = /preview|trailer|sample|thumb|sprite|\/ads?\/|vast|doubleclick|googlevideo\.com\/generate/i;
const KEEP_PER_TAB = 12;

const sniffed = new Map(); // tabId -> [{url, referer, when}]
const ignore = () => {};

function setBadge(tabId, text, color) {
  chrome.action.setBadgeBackgroundColor({ color, tabId }).catch(ignore);
  chrome.action.setBadgeText({ text, tabId }).catch(ignore);
}

function showCount(tabId) {
  const list = sniffed.get(tabId) || [];
  setBadge(tabId, list.length ? String(list.length) : "", "#2574EB");
}

function flash(tabId, ok) {
  setBadge(tabId, ok ? "✓" : "!", ok ? "#219E54" : "#D93025");
  setTimeout(() => showCount(tabId), 1200);
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

// เรียงลิงก์ที่ดักได้: playlist ตัวแม่ก่อน (เลือกความละเอียดได้) แล้วค่อย m3u8 อื่น แล้วค่อย mp4
function rank(m) {
  if (/master|playlist|index/i.test(m.url)) return 0;
  if (/\.m3u8|\.mpd|\/hls\//i.test(m.url)) return 1;
  return 2;
}

function listFor(tabId) {
  return (sniffed.get(tabId) || []).slice().sort((a, b) => rank(a) - rank(b) || b.when - a.when);
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
    return { ok: true };
  } catch (e) {
    flash(tabId, false);
    console.error("YtdlpGUI:", e);
    return { ok: false, error: String(e.message || e) };
  }
}

// popup ถามรายการ / สั่งส่ง
chrome.runtime.onMessage.addListener((msg, sender, reply) => {
  if (msg.type === "list") {
    reply(listFor(msg.tabId));
    return false;
  }
  if (msg.type === "send") {
    post({ media: [msg.item], start: true }, msg.tabId).then(reply);
    return true;
  }
  if (msg.type === "sendPage") {
    post({ urls: [msg.url], start: true }, msg.tabId).then(reply);
    return true;
  }
  return false;
});

// ---------- เมนูคลิกขวา (ส่งทันที ไม่ต้องเลือกความละเอียด) ----------
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
    const best = listFor(tab.id)[0];
    if (!best) {
      notify("No video captured yet - press play first, then try again. / " +
             "ยังไม่เจอวิดีโอ ลองกดเล่นในหน้าเว็บก่อนแล้วค่อยกดใหม่");
      flash(tab.id, false);
      return;
    }
    const res = await post({
      media: [{ url: best.url, referer: best.referer || tab.url, title: (tab.title || "").slice(0, 150) }],
      start: true,
    }, tab.id);
    if (res.ok) notify(`ส่งวิดีโอที่หน้านี้กำลังเล่นเข้าแอปแล้ว:\n${best.url.slice(0, 120)}`);
    else notify(`ส่งเข้าแอปไม่ได้ (${res.error}) เช็คว่าเปิดแอป YtdlpGUI อยู่`);
    return;
  }
  const url = info.menuItemId === "link" ? info.linkUrl : info.frameUrl || info.pageUrl;
  if (!/^https?:\/\//i.test(url || "")) {
    flash(tab && tab.id, false);
    notify("This page has no http(s) link to download. / หน้านี้ไม่มีลิงก์ที่ส่งได้");
    return;
  }
  const res = await post({ urls: [url], start: true }, tab && tab.id);
  if (!res.ok) notify(`ส่งเข้าแอปไม่ได้ (${res.error}) เช็คว่าเปิดแอป YtdlpGUI อยู่`);
});
