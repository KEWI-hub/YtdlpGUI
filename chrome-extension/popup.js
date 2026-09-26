// หน้าต่างเลือกวิดีโอ/ความละเอียด ก่อนส่งเข้าแอป
// Popup: pick which captured video (and which resolution) to send to the app.
const CHOICES = [
  { h: 0, label: "สูงสุด / Best", best: true },
  { h: 1080, label: "1080p" },
  { h: 720, label: "720p" },
  { h: 480, label: "480p" },
  { h: 360, label: "360p" },
];

const $body = document.getElementById("body");
const $msg = document.getElementById("msg");

function say(text, cls) {
  $msg.className = cls;
  $msg.textContent = text;
}

function fileName(url) {
  try {
    const u = new URL(url);
    return decodeURIComponent(u.pathname.split("/").filter(Boolean).pop() || u.hostname);
  } catch {
    return url.slice(0, 60);
  }
}

function hostOf(url) {
  try {
    return new URL(url).hostname;
  } catch {
    return "";
  }
}

async function send(payload) {
  say("กำลังส่ง ...", "");
  const res = await chrome.runtime.sendMessage(payload);
  if (res && res.ok) {
    say("ส่งเข้าแอปแล้ว / Sent to YtdlpGUI", "done");
    setTimeout(() => window.close(), 900);
  } else {
    say(`ส่งไม่สำเร็จ: ${(res && res.error) || "?"} (เปิดแอปอยู่หรือเปล่า)`, "err");
  }
}

function render(list, tab) {
  if (!list.length) {
    $body.innerHTML =
      '<p class="hint">ยังไม่เจอวิดีโอในหน้านี้ — กดเล่นให้วิดีโอเริ่มวิ่งก่อน แล้วเปิดเมนูนี้ใหม่<br>' +
      "No video captured yet: press play first, then open this again.</p>";
    return;
  }
  $body.innerHTML = `<p class="hint">เลือกความละเอียดที่จะโหลด (${list.length} ลิงก์ที่ดักได้)</p>`;
  list.forEach((m) => {
    const box = document.createElement("div");
    box.className = "item";
    const name = document.createElement("div");
    name.className = "name";
    name.textContent = fileName(m.url);
    const host = document.createElement("div");
    host.className = "host";
    host.textContent = hostOf(m.url);
    const res = document.createElement("div");
    res.className = "res";
    CHOICES.forEach((c) => {
      const b = document.createElement("button");
      b.textContent = c.label;
      if (c.best) b.className = "best";
      b.addEventListener("click", () =>
        send({ type: "send", tabId: tab.id, item: { url: m.url, referer: m.referer || tab.url,
                                                    title: (tab.title || "").slice(0, 150), height: c.h } }));
      res.appendChild(b);
    });
    box.append(name, host, res);
    $body.appendChild(box);
  });
}

(async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  const list = (await chrome.runtime.sendMessage({ type: "list", tabId: tab.id })) || [];
  render(list, tab);
  document.getElementById("page").addEventListener("click", () =>
    send({ type: "sendPage", tabId: tab.id, url: tab.url }));
})();
