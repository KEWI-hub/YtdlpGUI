"""YtdlpGUI - คิวโหลดวิดีโอด้วย yt-dlp แบบมีหน้าต่าง
โหลดพร้อมกันได้หลายลิงก์ และแยกคิวแปลง H.265 ออกมาต่างหาก
"""
import html
import itertools
import json
import os
import queue
import re
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
import urllib.parse
from urllib.parse import parse_qs, urljoin, urlparse
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

from i18n import LANGS, set_lang, tr

APP_NAME = "YtdlpGUI"
APP_VERSION = "1.4.1"  # ต้องตรงกับ tag บน GitHub (vX.Y.Z) ตอนออก Release
GITHUB_REPO = "KEWI-hub/YtdlpGUI"
LOGS_REPO = "KEWI-hub/YtdlpGUI-logs"  # repo private เก็บ error log (push ได้เฉพาะเครื่องของเจ้าของ)
APP_DIR = os.path.dirname(sys.executable if getattr(sys, "frozen", False) else os.path.abspath(__file__))
BIN_DIR = os.path.join(APP_DIR, "bin")
TMP_DIR = os.path.join(APP_DIR, "_tmp")
YTDLP = os.path.join(BIN_DIR, "yt-dlp.exe")
FFMPEG = os.path.join(BIN_DIR, "ffmpeg.exe")
SETTINGS_FILE = os.path.join(APP_DIR, "settings.json")
QUEUE_FILE = os.path.join(APP_DIR, "queue.json")
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)

FORMATS = {
    "อัตโนมัติ (เลือกที่ดีที่สุดให้)":
        ["-f", "bv*+ba/b", "--merge-output-format", "mp4", "-S", "proto:https,res,fps,br,ext:mp4:m4a"],
    "MP4 ตรง (ไม่ใช้ m3u8)": ["-f", "b[ext=mp4][protocol^=http]/b[ext=mp4]/bv*+ba/b", "--merge-output-format", "mp4"],
    "ดีที่สุด (แยกภาพ+เสียง แล้วรวม)": ["-f", "bv*+ba/b", "--merge-output-format", "mp4"],
}
AUTO_FMT = "อัตโนมัติ (เลือกที่ดีที่สุดให้)"
BEST_FMT = "ดีที่สุด (แยกภาพ+เสียง แล้วรวม)"
AUTO_RES = 1080  # "อัตโนมัติ" + ความชัด "สูงสุด" = จำกัดที่ 1080p (ไม่มีก็เอา 720p) ยกเว้น YouTube ที่เอาชัดสุดเสมอ
RESOLUTIONS = {"สูงสุด": 0, "1080p": 1080, "720p": 720}  # 0 = ไม่จำกัด
BROWSERS = ["ไม่ใช้", "firefox", "chrome", "edge", "brave", "opera"]
PRESETS = ["ultrafast", "veryfast", "fast", "medium", "slow", "slower"]
CONTAINERS = ["mp4", "mkv"]
# ตัวแปลง H.265: ชื่อที่โชว์ -> ffmpeg encoder (เรียงตามความเร็ว เลือกตัวแรกที่ใช้ได้เป็นค่าเริ่มต้น)
ENCODERS = {
    "NVIDIA (NVENC)": "hevc_nvenc",
    "AMD (AMF)": "hevc_amf",
    "Intel (QSV)": "hevc_qsv",
    "CPU (x265)": "libx265",
}
CPU_ENC = "CPU (x265)"
NV_PRESET = {"ultrafast": "p1", "veryfast": "p2", "fast": "p3", "medium": "p4", "slow": "p6", "slower": "p7"}
AMF_QUALITY = {"ultrafast": "speed", "veryfast": "speed", "fast": "balanced", "medium": "balanced",
               "slow": "quality", "slower": "quality"}
QSV_PRESET = {"ultrafast": "veryfast", "veryfast": "veryfast", "fast": "fast", "medium": "medium",
              "slow": "slow", "slower": "veryslow"}
TITLE_WORKERS = 3
AUTO_CLEAR_SEC = 5  # แถวที่เสร็จแล้วค้างให้เห็นกี่วินาทีก่อนล้างอัตโนมัติ

NAME_MAX = 70  # ความยาวชื่อไฟล์สูงสุด (ตัวอักษร ไม่รวมนามสกุล) ค่าเริ่มต้น

DEFAULTS = {
    "out_dir": os.path.join(APP_DIR, "PH"),
    "format": "อัตโนมัติ (เลือกที่ดีที่สุดให้)",
    "crf": 24,
    "preset": "slow",
    "container": "mp4",
    "aria2c": True,
    "cookies": "firefox",
    "update_on_start": True,
    "max_dl": 3,
    "max_conv": 1,
    "frags": 16,
    "auto_clear": True,
    "max_pages": 5,
    "name_max": NAME_MAX,
    "lang": "en",
    "resolution": "สูงสุด",
}

# สถานะ
WAIT, DL, WAIT_CONV, CONV, DONE, FAIL, STOPPED, HAVE = (
    "รอ", "กำลังโหลด", "รอแปลง", "กำลังแปลง", "เสร็จ", "ล้มเหลว", "หยุด", "มีแล้ว")

PROG_RE = re.compile(r"^\[P\]\s*([\d.]+)%\|(.*?)\|(.*?)(?:\|(\S*))?$")
DEAD_FRAGS = 8  # เจอ "ชิ้นไฟล์หาย 404" กี่ครั้งถึงจะเลิกรอแล้วเปลี่ยน server
STALL_SEC = 90       # ขนาดไฟล์ไม่เพิ่มเลยนานเท่านี้ = ค้าง ให้ตัดแล้วโหลดต่อจากเดิม
STALL_RETRIES = 5    # โหลดต่อจากที่ค้างได้กี่ครั้งต่อคลิป
DUR_RE = re.compile(r"Duration: (\d+):(\d+):([\d.]+)")
TIME_RE = re.compile(r"time=(\d+):(\d+):([\d.]+).*?speed=\s*([\d.]+x|N/A)")
# keycode ของปุ่มตัวอักษร ใช้แทน keysym ที่เพี้ยนตอนแป้นพิมพ์เป็นภาษาไทย
CTRL_KEYS = {86: "<<Paste>>", 67: "<<Copy>>", 88: "<<Cut>>", 65: "<<SelectAll>>"}


def load_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def save_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


def child_env():
    env = os.environ.copy()
    env["PATH"] = BIN_DIR + os.pathsep + env.get("PATH", "")
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    return env


UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")
B62 = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
PACKER_RE = re.compile(r"}\('(.*?)',\s*(\d+),\s*(\d+),\s*'(.*?)'\.split\('\|'\)", re.S)
MEDIA_RE = re.compile(r"""https?://[^\s"'<>\\]+?\.(?:m3u8|mp4)(?:\?[^\s"'<>\\]*)?""", re.I)


def is_missav(url):
    return re.match(r"https?://(?:[\w-]+\.)*missav[\w-]*\.", url, re.I) is not None


def is_7mm(url):
    return re.match(r"https?://(?:[\w-]+\.)*7mm[\w-]*\.", url, re.I) is not None


NO_YTDLP_HOSTS = set()  # เว็บที่ yt-dlp บอกว่าไม่รองรับ (จำไว้ ครั้งต่อไปอ่านหน้าเว็บเลย)


def short_url(url, keep=44):
    """ลิงก์แบบสั้นไว้โชว์ในตาราง (ดับเบิลคลิกยังคัดลอกลิงก์เต็มได้เหมือนเดิม)"""
    m = re.match(r"https?://(?:www\.|m\.)?([^/?#]+)([^?#]*)", url or "")
    if not m:
        return url
    host, path = m.group(1), m.group(2).rstrip("/")
    last = path.rsplit("/", 1)[-1] if path else ""
    short = f"{host}/…/{last}" if last and path.count("/") > 1 else f"{host}{path}"
    return short if len(short) <= keep else short[:keep - 1] + "…"


def url_host(url):
    m = re.match(r"https?://(?:www\.|m\.)?([^/?#]+)", url or "", re.I)
    return m.group(1).lower() if m else ""


def is_youtube(url):
    return bool(re.search(r"^https?://(?:[\w-]+\.)*(?:youtube\.com|youtu\.be)/", url or "", re.I))


def is_page_site(url):
    """เว็บที่ต้องอ่านหน้าเว็บเอง ไม่ส่งให้ yt-dlp ตรงๆ (yt-dlp ไม่รู้จัก หรืออ่านผิดเป็น playlist ขยะ)"""
    return is_missav(url) or is_7mm(url)


CHALLENGE_TITLES = ("just a moment", "attention required", "please wait", "checking your browser",
                    "เพียงสักครู่", "โปรดรอสักครู่")
BROWSER_DIR = os.path.join(APP_DIR, "_browser")
CHROME_PATHS = [
    os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
    os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
    os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
    os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
    os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
]
_chrome_lock = threading.Lock()  # profile เดียวกันเปิดพร้อมกันไม่ได้ เลยให้ใช้ทีละลิงก์


def is_challenge(page):
    if not page:
        return True
    m = re.search(r"<title[^>]*>(.*?)</title>", page, re.I | re.S)
    title = html.unescape(m.group(1)).strip().lower() if m else ""
    return "_cf_chl_opt" in page or any(t in title for t in CHALLENGE_TITLES)


WEB_TIMEOUT = 60  # บาง server (เช่น recordplay.biz) ตอบช้าถึง ~20 วินาที ต้องรอนานพอ ไม่งั้นตัดทิ้งก่อนเจ้าตัวจะตอบ


def fetch_page_simple(url, timeout=WEB_TIMEOUT):
    """ชั้น A: ปลอมตัวเป็น Chrome ด้วย curl_cffi ถ้าไม่มีค่อยใช้ urllib"""
    try:
        from curl_cffi import requests as cffi
        r = cffi.get(url, impersonate="chrome", timeout=timeout)
        return r.text if r.status_code == 200 else ""
    except ImportError:
        pass
    except Exception:
        return ""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode(r.headers.get_content_charset() or "utf-8", "replace")
    except Exception:
        return ""


def find_chrome():
    return next((p for p in CHROME_PATHS if os.path.isfile(p)), "")


def _chrome_ua(chrome):
    # headless Chrome ใส่คำว่า HeadlessChrome ใน UA ซึ่ง Cloudflare บล็อก เลยตั้ง UA ให้เหมือน Chrome ปกติ
    ver = "140"
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-Command",
                              f"(Get-Item '{chrome}').VersionInfo.ProductVersion"],
                             capture_output=True, text=True, creationflags=NO_WINDOW, timeout=15).stdout
        ver = out.strip().split(".")[0] or ver
    except (OSError, subprocess.SubprocessError):
        pass
    return (f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            f"(KHTML, like Gecko) Chrome/{ver}.0.0.0 Safari/537.36")


_ua_cache = {}


def fetch_page_chrome(url, visible=False, timeout=60, js=None):
    """ชั้น C: เปิด Chrome จริง (profile แยกของแอป) อ่านหน้าเว็บผ่าน DevTools แล้วปิด"""
    import socket
    import websocket

    chrome = find_chrome()
    if not chrome:
        return ""
    if chrome not in _ua_cache:
        _ua_cache[chrome] = _chrome_ua(chrome)
    with socket.socket() as sk:
        sk.bind(("127.0.0.1", 0))
        port = sk.getsockname()[1]
    args = [chrome, f"--user-data-dir={BROWSER_DIR}", f"--remote-debugging-port={port}",
            "--remote-allow-origins=*", "--no-first-run", "--no-default-browser-check",
            "--disable-blink-features=AutomationControlled", f"--user-agent={_ua_cache[chrome]}",
            "--window-size=1100,850"]
    if not visible:
        args += ["--headless=new", "--mute-audio"]
    args.append(url)
    proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                            creationflags=NO_WINDOW if not visible else 0)
    ws = None
    try:
        deadline = time.time() + 15
        ws_url = ""
        while time.time() < deadline and not ws_url:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=2) as r:
                    tabs = json.loads(r.read().decode())
                ws_url = next((t["webSocketDebuggerUrl"] for t in tabs
                               if t.get("type") == "page" and t.get("webSocketDebuggerUrl")), "")
            except Exception:
                time.sleep(0.3)
        if not ws_url:
            return ""
        ws = websocket.create_connection(ws_url, timeout=10, suppress_origin=True)
        msg_id = [0]

        def evaluate(expr):
            msg_id[0] += 1
            ws.send(json.dumps({"id": msg_id[0], "method": "Runtime.evaluate",
                                "params": {"expression": expr, "returnByValue": True}}))
            while True:
                res = json.loads(ws.recv())
                if res.get("id") == msg_id[0]:
                    return res.get("result", {}).get("result", {}).get("value")

        deadline = time.time() + timeout
        while time.time() < deadline:
            if proc.poll() is not None:  # ผู้ใช้ปิดหน้าต่างเอง
                return ""
            try:
                ready = evaluate("location.href.startsWith('http') && document.readyState === 'complete'"
                                 " && document.body && document.body.innerText.length > 0")
                page = evaluate("document.documentElement.outerHTML") if ready else ""
            except Exception:
                page = ""
            if page and not is_challenge(page):
                if not js:
                    return page
                try:
                    val = evaluate(js)  # ให้ JavaScript ของเว็บทำงานแล้วดึงผลออกมา (คืนค่าว่าง = ยังไม่พร้อม)
                except Exception:
                    val = None
                if val:
                    return val
            time.sleep(1)
        return ""
    except Exception:
        return ""
    finally:
        try:
            if ws:
                ws.close()
        except Exception:
            pass
        subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                       capture_output=True, creationflags=NO_WINDOW)


def fetch_page(url, timeout=WEB_TIMEOUT, notify=None):
    """อ่านหน้าเว็บแบบหลายชั้น: A. curl_cffi -> C. Chrome แบบซ่อน -> C. Chrome แบบเปิดหน้าต่างให้กดยืนยันเอง"""
    page = fetch_page_simple(url, timeout)
    if page and not is_challenge(page):
        return page
    if not find_chrome():
        if notify:
            notify("โดน Cloudflare บล็อก และไม่เจอ Chrome ในเครื่อง")
        return ""
    with _chrome_lock:
        if notify:
            notify("โดน Cloudflare บล็อก กำลังเปิด Chrome แบบซ่อนเพื่อผ่าน ...")
        page = fetch_page_chrome(url, visible=False, timeout=60)
        if page:
            return page
        if notify:
            notify("ต้องยืนยันตัวตน: กดยืนยันในหน้าต่าง Chrome ที่เด้งขึ้นมา (รอ 3 นาที)")
        return fetch_page_chrome(url, visible=True, timeout=180)


def page_title(page):
    m = (re.search(r"""<meta[^>]+property=["']og:title["'][^>]+content=["']([^"']+)""", page, re.I)
         or re.search(r"<title[^>]*>(.*?)</title>", page, re.I | re.S))
    return html.unescape(m.group(1)).strip() if m else ""


def unpack_js(page):
    """แกะ JavaScript ที่ถูกบีบด้วย eval(function(p,a,c,k,e,d)...) ซึ่งเว็บชอบใช้ซ่อนลิงก์วิดีโอ"""
    out = []
    for p, a, c, k in PACKER_RE.findall(page):
        a, words = int(a), k.split("|")
        p = p.replace("\\'", "'")

        def sub(m):
            n = 0
            for ch in m.group(0):
                v = B62.find(ch)
                if v < 0 or v >= a:
                    return m.group(0)
                n = n * a + v
            return words[n] if n < len(words) and words[n] else m.group(0)

        out.append(re.sub(r"\b\w+\b", sub, p))
    return "\n".join(out)


AD_HOSTS = re.compile(r"realsrv|whitetrafsa|labadena|tapioni|dtscout|exoclick|juicyads|trafficjunky|nettrck|"
                      r"doubleclick|googlesyndication|adsterra|popads|cloudflareinsights", re.I)
IFRAME_RE = re.compile(r"""<iframe[^>]+src=["']([^"']+)""", re.I)
# 7mmtv: กดปุ่มเลือก server ทุกปุ่มด้วย JavaScript ของเว็บเอง แล้วอ่าน iframe ของแต่ละ server
# รอจนหน้า player ตัวจริงโหลดเสร็จ (มีลิงก์วิดีโออยู่ในหน้า) แล้วส่งทั้ง URL และ HTML กลับมา
JS_EMBED_PAGE = r"""(function(){
  var h = document.documentElement.outerHTML;
  var dead = /no longer available|has been deleted|file was deleted|File not found/i.test(h);
  if (!dead && !/m3u8|\.mp4|links\s*=/.test(h)) return '';
  return JSON.stringify({u: location.href, h: h});
})()"""

# ข้อความที่ player ขึ้นเมื่อคลิปถูกลบหรือหมดอายุไปแล้ว
DEAD_RE = re.compile(r"no longer available|has been deleted|file was deleted|file not found", re.I)
# ชื่อหน้าเว็บที่บอกว่าหน้านี้ไม่มีแล้ว (ลิงก์ในหน้ารวมบางอันชี้ไปหน้าที่ถูกลบ)
GONE_TITLE_RE = re.compile(r"page not found|404 not found|not found\s*[-–|]|ไม่พบหน้า", re.I)

JS_7MM_SERVERS = r"""(function(){
  var btns=[...document.querySelectorAll('.btn-server')].map(b=>b.textContent.trim());
  if(!btns.length || typeof window['jfun_show_'+btns[0]]!=='function') return '';
  var out=[];
  for (const n of btns){
    try{ window['jfun_show_'+n](); }catch(e){ continue; }
    var f=[...document.querySelectorAll('iframe')].map(x=>x.src)
      .filter(s=>/^https?:/.test(s) && !/realsrv|whitetrafsa|labadena|tapioni|dtscout/.test(s));
    if(f.length) out.push([n,f[0]]);
  }
  return JSON.stringify(out);
})()"""


def fetch_with_referer(url, referer, timeout=WEB_TIMEOUT):
    try:
        from curl_cffi import requests as cffi
        r = cffi.get(url, impersonate="chrome", headers={"Referer": referer}, timeout=timeout)
        return r.text if r.status_code == 200 else ""
    except Exception:
        return ""


def resolve_embed(embed, referer, depth=0):
    """คืนค่า (ลิงก์วิดีโอตัวที่ควรใช้, หน้าที่ใช้เป็น referer)"""
    links, ref, _ = resolve_embed_links(embed, referer, depth)
    return (links[0] if links else ""), ref


def resolve_embed_links(embed, referer, depth=0):
    """เปิดหน้า player ของแต่ละ server หาลิงก์ m3u8/mp4 ถ้าไม่เจอให้ตาม iframe ที่ซ้อนอยู่ข้างในอีกชั้น
    คืนค่า ([ลิงก์วิดีโอ เรียงตัวที่ควรใช้ก่อน], หน้าที่ใช้เป็น referer, คลิปถูกลบไปแล้วหรือไม่)"""
    if embed.startswith("//"):
        embed = "https:" + embed
    page = fetch_with_referer(embed, referer)
    media = find_media_all(page, embed)
    if media:
        return media, embed, False
    if page and DEAD_RE.search(page):
        return [], embed, True
    if page and len(page) < 4000 and not IFRAME_RE.search(page) and find_chrome():
        # หน้าเปล่าๆ ที่ขึ้นว่า "Loading..." = ตัวเว็บใช้ JavaScript พาไปหน้า player จริง ให้ Chrome รันให้
        with _chrome_lock:
            raw = fetch_page_chrome(embed, visible=False, timeout=40, js=JS_EMBED_PAGE)
        try:
            data = json.loads(raw) if raw else None
        except ValueError:
            data = None
        if data and data.get("h"):
            media = find_media_all(data["h"], data.get("u") or embed)
            if media:
                return media, data.get("u") or embed, False
            if DEAD_RE.search(data["h"]):
                return [], data.get("u") or embed, True
    if depth < 2:
        for f in IFRAME_RE.findall(page):
            if f.startswith("//"):
                f = "https:" + f
            if f.startswith("http") and not AD_HOSTS.search(f):
                media, ref, dead = resolve_embed_links(f, embed, depth + 1)
                if media or dead:
                    return media, ref, dead
    return [], "", False


def get_servers(url, page, notify=None):
    """คืนค่า [(ชื่อ server, หน้า player)] ของหน้านี้"""
    if is_7mm(url):
        with _chrome_lock:
            if notify:
                notify("กำลังอ่านรายชื่อ server ด้วย Chrome ...")
            raw = fetch_page_chrome(url, visible=False, timeout=40, js=JS_7MM_SERVERS)
        try:
            return [tuple(x) for x in json.loads(raw)]
        except (ValueError, TypeError):
            return []
    out = []
    for i, f in enumerate(IFRAME_RE.findall(page)):
        if f.startswith("//"):
            f = "https:" + f
        if f.startswith("http") and not AD_HOSTS.search(f):
            out.append((f"iframe{i + 1}", f))
    return out


def probe_quality(media, referer, limit=0):
    """ถาม yt-dlp ว่าลิงก์นี้ได้ความละเอียด/bitrate สูงสุดเท่าไหร่ คืนค่า (สูง, bitrate) หรือ None ถ้าใช้ไม่ได้"""
    origin = re.match(r"https?://[^/]+", referer).group(0)
    args = [YTDLP, "-J", "--no-warnings", "--encoding", "utf-8", "--impersonate", "chrome",
            "--referer", referer, "--add-headers", f"Origin:{origin}", media]
    try:
        r = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           env=child_env(), creationflags=NO_WINDOW, timeout=60)
        info = json.loads(r.stdout) if r.returncode == 0 else None
    except (OSError, subprocess.SubprocessError, ValueError):
        info = None
    if not info:
        return None
    fmts = info.get("formats") or [info]
    qs = [(f.get("height") or 0, f.get("tbr") or 0) for f in fmts]
    if limit:
        # เอาตัวที่ชัดที่สุดที่ไม่เกินที่ตั้งไว้ ถ้าไม่มีเลยเอาตัวที่ใกล้ที่สุด (เล็กสุดที่เกิน)
        within = [q for q in qs if q[0] <= limit]
        return max(within) if within else min(qs, default=(0, 0))
    return max(qs, default=(0, 0))


# ---------- แกะลิงก์คลิปจากหน้ารวม (ค้นหา / หมวด / tag / นักแสดง / ช่อง) ----------
LISTING_PATH = re.compile(r"/(search|tag|tags|category|categories|genre|genres|actress|actresses|actor|actors|"
                          r"performer|performers|idol|idols|cast|star|stars|"
                          r"model|models|pornstar|pornstars|channel|channels|studio|studios|maker|makers|"
                          r"series|playlist|playlists|user|users|videos|page)(/|$)", re.I)
NAV_PATH = re.compile(r"/(category|categories|tag|tags|page|author|feed|wp-[\w-]+|dmca|2257[\w-]*|contact[\w-]*|"
                      r"about[\w-]*|privacy[\w-]*|terms[\w-]*|login|register|signup|search|genres?|actress(es)?|"
                      r"actors?|performers?|idols?|cast|"
                      r"stars?|models?|pornstars?|channels?|studios?|makers?|series|faq|help|upload|premium)(/|$)", re.I)
MAX_LISTING_PAGES = 5
MAX_LISTING_LINKS = 1000


def is_listing_url(url):
    """ลิงก์นี้น่าจะเป็นหน้ารวมหลายคลิป (ไม่ใช่หน้าคลิปเดียว)"""
    u = urlparse(url)
    q = parse_qs(u.query)
    if any(k in q for k in ("s", "q", "search", "search_query", "k", "keyword", "query")):
        return True
    if re.search(r"youtube\.com/(@|channel/|c/|user/|playlist)", url, re.I):
        return True
    return bool(LISTING_PATH.search(u.path))


def _path_shape(path):
    parts = [x for x in path.strip("/").split("/") if x]
    return "/".join("9" if x.isdigit() else "x" for x in parts)


def listing_links(page, base):
    """หาลิงก์คลิปในหน้ารวม: เอาลิงก์ในเว็บเดียวกันที่รูปแบบ path เหมือนกันและมีมากที่สุด"""
    host = urlparse(base).netloc.lower().removeprefix("www.")
    seen, links = set(), []
    for h in re.findall(r"""<a[^>]+href=["']([^"'#]+)""", page, re.I):
        h = urljoin(base, html.unescape(h).strip())
        pu = urlparse(h)
        if pu.scheme not in ("http", "https") or pu.netloc.lower().removeprefix("www.") != host:
            continue
        if pu.query or NAV_PATH.search(pu.path) or pu.path.strip("/") == "":
            continue
        key = pu.path.rstrip("/")
        if key in seen or h.rstrip("/") == base.split("?")[0].rstrip("/"):
            continue
        seen.add(key)
        links.append(h)
    groups = {}
    for h in links:
        groups.setdefault(_path_shape(urlparse(h).path), []).append(h)
    groups = {k: v for k, v in groups.items() if len(v) >= 2 and k}
    if not groups:
        return []
    return max(groups.items(), key=lambda kv: (len(kv[1]), kv[0].count("/")))[1]


def next_page_url(page, base):
    m = (re.search(r"""<link[^>]+rel=["']next["'][^>]+href=["']([^"']+)""", page, re.I)
         or re.search(r"""<a[^>]+rel=["']next["'][^>]+href=["']([^"']+)""", page, re.I)
         or re.search(r"""<a[^>]+class=["'][^"']*\bnext\b[^"']*["'][^>]+href=["']([^"']+)""", page, re.I)
         or re.search(r"""<a[^>]+href=["']([^"']+)["'][^>]+class=["'][^"']*\bnext\b""", page, re.I))
    if m:
        return urljoin(base, html.unescape(m.group(1)))
    # ไม่มีลิงก์ "ถัดไป" ตรงๆ: หาลิงก์เลขหน้า (/page/N/, ?page=N, ?paged=N) ที่เป็นหน้าถัดจากหน้านี้
    num = re.compile(r"(?:/page/|[?&](?:page|paged|pg)=)(\d+)", re.I)
    cur = num.search(base)
    want = (int(cur.group(1)) if cur else 1) + 1
    host = urlparse(base).netloc
    for h in re.findall(r"""<a[^>]+href=["']([^"'#]+)""", page, re.I):
        h = urljoin(base, html.unescape(h))
        m = num.search(h)
        if m and int(m.group(1)) == want and urlparse(h).netloc == host:
            return h
    return ""


def listing_folder(url):
    """ตั้งชื่อโฟลเดอร์จากลิงก์หน้ารวม: ใช้คำค้นก่อน ถ้าไม่มีใช้ท้าย path (เช่น /actress/ririsu-amano/)"""
    u = urlparse(url)
    q = parse_qs(u.query)
    for k in ("s", "q", "search", "search_query", "k", "keyword", "query"):
        if q.get(k) and q[k][0].strip():
            return safe_filename(q[k][0].strip()).replace("%%", "%")
    parts = [x for x in u.path.strip("/").split("/")
             if x and not x.isdigit() and not LISTING_PATH.search("/" + x + "/")
             and x.lower() not in ("en", "th", "ja", "cn", "zh", "ko", "dm", "videos", "page")]
    name = (parts[-1] if parts else u.netloc).replace("-", " ").replace("_", " ")
    return safe_filename(urllib.parse.unquote(name)).replace("%%", "%") or "listing"


def expand_listing(url, notify=None, stop=lambda: False, max_pages=MAX_LISTING_PAGES):
    """แกะลิงก์คลิปทั้งหมดจากหน้ารวม คืน list ลิงก์ (ว่าง = แกะไม่ได้)"""
    # 1) เว็บที่ yt-dlp รู้จัก (YouTube channel/playlist, pornhub model ฯลฯ) ให้ yt-dlp แกะเอง
    if notify:
        notify("กำลังถาม yt-dlp ว่ามีคลิปอะไรบ้าง ...")
    try:
        r = subprocess.run([YTDLP, "--flat-playlist", "--no-warnings", "--encoding", "utf-8",
                            "--playlist-end", str(MAX_LISTING_LINKS), "--print", "%(extractor)s\t%(url)s", url],
                           capture_output=True, text=True, encoding="utf-8", errors="replace",
                           env=child_env(), creationflags=NO_WINDOW, timeout=120)
        rows = [l.split("\t", 1) for l in r.stdout.splitlines() if "\t" in l]
        urls = [u for ex, u in rows if u.startswith("http") and not ex.lower().startswith("generic")]
        if len(urls) >= 2:
            return list(dict.fromkeys(urls))
    except (OSError, subprocess.SubprocessError):
        pass
    # 2) อ่านหน้าเว็บเอง ตามหน้าถัดไปได้ MAX_LISTING_PAGES หน้า
    out, page_url = [], url
    for n in range(max_pages):
        if stop() or not page_url:
            break
        if notify:
            notify(f"กำลังอ่านหน้า {n + 1}/{max_pages} ... (ได้แล้ว {len(out)} ลิงก์)")
        page = fetch_page(page_url, notify=notify)
        found = listing_links(page, page_url)
        new = [u for u in found if u not in out]
        if not new:
            break
        out += new
        if len(out) >= MAX_LISTING_LINKS:
            break
        nxt = next_page_url(page, page_url)
        page_url = nxt if nxt and nxt != page_url else ""
    return out[:MAX_LISTING_LINKS]


# ตัวเล่นวิดีโอบางเจ้า (jwplayer) เก็บลิงก์ไว้หลายตัวใน links = {"hls2":..,"hls3":..,"hls4":..}
# แล้วเล่นจาก hls4 ก่อน ตัวท้ายๆ เร็วกว่าตัวแรกมาก (hls2 มักโดนจำกัดความเร็ว sp=500)
LINKS_RE = re.compile(r"""links\s*=\s*(\{[^{}]{0,4000}?\})""")


def player_links(text, base=""):
    """ลิงก์จาก links = {...} ของ player เรียงตัวที่เร็วที่สุดก่อน (hls4 > hls3 > hls2)"""
    out = []
    for m in LINKS_RE.finditer(text):
        try:
            d = json.loads(m.group(1))
        except ValueError:
            continue
        for k in sorted(d, key=lambda k: (-int(re.sub(r"\D", "", k) or 0), k)):
            u = d[k]
            if not isinstance(u, str) or not u.strip():
                continue
            u = urllib.parse.urljoin(base, u) if base else u
            if u.startswith("http") and u not in out:
                out.append(u)
    return out


def find_media_all(page, base=""):
    """ลิงก์วิดีโอทุกตัวที่เจอในหน้า เรียงตัวที่ควรใช้ก่อน (ลิงก์ของ player ก่อน แล้วค่อยลิงก์อื่นในหน้า)"""
    text = (page + "\n" + unpack_js(page)).replace("\\/", "/")
    out = []
    for u in player_links(text, base):
        # .txt คือ m3u8 ที่เปลี่ยนนามสกุล บาง server ใช้กันโดนบล็อก
        if re.search(r"\.(m3u8|mp4|txt)(\?|$)", u, re.I) and u not in out:
            out.append(u)
    urls = list(dict.fromkeys(MEDIA_RE.findall(text)))
    urls = [u for u in urls if not re.search(r"preview|thumb|trailer|sample", u, re.I)]
    for good in (r"(playlist|master)\.m3u8", r"\.m3u8", r"\.mp4"):
        for u in urls:
            if re.search(good, u, re.I) and u not in out:
                out.append(u)
    return out


def find_media(page, base=""):
    links = find_media_all(page, base)
    return links[0] if links else ""


OLD_ARCHIVE = os.path.join(APP_DIR, "downloaded.txt")  # ไฟล์ประวัติของเวอร์ชันเก่า (เลิกใช้แล้ว ลบทิ้งตอนเปิดแอป)
# ไฟล์ไหนโหลดมาจากลิงก์ไหน (ไว้แยกคลิปคนละอันที่ชื่อเหมือนกัน) {url_key: path ไม่มีนามสกุล}
SOURCES_FILE = os.path.join(APP_DIR, "sources.json")
SOURCES = {}
_names_lock = threading.Lock()
_reserved = {}  # id คลิปที่กำลังโหลด -> ชื่อไฟล์ที่จองไว้ (กันโหลดพร้อมกันแล้วชื่อชนกัน)


def clean_name(name, limit=150):
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', " ", name)
    return re.sub(r"\s+", " ", name).strip(" .")[:limit].rstrip(" .")


def safe_filename(name, limit=150):
    return clean_name(name, limit).replace("%", "%%")


def stem_key(path):
    return os.path.normcase(os.path.splitext(os.path.abspath(path))[0])


def owner_of(path):
    """ลิงก์ (url_key) ที่ไฟล์นี้โหลดมา หรือ None ถ้าไม่รู้ (ไฟล์เก่า/ไฟล์ที่ไม่ได้โหลดด้วยแอปนี้)"""
    k = stem_key(path)
    return next((u for u, v in list(SOURCES.items()) if v == k), None)


def remember_source(url, path):
    if url and path:
        SOURCES[url_key(url)] = stem_key(path)
        save_json(SOURCES_FILE, SOURCES)


def pick_name(item_id, folder, title, url, limit):
    """ชื่อไฟล์ (ยังไม่ escape %) ที่ไม่ชนกับคลิปอื่น: ชื่อเดียวกันแต่คนละลิงก์ จะได้ "ชื่อ (2)", "ชื่อ (3)" ...
    ไฟล์ที่เป็นของลิงก์นี้เองใช้ชื่อเดิมได้ (โหลดซ้ำ = เขียนทับ)"""
    key = url_key(url)
    base = clean_name(title, limit) or "video"
    try:
        names = [f for f in os.listdir(folder) if f.lower().endswith(VIDEO_EXTS)]
    except OSError:
        names = []
    with _names_lock:
        for n in range(1, 1000):
            suffix = f" ({n})" if n > 1 else ""
            cand = clean_name(base[:max(1, limit - len(suffix))], limit) + suffix
            ck = stem_key(os.path.join(folder, cand))
            if any(v == ck for i, v in _reserved.items() if i != item_id):
                continue
            if any(stem_key(os.path.join(folder, f)) == ck and owner_of(os.path.join(folder, f)) != key
                   for f in names):
                continue
            _reserved[item_id] = ck
            return cand
    return base


def release_name(item_id):
    with _names_lock:
        _reserved.pop(item_id, None)


def default_outtmpl(limit):
    """ชื่อไฟล์ = ชื่อเรื่องอย่างเดียว ไม่เกิน limit ตัวอักษร (ไม่นับนามสกุล) ไม่ใส่รหัสคลิป"""
    return f"%(title).{max(10, limit)}s.%(ext)s"


# คุณภาพต่อขนาดไฟล์ของแต่ละตัว (มากกว่า = ดีกว่า) ใช้ตัดสินเมื่อความเร็วผ่านเกณฑ์แล้ว
QUALITY_RANK = {"hevc_nvenc": 3, "hevc_qsv": 2, "hevc_amf": 1, "libx265": 0}
MIN_FPS = 60  # ต้องแปลง 1080p ได้เร็วกว่านี้ถึงจะนับว่า "เร็วพอ"
BENCH_FRAMES = {"libx265": (8, 32)}  # CPU ช้า ใช้เฟรมน้อยพอ
BENCH_FRAMES_GPU = (30, 300)


def _bench_time(name, frames, q, preset):
    _, vargs = encode_args(name, q, preset)
    args = [FFMPEG, "-hide_banner", "-loglevel", "error", "-f", "lavfi",
            "-i", "testsrc2=size=1920x1080:rate=30", "-frames:v", str(frames),
            "-pix_fmt", "yuv420p", *vargs, "-f", "null", "-"]
    t = time.perf_counter()
    r = subprocess.run(args, capture_output=True, creationflags=NO_WINDOW, timeout=120)
    return time.perf_counter() - t if r.returncode == 0 else None


def benchmark_encoders(q=24, preset="medium"):
    """แปลงภาพทดสอบ 1080p ด้วยทุกตัว คืนค่า [(ชื่อ, fps), ...] เฉพาะตัวที่ใช้ได้
    รัน 2 รอบ (สั้น/ยาว) แล้วเอาส่วนต่าง จะได้ไม่นับเวลาเปิดการ์ดจอ"""
    results = []
    for name, enc in ENCODERS.items():
        n1, n2 = BENCH_FRAMES.get(enc, BENCH_FRAMES_GPU)
        try:
            t1 = _bench_time(name, n1, q, preset)
            t2 = _bench_time(name, n2, q, preset) if t1 is not None else None
        except (OSError, subprocess.SubprocessError):
            t1 = t2 = None
        if t1 is not None and t2 is not None:
            # ส่วนต่างเวลาสั้นเกินไปจะวัดเพี้ยน เลยใช้เวลารวมของรอบยาวแทน
            fps = (n2 - n1) / (t2 - t1) if t2 - t1 > 0.3 else n2 / t2
            results.append((name, min(fps, n2 / max(t2 * 0.2, 1e-3))))
    if not any(n == CPU_ENC for n, _ in results):
        results.append((CPU_ENC, 0.0))
    return results


def pick_best(results):
    fast = [r for r in results if r[1] >= MIN_FPS]
    if fast:
        return max(fast, key=lambda r: (QUALITY_RANK[ENCODERS[r[0]]], r[1]))[0]
    return max(results, key=lambda r: r[1])[0]


def enc_label(name, fps):
    return f"{name} · {fps:.0f} fps" if fps else name


def enc_name(label):
    return label.split(" · ")[0] if label else CPU_ENC


def encode_args(enc_name, q, preset):
    """คืนค่า (args ก่อน -i, args ฝั่งวิดีโอ)"""
    enc = ENCODERS.get(enc_name, "libx265")
    q = str(q)
    if enc == "hevc_nvenc":
        return (["-hwaccel", "cuda"],
                ["-c:v", enc, "-preset", NV_PRESET.get(preset, "p5"), "-tune", "hq", "-rc", "vbr",
                 "-cq", q, "-b:v", "0", "-spatial-aq", "1", "-temporal-aq", "1", "-rc-lookahead", "32"])
    if enc == "hevc_amf":
        return ([], ["-c:v", enc, "-quality", AMF_QUALITY.get(preset, "balanced"), "-rc", "cqp",
                     "-qp_i", q, "-qp_p", q])
    if enc == "hevc_qsv":
        return ([], ["-c:v", enc, "-preset", QSV_PRESET.get(preset, "medium"), "-global_quality", q])
    return ([], ["-c:v", "libx265", "-crf", q, "-preset", preset, "-x265-params", "log-level=error"])


VIDEO_EXTS = (".mp4", ".mkv", ".webm", ".m4v", ".mov", ".ts", ".flv", ".avi")


def url_key(url):
    """แปลงลิงก์เป็นรหัสคลิป ให้ลิงก์ที่ต่างกันแต่เป็นคลิปเดียวกันได้รหัสเดียวกัน"""
    u = url.strip()
    m = re.search(r"pornhub[\w-]*\.\w+/.*[?&]viewkey=([\w-]+)", u, re.I)
    if m:
        return "ph:" + m.group(1).lower()
    m = (re.search(r"(?:youtube\.com/(?:watch\?(?:.*&)?v=|shorts/|live/|embed/)|youtu\.be/)([\w-]{11})", u, re.I))
    if m:
        return "yt:" + m.group(1)
    if is_missav(u):  # mirror หลายโดเมน หลายภาษา แต่ท้ายลิงก์คือรหัสคลิปเดียวกัน
        return "missav:" + u.split("?")[0].rstrip("/").rsplit("/", 1)[-1].lower()
    m = re.search(r"7mm[\w-]*\.\w+/.*?/(\d+)/", u, re.I)
    if m:
        return "7mm:" + m.group(1)
    m = re.match(r"https?://(?:www\.|m\.)?([^/?#]+)([^?#]*)(\?[^#]*)?", u, re.I)
    if not m:
        return u.lower()
    q = "&".join(sorted(x for x in (m.group(3) or "?")[1:].split("&")
                        if x and not re.match(r"(utm_|fbclid|gclid|si=|feature=|t=)", x)))
    return f"{m.group(1).lower()}{m.group(2).rstrip('/')}" + (f"?{q}" if q else "")


def norm_name(text):
    """ตัดสัญลักษณ์ออก เหลือแต่ตัวอักษร/ตัวเลข (รวมภาษาไทย) ไว้เทียบชื่อ"""
    return re.sub(r"[\W_]+", "", text.lower())


def find_existing(folder, title, url=""):
    """หาไฟล์วิดีโอในโฟลเดอร์ที่น่าจะเป็นคลิปเดียวกัน (เทียบชื่อ หรือรหัสคลิปในวงเล็บ [..]) คืน path หรือ ''"""
    try:
        names = [n for n in os.listdir(folder) if n.lower().endswith(VIDEO_EXTS) and ".h265-tmp." not in n]
    except OSError:
        return ""
    ukey = url_key(url) if url else ""
    key = ukey.split(":", 1)[-1]
    mine = SOURCES.get(ukey)
    nt = norm_name(title) if title else ""
    for n in names:
        path = os.path.join(folder, n)
        if mine and stem_key(path) == mine:  # ไฟล์ที่โหลดจากลิงก์นี้เอง
            return path
        stem = os.path.splitext(n)[0]
        m = re.search(r"\[([\w-]+)\]$", stem)
        if m and key and m.group(1).lower() == key.lower():
            return path
        if not nt:
            continue
        owner = owner_of(path)
        if owner and owner != ukey:  # ชื่อเหมือนกัน แต่เป็นคลิปจากลิงก์อื่น
            continue
        ns = norm_name(re.sub(r"\s*\[[\w-]+\]$", "", stem))
        # yt-dlp ตัดชื่อยาวให้สั้นลง เลยยอมให้ขึ้นต้นตรงกันถ้ายาวพอ
        if ns and (ns == nt or (min(len(ns), len(nt)) >= 30 and (ns.startswith(nt) or nt.startswith(ns)))):
            return os.path.join(folder, n)
    return ""


def find_moved_url(url):
    """หน้าคลิปขึ้น 404 เพราะเว็บย้ายวันที่ใน URL (ลงคลิปเดิมใหม่) ลองค้นชื่อคลิปในเว็บนั้นเพื่อหา URL ใหม่"""
    m = re.match(r"(https?://[^/]+)/\d{4}/\d{2}/\d{2}/([^/?#]+)/?$", url)
    if not m:
        return ""
    root, slug = m.group(1), m.group(2)
    page = fetch_page(f"{root}/?s={urllib.parse.quote(slug)}")
    if not page:
        return ""
    same = re.compile(rf"{re.escape(root)}/\d{{4}}/\d{{2}}/\d{{2}}/{re.escape(slug)}/?$", re.I)
    for link in dict.fromkeys(re.findall(r'https?://[^\s"\'<>]+', page)):
        link = link.rstrip('"\'')
        if same.match(link) and link.rstrip("/") != url.rstrip("/"):
            return link
    return ""


NO_MEDIA = -2  # หาลิงก์วิดีโอไม่เจอ
DEAD_CLIP = -3  # เว็บบอกเองว่าคลิปถูกลบหรือหมดอายุแล้ว
PAGE_GONE = -4  # หน้าคลิปบนเว็บถูกลบไปแล้ว (404)


def fail_reason(out):
    """สรุปสาเหตุจาก output ของ yt-dlp ให้อ่านง่าย"""
    m = re.search(r"HTTP Error (\d+)", out)
    if m:
        return f"HTTP {m.group(1)}"
    for key, msg in (("stalled", "ค้างหลายรอบ ลองใหม่ทีหลัง"), ("Unsupported URL", "เว็บไม่รองรับ"),
                     ("Requested format is not available", "ไม่มีรูปแบบที่เลือก"),
                     ("Operation too slow", "เซิร์ฟเวอร์ตอบช้ามาก"), ("fragment 1 not found", "ไฟล์หายจากเซิร์ฟเวอร์"),
                     ("Private video", "คลิปส่วนตัว"), ("Sign in", "ต้องล็อกอิน"), ("timed out", "หมดเวลา"),
                     ("could not copy", "อ่าน cookie ไม่ได้"), ("cookie database", "อ่าน cookie ไม่ได้")):
        if key.lower() in out.lower():
            return msg
    return ""


def parse_version(v):
    """'v1.2.3' -> (1, 2, 3) ไว้เทียบว่าใหม่กว่าไหม"""
    return tuple(int(x) for x in re.findall(r"\d+", v)[:3]) or (0,)


def github_token(owner_only=False):
    """ยืม token ที่ git จำไว้ (Git Credential Manager) ใช้เฉพาะตอน repo เป็น private ไม่เด้งหน้าต่างถามรหัส"""
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")
    # ลองระบุชื่อเจ้าของ repo ก่อน (เครื่องที่จำไว้หลายบัญชีจะถามว่าใช้บัญชีไหน ถ้าไม่ระบุ)
    for user in (GITHUB_REPO.split("/")[0],) + (() if owner_only else ("",)):
        q = "protocol=https\nhost=github.com\n" + (f"username={user}\n" if user else "") + "\n"
        try:
            r = subprocess.run(["git", "credential", "fill"], input=q, capture_output=True, text=True,
                               env=env, creationflags=NO_WINDOW, timeout=15)
        except (OSError, subprocess.SubprocessError):
            continue
        m = re.search(r"^password=(.+)$", r.stdout, re.M)
        if m:
            return m.group(1).strip()
    return ""


_rate_token = {"t": None}


def github_get(url, token="", accept="application/vnd.github+json", timeout=30):
    headers = {"User-Agent": f"{APP_NAME}/{APP_VERSION}", "Accept": accept}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=timeout) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        # ไม่ได้ล็อกอิน GitHub จำกัด 60 ครั้ง/ชม. ต่อ IP ถ้าหมด ลองใหม่ด้วยบัญชีที่ git จำไว้ในเครื่อง (ถ้ามี)
        if token or e.code not in (403, 429) or "api.github.com" not in url:
            raise
        if _rate_token["t"] is None:
            _rate_token["t"] = github_token()
        if not _rate_token["t"]:
            raise
        return github_get(url, _rate_token["t"], accept, timeout)


def latest_release():
    """คืน (tag, ลิงก์ asset YtdlpGUI.exe, token ที่ต้องใช้) หรือ None ถ้าเช็คไม่ได้"""
    api = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    token = ""
    try:
        data = json.loads(github_get(api))
    except urllib.error.HTTPError as e:
        if e.code not in (401, 403, 404):  # 404 = repo เป็น private ต้องใช้ token
            return None
        token = github_token()
        if not token:
            return None
        try:
            data = json.loads(github_get(api, token))
        except Exception:
            return None
    except Exception:
        return None
    asset = next((a for a in data.get("assets", []) if a.get("name", "").lower() == "ytdlpgui.exe"), None)
    if not asset:
        return None
    return data.get("tag_name", ""), asset["url"], token


def download_update(asset_url, token, dest):
    blob = github_get(asset_url, token, accept="application/octet-stream", timeout=300)
    if len(blob) < 1_000_000 or blob[:2] != b"MZ":  # ต้องเป็นไฟล์ exe จริง
        raise ValueError("ไฟล์ที่โหลดมาไม่ใช่ exe")
    with open(dest, "wb") as f:
        f.write(blob)


# ---------- อัปเดตเครื่องมือใน bin\ ทุกครั้งที่เปิดแอป ----------
TOOLS = {
    # ชื่อ: (repo บน GitHub, ชื่อไฟล์ asset (regex), ไฟล์ที่ต้องดึงออกจาก zip, คำสั่งดูเวอร์ชัน, regex เวอร์ชัน)
    "yt-dlp": ("yt-dlp/yt-dlp", r"^yt-dlp\.exe$", None, ["--version"], r"(\d{4}\.\d{2}\.\d{2}(?:\.\d+)?)"),
    "ffmpeg": ("yt-dlp/FFmpeg-Builds", r"^ffmpeg-master-latest-win64-gpl\.zip$", ("ffmpeg.exe", "ffprobe.exe"),
               ["-hide_banner", "-version"], r"(\d{4})-?(\d{2})-?(\d{2})"),
    "deno": ("denoland/deno", r"^deno-x86_64-pc-windows-msvc\.zip$", ("deno.exe",), ["--version"], r"deno (\d+\.\d+\.\d+)"),
    "aria2c": ("aria2/aria2", r"win-64bit.*\.zip$", ("aria2c.exe",), ["--version"], r"aria2 version (\d+\.\d+\.\d+)"),
}


def local_tool_version(name):
    exe = os.path.join(BIN_DIR, f"{name}.exe")
    if not os.path.isfile(exe):
        return None
    try:
        out = subprocess.run([exe, *TOOLS[name][3]], capture_output=True, text=True, errors="replace",
                             creationflags=NO_WINDOW, timeout=30).stdout
    except (OSError, subprocess.SubprocessError):
        return ""
    m = re.search(TOOLS[name][4], out)
    if not m:
        return ""
    return "-".join(m.groups()) if name == "ffmpeg" else m.group(1)


def remote_tool(name):
    """คืน (เวอร์ชันล่าสุด, ลิงก์ asset) จาก GitHub Releases"""
    repo, pattern = TOOLS[name][0], TOOLS[name][1]
    url = f"https://api.github.com/repos/{repo}/releases/" + ("tags/latest" if name == "ffmpeg" else "latest")
    data = json.loads(github_get(url))
    asset = next((a for a in data.get("assets", []) if re.search(pattern, a["name"])), None)
    if not asset:
        return None, None
    if name == "ffmpeg":  # build รายวัน ใช้วันที่ของไฟล์เป็นเวอร์ชัน
        ver = asset["updated_at"][:10]
    else:
        ver = re.sub(r"^[^\d]*", "", data.get("tag_name", ""))
    return ver, asset["browser_download_url"]


def tool_is_newer(name, remote, local):
    if not local:
        return True
    if name == "ffmpeg":
        return remote.replace("-", "") > local.replace("-", "")
    return parse_version(remote) > parse_version(local)


def download_file(url, dest, progress=None):
    req = urllib.request.Request(url, headers={"User-Agent": f"{APP_NAME}/{APP_VERSION}"})
    with urllib.request.urlopen(req, timeout=60) as r, open(dest, "wb") as f:
        total = int(r.headers.get("Content-Length") or 0)
        got = 0
        while True:
            chunk = r.read(1 << 20)
            if not chunk:
                break
            f.write(chunk)
            got += len(chunk)
            if progress and total:
                progress(got * 100 // total)


def update_tool(name, url, progress=None):
    """โหลดเครื่องมือตัวใหม่มาไว้ใน _tmp ก่อน แล้วค่อยสลับเข้า bin\\ (ถ้าโหลดพังกลางทาง ตัวเดิมยังอยู่)"""
    os.makedirs(TMP_DIR, exist_ok=True)
    os.makedirs(BIN_DIR, exist_ok=True)
    tmp = os.path.join(TMP_DIR, os.path.basename(urlparse(url).path))
    download_file(url, tmp, progress)
    members = TOOLS[name][2]
    try:
        if not members:  # ไฟล์ exe ตรงๆ (yt-dlp)
            os.replace(tmp, os.path.join(BIN_DIR, f"{name}.exe"))
            return
        import zipfile
        with zipfile.ZipFile(tmp) as z:
            for want in members:
                src = next((n for n in z.namelist() if n.replace("\\", "/").split("/")[-1].lower() == want), None)
                if not src:
                    raise ValueError(f"ไม่เจอ {want} ในไฟล์ zip")
                part = os.path.join(TMP_DIR, want + ".new")
                with z.open(src) as a, open(part, "wb") as b:
                    b.write(a.read())
                os.replace(part, os.path.join(BIN_DIR, want))
    finally:
        try:
            os.remove(tmp)
        except OSError:
            pass


# ---------- ไอคอนสถานะ (System Tray + ไอคอนหน้าต่าง) ----------
TRAY_COLORS = {"wait": (242, 181, 12), "busy": (37, 116, 235), "done": (33, 158, 84), "idle": (120, 128, 140)}


def make_status_icon(color, size=64):
    """วงกลมสี + ลูกศรลงสีขาว"""
    from PIL import Image, ImageDraw
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse((2, 2, size - 3, size - 3), fill=color + (255,))
    c, w = size / 2, size * 0.11
    d.rectangle((c - w, size * 0.2, c + w, size * 0.55), fill="white")
    d.polygon([(size * 0.26, size * 0.5), (size * 0.74, size * 0.5), (c, size * 0.8)], fill="white")
    return img


class TrVar(tk.StringVar):
    """StringVar ที่แปลภาษาให้ทุกครั้งที่ set"""

    def set(self, value):
        super().set(tr(value))


def from_display(value, keys):
    """ค่าที่โชว์ใน dropdown (แปลแล้ว) -> key เดิมที่โค้ดใช้"""
    return next((k for k in keys if value in (k, tr(k))), value)


# ---------- Error log: เขียนลงไฟล์เฉพาะตอนมี error แล้ว push ขึ้น repo private ----------
LOG_DIR = os.path.join(APP_DIR, "logs")
_log_lock = threading.Lock()


def _sanitize(text):
    """ซ่อนชื่อผู้ใช้ Windows ใน path"""
    home = os.path.expanduser("~")
    return text.replace(home, "~").replace(home.replace("\\", "/"), "~") if home else text


def log_error(kind, message, detail="", url=""):
    """เขียน error 1 รายการลง logs/errors-YYYY-MM-DD.log (ไม่เขียนอย่างอื่นลงไฟล์)"""
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    block = [f"===== {stamp} | v{APP_VERSION} | {kind}", f"message: {message}"]
    if url:
        block.append(f"url: {url}")
    if detail:
        block.append("detail:\n" + "\n".join("    " + l for l in detail.strip().splitlines()[-60:]))
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        with _log_lock, open(os.path.join(LOG_DIR, f"errors-{time.strftime('%Y-%m-%d')}.log"), "a",
                             encoding="utf-8") as f:
            f.write(_sanitize("\n".join(block)) + "\n\n")
    except OSError:
        pass


def upload_error_logs():
    """push ไฟล์ error log ที่มีการเปลี่ยนแปลงขึ้น LOGS_REPO (ใช้บัญชีเจ้าของเท่านั้น เครื่องอื่นจะข้ามไปเฉยๆ)
    คืนจำนวนไฟล์ที่อัปโหลด หรือ None ถ้าไม่มีสิทธิ์/ไม่ได้อัป"""
    import base64
    import hashlib
    try:
        files = sorted(f for f in os.listdir(LOG_DIR) if f.startswith("errors-") and f.endswith(".log"))
    except OSError:
        return 0
    state_file = os.path.join(LOG_DIR, ".uploaded.json")
    state = load_json(state_file, {})
    todo = []
    for f in files:
        data = open(os.path.join(LOG_DIR, f), "rb").read()
        h = hashlib.sha1(data).hexdigest()
        if state.get(f) != h:
            todo.append((f, data, h))
    if not todo:
        return 0
    token = github_token(owner_only=True)
    if not token:
        return None
    machine = re.sub(r"[^\w.-]", "_", os.environ.get("COMPUTERNAME", "pc"))
    done = 0
    for f, data, h in todo:
        api = f"https://api.github.com/repos/{LOGS_REPO}/contents/logs/{machine}/{f}"
        headers = {"User-Agent": f"{APP_NAME}/{APP_VERSION}", "Accept": "application/vnd.github+json",
                   "Authorization": f"Bearer {token}"}
        sha = None
        try:
            with urllib.request.urlopen(urllib.request.Request(api, headers=headers), timeout=20) as r:
                sha = json.loads(r.read()).get("sha")
        except urllib.error.HTTPError as e:
            if e.code != 404:
                return None if e.code in (401, 403) else done
        except Exception:
            return done
        body = {"message": f"error log {machine} {f}", "content": base64.b64encode(data).decode()}
        if sha:
            body["sha"] = sha
        try:
            req = urllib.request.Request(api, data=json.dumps(body).encode(), headers=headers, method="PUT")
            with urllib.request.urlopen(req, timeout=30):
                pass
        except urllib.error.HTTPError as e:
            return None if e.code in (401, 403, 404) else done
        except Exception:
            return done
        state[f] = h
        done += 1
    save_json(state_file, state)
    return done


# ---------- รับลิงก์จาก Chrome Extension (เฉพาะในเครื่องนี้) ----------
EXT_PORT = 47777
EXT_HEADER = "X-YtdlpGUI"


def start_extension_server(on_urls):
    """เปิด HTTP server ที่ 127.0.0.1:EXT_PORT ให้ Chrome Extension ส่งลิงก์มา
    รับเฉพาะคำขอที่มี header X-YtdlpGUI และมาจาก extension (เว็บทั่วไปส่งมาไม่ได้)"""
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):  # ไม่ต้องพิมพ์ log ของ server
            pass

        def _allowed(self):
            origin = self.headers.get("Origin", "")
            return self.headers.get(EXT_HEADER) == "1" and (
                not origin or origin.startswith(("chrome-extension://", "moz-extension://", "extension://")))

        def _ext_origin(self):
            origin = self.headers.get("Origin", "")
            return origin if origin.startswith(("chrome-extension://", "moz-extension://", "extension://")) else ""

        def _cors(self):
            # อนุญาตเฉพาะ origin ของ extension (Chrome ใหม่ๆ ถามก่อนยิงเข้า 127.0.0.1 / Local Network Access)
            origin = self._ext_origin()
            if origin:
                self.send_header("Access-Control-Allow-Origin", origin)
                self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", f"Content-Type, {EXT_HEADER}")
                self.send_header("Access-Control-Allow-Private-Network", "true")
                self.send_header("Vary", "Origin")

        def _reply(self, code, obj):
            body = json.dumps(obj).encode()
            self.send_response(code)
            self._cors()
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_OPTIONS(self):
            # preflight: ตอบอนุญาตเฉพาะ extension / หน้าเว็บทั่วไปได้ 403 เลยยิงเข้ามาไม่ได้
            self.send_response(204 if self._ext_origin() else 403)
            self._cors()
            self.send_header("Content-Length", "0")
            self.end_headers()

        def do_GET(self):
            if self.path.startswith("/ping") and self._allowed():
                self._reply(200, {"app": APP_NAME, "version": APP_VERSION})
            else:
                self._reply(403, {"ok": False})

        def do_POST(self):
            if not self.path.startswith("/add") or not self._allowed():
                return self._reply(403, {"ok": False})
            try:
                n = int(self.headers.get("Content-Length") or 0)
                data = json.loads(self.rfile.read(min(n, 1 << 20)) or b"{}")
                urls = [u for u in data.get("urls", []) if isinstance(u, str) and u.startswith(("http://", "https://"))]
            except (ValueError, AttributeError):
                return self._reply(400, {"ok": False})
            if not urls:
                return self._reply(400, {"ok": False, "error": "no http(s) url"})
            on_urls(urls[:500], bool(data.get("start", True)))
            self._reply(200, {"ok": True, "received": len(urls)})

    srv = ThreadingHTTPServer(("127.0.0.1", EXT_PORT), Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def fresh_env():
    """environment สำหรับเปิดแอปตัวใหม่: ตัดตัวแปรของ PyInstaller ทิ้ง
    ไม่งั้นแอปตัวใหม่จะไปหาโฟลเดอร์ _MEIxxxx ของแอปตัวเก่า (ที่ถูกลบไปแล้ว) แล้วเปิดไม่ขึ้น
    ("Failed to load Python DLL")"""
    env = {k: v for k, v in os.environ.items() if not k.startswith("_PYI") and k not in ("_MEIPASS", "_MEIPASS2")}
    env["PYINSTALLER_RESET_ENVIRONMENT"] = "1"
    return env


def to_int(var, default, lo, hi):
    try:
        return max(lo, min(hi, int(var.get())))
    except (tk.TclError, ValueError):
        return default


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} v{APP_VERSION}")
        self.pending_update = ""  # path ของ exe ใหม่ที่โหลดมาแล้ว รอติดตั้งตอนคิวว่าง
        self.geometry("1000x680")
        self.minsize(820, 540)

        s = {**DEFAULTS, **load_json(SETTINGS_FILE, {})}
        set_lang(s["lang"])
        self.lang = s["lang"] if s["lang"] in LANGS else "en"
        self.var_out = tk.StringVar(value=s["out_dir"])
        self.var_format = tk.StringVar(value=tr(s["format"] if s["format"] in FORMATS else DEFAULTS["format"]))
        self.var_res = tk.StringVar(value=tr(s["resolution"] if s["resolution"] in RESOLUTIONS else "สูงสุด"))
        self.var_crf = tk.IntVar(value=s["crf"])
        self.var_preset = tk.StringVar(value=s["preset"])
        self.var_container = tk.StringVar(value=s["container"] if s["container"] in CONTAINERS else "mp4")
        self.var_aria = tk.BooleanVar(value=s["aria2c"])
        self.var_cookies = tk.StringVar(value=tr(s["cookies"]))
        self.var_update = tk.BooleanVar(value=s["update_on_start"])
        self.var_auto_clear = tk.BooleanVar(value=s["auto_clear"])
        self.var_max_pages = tk.IntVar(value=s["max_pages"])
        self.var_name_max = tk.IntVar(value=s["name_max"])
        self.done_count = 0  # จำนวนที่เสร็จในรอบนี้ (นับแม้ถูกล้างออกจากคิวไปแล้ว)
        self.var_max_dl = tk.IntVar(value=s["max_dl"])
        self.var_max_conv = tk.IntVar(value=s["max_conv"])
        self.var_frags = tk.IntVar(value=s["frags"])
        self.var_encoder = tk.StringVar(value=tr("กำลังทดสอบ ..."))
        self.var_url = tk.StringVar()
        self.var_status = TrVar(value=tr("พร้อม"))

        self.items = []
        self.ids = itertools.count(1)
        self.events = queue.Queue()
        self.procs = {}  # item id -> Popen
        self.procs_lock = threading.Lock()
        self.active_dl = 0
        self.active_conv = 0
        self.running = False
        self.stopping = False
        self.busy_updating = False
        self.title_queue = queue.Queue()
        self.cancelled = set()  # id ของคลิปที่ผู้ใช้เอาติ๊กแปลงออกระหว่างแปลง

        os.makedirs(TMP_DIR, exist_ok=True)
        try:  # เลิกใช้ประวัติของ yt-dlp แล้ว (รหัสคลิปที่แกะจากลิงก์วิดีโอซ้ำกันจนข้ามคลิปอื่นทิ้ง)
            os.remove(OLD_ARCHIVE)
        except OSError:
            pass
        SOURCES.update(load_json(SOURCES_FILE, {}))
        self._build_ui()
        self._build_menubar()
        self._translate_widgets(self)
        for _ in range(TITLE_WORKERS):
            threading.Thread(target=self._title_worker, daemon=True).start()
        for it in load_json(QUEUE_FILE, []):
            if isinstance(it, dict) and it.get("url"):
                if self._add_item(it["url"], it.get("title", ""), save=False, file=it.get("file", ""),
                                  convert=bool(it.get("convert", False)), subdir=it.get("subdir", "")):
                    self.items[-1]["custom_title"] = bool(it.get("custom_title", False))
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.tray = None
        self.tray_state = None
        self._setup_tray()
        self.autostart = False  # ลิงก์จาก extension: เริ่มโหลดให้เองเมื่อพร้อม
        try:
            self.ext_server = start_extension_server(lambda urls, go: self.events.put(("ext_add", urls, go)))
        except OSError as e:
            self.ext_server = None
            self.write_log(f"เปิดช่องรับลิงก์จาก Chrome Extension ไม่ได้ (port {EXT_PORT}): {e}")
        self.after(15000, self.push_error_logs)
        self.bench_ready = False
        threading.Thread(target=lambda: self.events.put(("encoders", benchmark_encoders())), daemon=True).start()
        self.after(100, self._pump)

        if not os.path.isfile(YTDLP):
            messagebox.showerror(APP_NAME, tr(f"ไม่เจอ yt-dlp.exe ที่\n{YTDLP}") + "\n\nsetup.bat")
        elif self.var_update.get():
            self.run_update()
            self.check_app_update()

    # ---------- UI ----------
    def _build_ui(self):
        style = ttk.Style(self)
        if "vista" in style.theme_names():
            style.theme_use("vista")
        self.option_add("*Font", ("Segoe UI", 10))
        pad = {"padx": 8, "pady": 4}
        self.bind_all("<Control-KeyPress>", self._on_ctrl_key)

        top = ttk.LabelFrame(self, text="เพิ่มลิงก์ (Ctrl+V วางแล้วเข้าคิวทันที วางหลายลิงก์พร้อมกันได้)")
        top.pack(fill="x", **pad)
        self.ent_url = ttk.Entry(top, textvariable=self.var_url)
        self.ent_url.pack(side="left", fill="x", expand=True, padx=6, pady=6)
        self.ent_url.bind("<Return>", lambda e: self.add_urls())
        self.ent_url.focus_set()
        ttk.Button(top, text="วางจากคลิปบอร์ด", command=self.paste_urls).pack(side="left", padx=2)
        ttk.Button(top, text="เพิ่มเข้าคิว", command=self.add_urls).pack(side="left", padx=6)

        mid = ttk.LabelFrame(self, text="คิว")
        mid.pack(fill="both", expand=True, **pad)
        cols = ("no", "title", "url", "folder", "status", "progress", "conv")
        self.conv_col = f"#{cols.index('conv') + 1}"
        self.tree = ttk.Treeview(mid, columns=cols, show="headings", selectmode="extended")
        # กว้างเท่าไหร่ก็แบ่งตามสัดส่วนนี้ (รวม 100) จะได้เห็นครบทุกช่องตั้งแต่เปิดแอป ไม่ต้องลากขยายเอง
        self.col_share = {"no": 4, "title": 25, "url": 23, "folder": 11, "status": 10, "progress": 21, "conv": 6}
        self.col_min = {"no": 34, "title": 110, "url": 120, "folder": 70, "status": 70, "progress": 130, "conv": 45}
        # ช่องสั้นๆ ไม่ต้องกว้างเกินนี้ ที่เหลือยกให้ "ชื่อ" กับ "ความคืบหน้า"
        self.col_max = {"no": 46, "folder": 130, "status": 110, "conv": 62}
        for c, t in [("no", "#"), ("title", "ชื่อ"), ("url", "ลิงก์"), ("folder", "โฟลเดอร์ย่อย"),
                     ("status", "สถานะ"), ("progress", "ความคืบหน้า"), ("conv", "แปลง")]:
            self.tree.heading(c, text=t)
            self.tree.column(c, width=self.col_min[c], minwidth=self.col_min[c], stretch=False,
                             anchor="w" if c in ("title", "url", "progress") else "center")
        self.tree.bind("<Configure>", self._fit_columns)
        sb = ttk.Scrollbar(mid, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=(6, 0), pady=6)
        sb.pack(side="left", fill="y", pady=6)
        self.tree.bind("<Delete>", lambda e: self.remove_selected())
        self.tree.bind("<Double-1>", self._copy_url)
        self.tree.bind("<Button-3>", self._on_right_click)
        self.menu = tk.Menu(self, tearoff=0)
        self.tree.bind("<Button-1>", self._on_tree_click)
        self.tree.bind("<space>", lambda e: self.toggle_convert_selected() or "break")
        self.tree.heading("conv", command=self.toggle_convert_all)

        qbtn = ttk.Frame(self)
        qbtn.pack(fill="x", padx=8)
        ttk.Button(qbtn, text="ลบที่เลือก", command=self.remove_selected).pack(side="left")
        ttk.Button(qbtn, text="ล้างที่เสร็จแล้ว", command=self.clear_done).pack(side="left", padx=4)
        ttk.Checkbutton(qbtn, text="ล้างอัตโนมัติ", variable=self.var_auto_clear,
                        command=self.save_settings).pack(side="left", padx=(0, 8))
        ttk.Button(qbtn, text="ลองใหม่ที่ล้มเหลว", command=self.retry_failed).pack(side="left")
        ttk.Button(qbtn, text="เปิดโฟลเดอร์", command=self.open_folder).pack(side="left", padx=4)
        ttk.Button(qbtn, text="ดึงชื่อใหม่", command=self.refetch_titles).pack(side="left")
        ttk.Label(qbtn, text="คลิก ☐ = สลับแปลง/ไม่แปลง (เลือกหลายแถวแล้วกด Space ได้) · ดับเบิลคลิก = คัดลอกลิงก์",
                  foreground="gray").pack(side="right")

        opt = ttk.LabelFrame(self, text="ตั้งค่า")
        opt.pack(fill="x", **pad)
        r0 = ttk.Frame(opt)
        r0.pack(fill="x", padx=6, pady=(6, 2))
        ttk.Label(r0, text="โหลดลง:").pack(side="left")
        ttk.Entry(r0, textvariable=self.var_out).pack(side="left", fill="x", expand=True, padx=6)
        ttk.Button(r0, text="เลือก...", command=self.browse_out).pack(side="left")

        r1 = ttk.Frame(opt)
        r1.pack(fill="x", padx=6, pady=2)
        ttk.Label(r1, text="รูปแบบ:").pack(side="left")
        ttk.Combobox(r1, textvariable=self.var_format, values=[tr(k) for k in FORMATS], state="readonly",
                     width=30).pack(side="left", padx=6)
        ttk.Label(r1, text="ความชัด:").pack(side="left", padx=(8, 0))
        ttk.Combobox(r1, textvariable=self.var_res, values=[tr(k) for k in RESOLUTIONS], state="readonly",
                     width=7).pack(side="left", padx=4)
        ttk.Label(r1, text="Cookies จาก:").pack(side="left", padx=(12, 0))
        ttk.Combobox(r1, textvariable=self.var_cookies, values=[tr(b) for b in BROWSERS], state="readonly",
                     width=10).pack(side="left", padx=6)
        ttk.Checkbutton(r1, text="ใช้ aria2c (โหลดเร็ว)", variable=self.var_aria).pack(side="left", padx=12)
        r1b = ttk.Frame(opt)  # แยกเป็นแถวที่ 2 ภาษาอังกฤษข้อความยาวกว่า ไม่งั้นล้นจอ
        r1b.pack(fill="x", padx=6, pady=(2, 6))
        ttk.Label(r1b, text="โหลดพร้อมกัน:").pack(side="left")
        ttk.Spinbox(r1b, from_=1, to=8, textvariable=self.var_max_dl, width=4,
                    state="readonly").pack(side="left", padx=4)
        ttk.Label(r1b, text="หน้ารวมสูงสุด:").pack(side="left", padx=(12, 0))
        ttk.Spinbox(r1b, from_=1, to=50, textvariable=self.var_max_pages, width=4).pack(side="left", padx=4)
        ttk.Label(r1b, text="ชิ้นส่วนพร้อมกัน:").pack(side="left", padx=(12, 0))
        ttk.Spinbox(r1b, from_=1, to=32, textvariable=self.var_frags, width=4).pack(side="left", padx=4)
        ttk.Label(r1b, text="ชื่อไฟล์ยาวสุด:").pack(side="left", padx=(12, 0))
        ttk.Spinbox(r1b, from_=30, to=150, increment=5, textvariable=self.var_name_max, width=4).pack(side="left", padx=4)
        ttk.Checkbutton(r1b, text="เช็คอัปเดตตอนเปิด", variable=self.var_update).pack(side="right")

        conv = ttk.LabelFrame(self, text="ตั้งค่าการแปลง H.265 (ใช้กับคลิปที่ติ๊ก ☑ ในช่อง \"แปลง\")")
        conv.pack(fill="x", padx=8, pady=4)
        r2 = ttk.Frame(conv)
        r2.pack(fill="x", padx=6, pady=6)
        ttk.Label(r2, text="ตัวแปลง:").pack(side="left")
        self.cmb_encoder = ttk.Combobox(r2, textvariable=self.var_encoder, values=[CPU_ENC],
                                        state="readonly", width=24)
        self.cmb_encoder.pack(side="left", padx=4)
        ttk.Label(r2, text="ไฟล์:").pack(side="left", padx=(8, 0))
        self.cmb_container = ttk.Combobox(r2, textvariable=self.var_container, values=CONTAINERS,
                                          state="readonly", width=5)
        self.cmb_container.pack(side="left", padx=4)
        ttk.Label(r2, text="คุณภาพ:").pack(side="left", padx=(8, 0))
        self.spin_crf = ttk.Spinbox(r2, from_=16, to=34, textvariable=self.var_crf, width=4)
        self.spin_crf.pack(side="left", padx=4)
        ttk.Label(r2, text="Preset:").pack(side="left", padx=(8, 0))
        self.cmb_preset = ttk.Combobox(r2, textvariable=self.var_preset, values=PRESETS,
                                       state="readonly", width=9)
        self.cmb_preset.pack(side="left", padx=4)
        ttk.Label(r2, text="แปลงพร้อมกัน:").pack(side="left", padx=(8, 0))
        self.spin_conv = ttk.Spinbox(r2, from_=1, to=4, textvariable=self.var_max_conv, width=4,
                                     state="readonly")
        self.spin_conv.pack(side="left", padx=4)

        act = ttk.Frame(self)
        act.pack(fill="x", padx=8, pady=4)
        self.btn_start = ttk.Button(act, text="▶ เริ่มโหลด", command=self.start)
        self.btn_start.pack(side="left")
        self.btn_stop = ttk.Button(act, text="■ หยุด", command=self.stop, state="disabled")
        self.btn_stop.pack(side="left", padx=4)
        self.btn_update = ttk.Button(act, text="อัปเดตเครื่องมือ", command=self.run_update)
        self.btn_update.pack(side="left", padx=4)
        ttk.Label(act, textvariable=self.var_status).pack(side="left", padx=12)

        logf = ttk.LabelFrame(self, text="Log")
        logf.pack(fill="both", **pad)
        self.log = tk.Text(logf, height=8, wrap="none", font=("Consolas", 9), state="disabled")
        lsb = ttk.Scrollbar(logf, orient="vertical", command=self.log.yview)
        self.log.configure(yscrollcommand=lsb.set)
        self.log.pack(side="left", fill="both", expand=True, padx=(6, 0), pady=6)
        lsb.pack(side="left", fill="y", pady=6)

    def _on_ctrl_key(self, e):
        w = e.widget
        if e.keycode == 86 and w in (self.ent_url, self.tree):
            self.paste_urls()  # วางลิงก์ = เข้าคิวเลย
            return "break"
        # แป้นภาษาไทยทำให้ keysym ไม่ใช่ v/c/x/a ทำให้ Tk ไม่รู้จักทางลัด ต้องยิงเหตุการณ์เอง
        ev = CTRL_KEYS.get(e.keycode)
        if ev and e.keysym.lower() not in ("v", "c", "x", "a") and isinstance(w, (tk.Entry, ttk.Entry, tk.Text)):
            w.event_generate(ev)
            return "break"
        if e.keycode == 65 and isinstance(w, (tk.Entry, ttk.Entry)):
            w.select_range(0, "end")
            w.icursor("end")
            return "break"
        return None

    def _translate_widgets(self, w):
        """แปลข้อความบนปุ่ม/ป้าย/กรอบ/หัวตาราง ทั้งหมดหลังสร้างหน้าจอ"""
        for c in w.winfo_children():
            try:
                t = c.cget("text")
                if isinstance(t, str) and t:
                    c.configure(text=tr(t))
            except tk.TclError:
                pass
            if isinstance(c, ttk.Treeview):
                for col in c["columns"]:
                    c.heading(col, text=tr(c.heading(col, "text")))
            self._translate_widgets(c)

    def _build_menubar(self):
        bar = tk.Menu(self)
        lang = tk.Menu(bar, tearoff=0)
        self.var_lang = tk.StringVar(value=self.lang)
        for code, name in LANGS.items():
            lang.add_radiobutton(label=name, value=code, variable=self.var_lang,
                                 command=lambda c=code: self.change_language(c))
        bar.add_cascade(label="Language / ภาษา", menu=lang)
        tools = tk.Menu(bar, tearoff=0)
        tools.add_command(label=tr("ล้างประวัติไฟล์ที่โหลด (sources.json)"), command=self.clear_sources)
        bar.add_cascade(label=tr("เครื่องมือ"), menu=tools)
        self.config(menu=bar)

    def clear_sources(self):
        """ลืมว่าไฟล์ไหนโหลดมาจากลิงก์ไหน (ไฟล์วิดีโอไม่ถูกลบ) หลังล้างแล้วไฟล์เดิมที่ชื่อตรงกันจะนับว่า "มีแล้ว" ตามชื่อ"""
        n = len(SOURCES)
        if not messagebox.askyesno(APP_NAME, tr(f"ล้างประวัติไฟล์ที่โหลด {n} รายการ ไฟล์วิดีโอไม่ถูกลบ") + "?"):
            return
        SOURCES.clear()
        try:
            os.remove(SOURCES_FILE)
        except OSError:
            pass
        self.write_log(f"ล้างประวัติไฟล์ที่โหลดแล้ว {n} รายการ")
        self.var_status.set(tr("ล้างประวัติไฟล์ที่โหลดแล้ว"))

    def change_language(self, code):
        """เปลี่ยนภาษาแล้วเปิดแอปใหม่ (คิวและค่าที่ตั้งไว้ยังอยู่)"""
        if code == self.lang:
            return
        if self.running and not messagebox.askyesno(APP_NAME, tr("กำลังโหลด/แปลงอยู่ จะปิดและหยุดเลยไหม") + "?"):
            self.var_lang.set(self.lang)
            return
        self.stop()
        self.lang = code
        self.save_settings()
        self.save_queue()
        args = [sys.executable] if getattr(sys, "frozen", False) else [sys.executable, os.path.abspath(__file__)]
        subprocess.Popen(args, cwd=APP_DIR, env=fresh_env())
        self.destroy()

    def write_log(self, text):
        text = tr(text)
        self.log.configure(state="normal")
        self.log.insert("end", text.rstrip("\n") + "\n")
        if int(self.log.index("end-1c").split(".")[0]) > 3000:
            self.log.delete("1.0", "500.0")
        self.log.see("end")
        self.log.configure(state="disabled")

    # ---------- queue ----------
    def _add_item(self, url, title="", save=True, file="", convert=False, subdir=""):
        """คืน True ถ้าเพิ่มเข้าคิว, False ถ้าซ้ำกับคลิปที่อยู่ในคิวแล้ว"""
        key = url_key(url)
        dup = next((i for i in self.items if i["key"] == key), None)
        if dup:
            self.write_log(f"ข้ามลิงก์ซ้ำ (ซ้ำกับ #{self.items.index(dup) + 1}): {url}")
            return False
        it = {"id": next(self.ids), "url": url, "key": key, "title": title, "status": WAIT, "progress": "",
              "file": "", "convert": convert, "converted": False, "cancel_conv": False, "force": False,
              "subdir": subdir}
        if file and os.path.isfile(file):
            it["file"] = file
            if convert:
                it["status"], it["progress"] = WAIT_CONV, "โหลดแล้ว รอแปลง"
            else:
                it["status"], it["progress"] = DONE, "โหลดแล้ว (ไม่แปลง)"
        self.items.append(it)
        it["iid"] = self.tree.insert("", "end")
        self._refresh(it)
        if not title:
            it["progress"] = "กำลังดึงชื่อ ..."
            self._refresh(it)
            self.title_queue.put((it["id"], url, self._cookie_args()))
        else:
            self._check_existing(it)
        if save:
            self.save_queue()
        return True

    def _dest(self, it):
        """โฟลเดอร์ปลายทางของคลิปนี้ (โฟลเดอร์หลัก + โฟลเดอร์ย่อยถ้ามาจากหน้ารวม)"""
        base = self.var_out.get().strip() or DEFAULTS["out_dir"]
        return os.path.join(base, it["subdir"]) if it.get("subdir") else base

    def _check_existing(self, it):
        """ถ้ามีไฟล์คลิปนี้ในโฟลเดอร์ปลายทางอยู่แล้ว ให้ข้ามไม่ต้องโหลด (เว้นแต่กดลองใหม่เพื่อบังคับโหลด)"""
        if it["status"] != WAIT or it["force"]:
            return False
        f = find_existing(self._dest(it), it["title"], it["url"])
        if f:
            it["status"], it["progress"], it["file"] = HAVE, os.path.basename(f), f
            self._refresh(it)
            self.write_log(f"มีไฟล์อยู่แล้ว ไม่โหลดซ้ำ: {f}")
            return True
        return False

    def _find(self, item_id):
        return next((i for i in self.items if i["id"] == item_id), None)

    def _fit_columns(self, event=None):
        """แบ่งความกว้างคอลัมน์ตามสัดส่วนของตารางตอนนี้ (เรียกทุกครั้งที่ตารางเปลี่ยนขนาด)"""
        total = (event.width if event else self.tree.winfo_width()) - 4
        if total < sum(self.col_min.values()):
            total = sum(self.col_min.values())
        if abs(total - getattr(self, "_cols_w", 0)) < 8:
            return
        self._cols_w = total
        w = {c: max(self.col_min[c], total * share // 100) for c, share in self.col_share.items()}
        for c, mx in self.col_max.items():
            w[c] = min(w[c], mx)
        left = total - sum(w.values())  # ที่เหลือจากการตัดช่องสั้น แบ่งให้สองช่องที่ข้อความยาว
        w["title"] += left // 2
        w["progress"] += left - left // 2
        for c, width in w.items():
            self.tree.column(c, width=width)

    def _refresh(self, it):
        if self.tree.exists(it["iid"]):
            idx = self.items.index(it) + 1
            self.tree.item(it["iid"], values=(idx, it["title"] or it["file"] or "-", short_url(it["url"]),
                                              it.get("subdir", ""), tr(it["status"]), tr(it["progress"]),
                                              "☑" if it["convert"] else "☐"))

    def _renumber(self):
        for it in self.items:
            self._refresh(it)

    def add_urls(self, text=None):
        text = self.var_url.get() if text is None else text
        urls = [u for u in re.split(r"\s+", text) if u.lower().startswith(("http://", "https://"))]
        if not urls:
            if text.strip():
                self.var_status.set("ไม่เจอลิงก์ (ต้องขึ้นต้นด้วย http:// หรือ https://)")
            return
        urls = list(dict.fromkeys(urls))
        listings = [u for u in urls if is_listing_url(u)]
        singles = [u for u in urls if u not in listings]
        added = sum(1 for u in singles if self._add_item(u, save=False))
        self.save_queue()
        self.var_url.set("")
        skipped = len(singles) - added
        msg = f"เพิ่ม {added} ลิงก์" + (f" (ข้ามลิงก์ซ้ำ {skipped})" if skipped else "")
        if listings:
            msg += f" · กำลังแกะลิงก์จากหน้ารวม {len(listings)} หน้า ..."
            for u in listings:
                self.expand_async(u)
        self.var_status.set(msg)

    def expand_async(self, url):
        """แกะลิงก์คลิปจากหน้ารวมใน thread แยก แล้วส่งผลกลับมาเพิ่มเข้าคิว"""
        pages = to_int(self.var_max_pages, 5, 1, 50)
        self.write_log(f"แกะลิงก์คลิปจาก: {url} (สูงสุด {pages} หน้า)")

        def work():
            links = expand_listing(url, notify=lambda m: self.events.put(("notice", f"[แกะลิงก์] {m}")),
                                   max_pages=pages)
            self.events.put(("expanded", url, links, listing_folder(url)))

        threading.Thread(target=work, daemon=True).start()

    def paste_urls(self):
        try:
            self.add_urls(self.clipboard_get())
        except tk.TclError:
            pass

    def _copy_url(self, e):
        iid = self.tree.identify_row(e.y)
        it = next((i for i in self.items if i["iid"] == iid), None)
        if it:
            self.clipboard_clear()
            self.clipboard_append(it["url"])
            self.var_status.set("คัดลอกลิงก์แล้ว")

    # ---------- right-click menu ----------
    def _selected_items(self):
        sel = set(self.tree.selection())
        return [i for i in self.items if i["iid"] in sel]

    def _on_right_click(self, e):
        iid = self.tree.identify_row(e.y)
        if not iid:
            return
        if iid not in self.tree.selection():
            self.tree.selection_set(iid)
        items = self._selected_items()
        one = items[0] if len(items) == 1 else None
        busy = any(i["status"] in (DL, CONV) for i in items)
        m = self.menu
        m.delete(0, "end")
        m.add_command(label=f"รีเซ็ตสถานะ (กลับไปรอโหลด){'' if one else f'  [{len(items)} แถว]'}",
                      command=self.menu_reset, state="disabled" if busy else "normal")
        m.add_command(label="โหลดซ้ำ (ไม่สนว่ามีไฟล์แล้ว)", command=self.menu_force,
                      state="disabled" if busy else "normal")
        m.add_separator()
        m.add_command(label="แก้ไขลิงก์ ...", command=lambda: self.menu_edit_url(one),
                      state="normal" if one and not busy else "disabled")
        m.add_command(label="แก้ไขชื่อ (ใช้เป็นชื่อไฟล์) ...", command=lambda: self.menu_edit_title(one),
                      state="normal" if one and not busy else "disabled")
        m.add_command(label="แกะลิงก์คลิปจากหน้านี้ (หน้ารวม/ค้นหา)", command=self.menu_expand,
                      state="disabled" if busy else "normal")
        m.add_command(label="ดึงชื่อใหม่", command=self.refetch_titles)
        m.add_command(label="สลับ แปลง / ไม่แปลง", command=self.toggle_convert_selected)
        m.add_separator()
        m.add_command(label="คัดลอกลิงก์", command=lambda: self._copy_text("\n".join(i["url"] for i in items)))
        has_file = bool(one and one["file"] and os.path.isfile(one["file"]))
        m.add_command(label="เปิดไฟล์", command=lambda: os.startfile(one["file"]),
                      state="normal" if has_file else "disabled")
        m.add_command(label="เปิดโฟลเดอร์ที่มีไฟล์",
                      command=lambda: subprocess.Popen(["explorer", "/select,", one["file"]]),
                      state="normal" if has_file else "disabled")
        m.add_separator()
        m.add_command(label="ลบออกจากคิว", command=self.remove_selected, state="disabled" if busy else "normal")
        for i in range((m.index("end") or 0) + 1):
            if m.type(i) == "command":
                m.entryconfigure(i, label=tr(m.entrycget(i, "label")))
        m.tk_popup(e.x_root, e.y_root)

    def _copy_text(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)
        self.var_status.set("คัดลอกแล้ว")

    def _reset_item(self, it, force=False):
        has_file = bool(it["file"]) and os.path.isfile(it["file"])
        if not force and has_file and it["convert"] and not it["converted"] and it["status"] in (FAIL, STOPPED):
            it["status"], it["progress"] = WAIT_CONV, "รอแปลง"  # โหลดแล้ว แค่แปลงไม่ผ่าน
        else:
            it["status"], it["progress"], it["file"] = WAIT, "โหลดซ้ำ" if force else "", ""
            it["converted"], it["cancel_conv"] = False, False
        it["force"] = force
        self._refresh(it)

    def menu_reset(self):
        for it in self._selected_items():
            if it["status"] not in (DL, CONV):
                self._reset_item(it)
                self._check_existing(it)
        self.save_queue()
        if self.running:
            self._schedule()

    def menu_expand(self):
        """เอาแถวที่เลือกออก แล้วแกะลิงก์คลิปจากหน้านั้นมาใส่คิวแทน"""
        for it in self._selected_items():
            if it["status"] in (DL, CONV):
                continue
            self.tree.delete(it["iid"])
            self.items.remove(it)
            self.expand_async(it["url"])
        self._renumber()
        self.save_queue()

    def menu_force(self):
        for it in self._selected_items():
            if it["status"] not in (DL, CONV):
                self._reset_item(it, force=True)
        self.save_queue()
        if self.running:
            self._schedule()

    def menu_edit_url(self, it):
        if not it:
            return
        new = simpledialog.askstring(tr("แก้ไขลิงก์"), tr("ลิงก์ใหม่") + ":", initialvalue=it["url"], parent=self)
        if not new or not new.strip() or new.strip() == it["url"]:
            return
        new = new.strip()
        key = url_key(new)
        dup = next((i for i in self.items if i is not it and i["key"] == key), None)
        if dup:
            messagebox.showwarning(APP_NAME, tr(f"ลิงก์นี้ซ้ำกับแถว #{self.items.index(dup) + 1} อยู่แล้ว"), parent=self)
            return
        it["url"], it["key"] = new, key
        if not it.get("custom_title"):
            it["title"] = ""
        self._reset_item(it)
        if not it["title"]:
            it["progress"] = "กำลังดึงชื่อ ..."
            self._refresh(it)
            self.title_queue.put((it["id"], new, self._cookie_args()))
        self.save_queue()

    def menu_edit_title(self, it):
        if not it:
            return
        new = simpledialog.askstring(tr("แก้ไขชื่อ"), tr("ชื่อใหม่ (ใช้เป็นชื่อไฟล์ตอนโหลด)") + ":",
                                     initialvalue=it["title"], parent=self)
        if new is None or not new.strip():
            return
        it["title"], it["custom_title"] = new.strip(), True
        self._refresh(it)
        self.save_queue()

    def refetch_titles(self):
        """ดึงชื่อใหม่ของแถวที่เลือก (ไม่เลือก = ทุกแถว)"""
        sel = set(self.tree.selection())
        cookies = self._cookie_args()
        for it in self.items:
            if (not sel or it["iid"] in sel) and it["status"] in (WAIT, FAIL, STOPPED, WAIT_CONV, DONE):
                if it["status"] == WAIT:
                    it["progress"] = "กำลังดึงชื่อ ..."
                    self._refresh(it)
                self.title_queue.put((it["id"], it["url"], cookies))

    def _on_tree_click(self, e):
        if self.tree.identify_region(e.x, e.y) != "cell" or self.tree.identify_column(e.x) != self.conv_col:
            return None
        iid = self.tree.identify_row(e.y)
        it = next((i for i in self.items if i["iid"] == iid), None)
        if it:
            self._set_convert(it, not it["convert"])
            self.save_queue()
        return "break"

    def toggle_convert_selected(self):
        sel = [i for i in self.items if i["iid"] in set(self.tree.selection())]
        if sel:
            on = not all(i["convert"] for i in sel)
            for it in sel:
                self._set_convert(it, on)
            self.save_queue()

    def toggle_convert_all(self):
        if self.items:
            on = not all(i["convert"] for i in self.items)
            for it in self.items:
                self._set_convert(it, on)
            self.save_queue()

    def _set_convert(self, it, on):
        """สลับว่าจะแปลงคลิปนี้ไหม มีผลทันทีแม้คลิปโหลดเสร็จหรือกำลังแปลงอยู่"""
        it["convert"] = on
        has_file = bool(it["file"]) and os.path.isfile(it["file"])
        if on and it["status"] == DONE and not it["converted"] and has_file:
            it["status"], it["progress"] = WAIT_CONV, "รอแปลง"
            if not self.running:
                self.var_status.set("มีคลิปรอแปลง กด ▶ เริ่มโหลด เพื่อเริ่มแปลง")
        elif not on and it["status"] == WAIT_CONV:
            it["status"], it["progress"] = DONE, "โหลดแล้ว (ไม่แปลง)"
        elif not on and it["status"] == CONV:
            it["cancel_conv"] = True
            self.cancelled.add(it["id"])
            with self.procs_lock:
                p = self.procs.get(("conv", it["id"]))
            if p and p.poll() is None:
                subprocess.run(["taskkill", "/PID", str(p.pid), "/T", "/F"],
                               creationflags=NO_WINDOW, capture_output=True)
            it["progress"] = "กำลังยกเลิกแปลง ..."
        self._refresh(it)
        if self.running:
            self._schedule()

    def remove_selected(self):
        sel = set(self.tree.selection())
        for it in list(self.items):
            if it["iid"] in sel and it["status"] not in (DL, CONV):
                self.tree.delete(it["iid"])
                self.items.remove(it)
        self._renumber()
        self.save_queue()

    def clear_done(self):
        for it in list(self.items):
            if it["status"] in (DONE, HAVE):
                self.tree.delete(it["iid"])
                self.items.remove(it)
        self._renumber()
        self.save_queue()

    def retry_failed(self):
        for it in self.items:
            if it["status"] == HAVE:  # กดลองใหม่ = ยืนยันว่าจะโหลดซ้ำจริงๆ
                it["status"], it["progress"], it["file"], it["force"] = WAIT, "โหลดซ้ำ", "", True
                self._refresh(it)
            elif it["status"] in (FAIL, STOPPED):
                # ถ้าโหลดเสร็จแล้วแต่แปลงไม่ผ่าน ให้กลับไปรอแปลง ไม่ต้องโหลดใหม่
                has_file = bool(it["file"]) and os.path.isfile(it["file"])
                it["status"] = (WAIT_CONV if it["convert"] else DONE) if has_file else WAIT
                it["progress"] = ""
                self._refresh(it)
        self.save_queue()
        if self.running:
            self._schedule()

    def save_queue(self):
        save_json(QUEUE_FILE, [{"url": it["url"], "title": it["title"], "convert": it["convert"],
                                "custom_title": it.get("custom_title", False), "subdir": it.get("subdir", ""),
                                "file": it["file"] if it["status"] in (WAIT_CONV, CONV) else ""}
                               for it in self.items if it["status"] not in (DONE, HAVE)])

    def save_settings(self):
        save_json(SETTINGS_FILE, {
            "out_dir": self.var_out.get(), "format": from_display(self.var_format.get(), FORMATS),
            "resolution": from_display(self.var_res.get(), RESOLUTIONS), "lang": self.lang,
            "crf": to_int(self.var_crf, DEFAULTS["crf"], 0, 51), "preset": self.var_preset.get(),
            "container": self.var_container.get(), "aria2c": self.var_aria.get(),
            "cookies": from_display(self.var_cookies.get(), BROWSERS), "update_on_start": self.var_update.get(),
            "auto_clear": self.var_auto_clear.get(), "max_pages": to_int(self.var_max_pages, 5, 1, 50),
            "max_dl": to_int(self.var_max_dl, 3, 1, 8), "max_conv": to_int(self.var_max_conv, 1, 1, 4),
            "frags": to_int(self.var_frags, 16, 1, 32), "name_max": to_int(self.var_name_max, NAME_MAX, 30, 150),
        })

    def browse_out(self):
        d = filedialog.askdirectory(initialdir=self.var_out.get() or APP_DIR)
        if d:
            self.var_out.set(os.path.normpath(d))

    def open_folder(self):
        d = self.var_out.get()
        os.makedirs(d, exist_ok=True)
        os.startfile(d)

    # ---------- processes ----------
    def _run_proc(self, args, on_line, key=None):
        p = subprocess.Popen(
            args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
            env=child_env(), cwd=BIN_DIR, creationflags=NO_WINDOW,
            text=True, encoding="utf-8", errors="replace", bufsize=1)
        if key is not None:
            with self.procs_lock:
                self.procs[key] = p
        buf = ""
        # yt-dlp/ffmpeg ใช้ \r อัปเดตบรรทัดเดิม เลยอ่านทีละตัวแล้วตัดที่ \r หรือ \n
        try:
            while True:
                ch = p.stdout.read(1)
                if not ch:
                    break
                if ch in "\r\n":
                    if buf.strip():
                        on_line(buf)
                    buf = ""
                else:
                    buf += ch
            if buf.strip():
                on_line(buf)
            return p.wait()
        finally:
            if key is not None:
                with self.procs_lock:
                    self.procs.pop(key, None)

    def _cookie_args(self):
        c = from_display(self.var_cookies.get(), BROWSERS)
        return ["--cookies-from-browser", c] if c in BROWSERS[1:] else []

    def _title_worker(self):
        while True:
            item_id, url, cookies = self.title_queue.get()
            try:
                title = self._fetch_title(url, cookies)
            except Exception as e:  # ห้ามตาย ไม่งั้นแถวนี้ค้างอยู่ที่ "กำลังดึงชื่อ" ตลอดไป
                self.events.put(("log", f"ดึงชื่อไม่ได้: {e}"))
                title = ""
            self.events.put(("title", item_id, title))

    def _fetch_title(self, url, cookies):
        title = ""
        if not is_page_site(url) and url_host(url) not in NO_YTDLP_HOSTS:
            lines = []
            try:
                # %(title)j = ส่งเป็น JSON ไม่งั้นตัวอักษรไทยหายตอนส่งผ่าน pipe
                args = [YTDLP, "--skip-download", "--no-warnings", "--no-playlist", "--encoding", "utf-8",
                        "--js-runtimes", "deno", "--print", "%(title)j", *cookies, url]
                self._run_proc(args, lines.append)
            except OSError:
                pass
            for l in lines:
                l = l.strip()
                if l.startswith('"'):
                    try:
                        title = json.loads(l).strip()
                        break
                    except ValueError:
                        pass
                elif "Unsupported URL" in l:
                    NO_YTDLP_HOSTS.add(url_host(url))
                    self.events.put(("log", f"yt-dlp ไม่รองรับ {url_host(url)} ต่อไปจะอ่านหน้าเว็บเอาชื่อเลย"))
        if not title:
            title = page_title(fetch_page(url, notify=lambda m: self.events.put(("notice", m))))
        return title

    def check_app_update(self):
        """เช็คเวอร์ชันแอปกับ GitHub Releases ถ้ามีใหม่กว่า โหลดมาเตรียมไว้แล้วติดตั้งให้เอง"""
        if not getattr(sys, "frozen", False):
            return  # รันจาก source (.py) ให้ git pull เอง

        def work():
            rel = latest_release()
            if not rel:
                self.events.put(("log", "เช็คเวอร์ชันแอปกับ GitHub ไม่ได้ (ข้าม)"))
                return
            tag, asset_url, token = rel
            if parse_version(tag) <= parse_version(APP_VERSION):
                self.events.put(("log", f"แอปเป็นเวอร์ชันล่าสุดแล้ว (v{APP_VERSION})"))
                return
            self.events.put(("notice", f"มีแอปเวอร์ชันใหม่ {tag} กำลังโหลด ..."))
            dest = os.path.join(APP_DIR, "YtdlpGUI.new.exe")
            try:
                download_update(asset_url, token, dest)
            except Exception as e:
                self.events.put(("log", f"โหลดแอปเวอร์ชันใหม่ไม่ได้: {e}"))
                return
            self.events.put(("app_update", tag, dest))

        threading.Thread(target=work, daemon=True).start()

    def _apply_app_update(self):
        """ปิดแอป แล้วให้สคริปต์รอจนแอปปิดสนิท สลับไฟล์ exe แล้วเปิดแอปใหม่"""
        new = self.pending_update
        exe = sys.executable
        script = os.path.join(APP_DIR, "_update.cmd")
        # newline="" กัน \r\n กลายเป็น \r\r\n / ใช้ ping แทน timeout เพราะ timeout ใช้ไม่ได้ตอนไม่มีหน้าต่าง
        with open(script, "w", encoding="utf-8", newline="") as f:
            # ใช้ path เต็มของ find/tasklist ของ Windows กันไปเจอ find ของโปรแกรมอื่นใน PATH
            # และวนย้ายไฟล์ซ้ำจนสำเร็จ (ไฟล์ exe ยังถูกล็อกอยู่ครู่หนึ่งหลังแอปปิด)
            name = os.path.basename(exe)
            f.write("@echo off\r\n"
                    "set PYINSTALLER_RESET_ENVIRONMENT=1\r\n"
                    'set "SYS=%SystemRoot%\\System32"\r\n'
                    "set n=0\r\n"
                    ":wait\r\n"
                    f'"%SYS%\\tasklist.exe" /FI "IMAGENAME eq {name}" | "%SYS%\\find.exe" /I "{name}" >nul'
                    ' && ("%SYS%\\PING.EXE" -n 2 127.0.0.1 >nul & goto wait)\r\n'
                    ":move\r\n"
                    f'move /y "{new}" "{exe}" >nul 2>&1\r\n'
                    "if errorlevel 1 (\r\n"
                    "  set /a n+=1\r\n"
                    '  if %n% lss 30 ("%SYS%\\PING.EXE" -n 2 127.0.0.1 >nul & goto move)\r\n'
                    ")\r\n"
                    f'start "" "{exe}"\r\n'
                    'del "%~f0"\r\n')
        self.save_settings()
        self.save_queue()
        subprocess.Popen(["cmd", "/c", script], creationflags=NO_WINDOW, cwd=APP_DIR, env=fresh_env())
        self.destroy()

    def run_update(self):
        if self.running or self.busy_updating:
            return
        self.busy_updating = True
        self.btn_start.configure(state="disabled")
        self.btn_update.configure(state="disabled")
        self.var_status.set("กำลังเช็คอัปเดตเครื่องมือ ...")

        def work():
            rc = 0
            log = lambda m: self.events.put(("log", m))
            for name in TOOLS:
                try:
                    local = local_tool_version(name)
                    remote, url = remote_tool(name)
                    if not remote:
                        log(f"[อัปเดต] {name}: หาเวอร์ชันล่าสุดไม่เจอ ข้าม")
                        continue
                    if not tool_is_newer(name, remote, local):
                        log(f"[อัปเดต] {name} {local} ล่าสุดแล้ว")
                        continue
                    log(f"[อัปเดต] {name} {local or 'ยังไม่มี'} -> {remote} กำลังโหลด ...")
                    self.events.put(("notice", f"กำลังอัปเดต {name} เป็น {remote} ..."))
                    update_tool(name, url, lambda pct, n=name: self.events.put(
                        ("status", f"กำลังอัปเดต {n} ... {pct}%")))
                    log(f"[อัปเดต] {name} -> {remote} เสร็จ")
                except Exception as e:
                    rc = 1
                    log(f"[อัปเดต] {name} อัปเดตไม่ได้: {e}")
            self.events.put(("update_done", rc))

        threading.Thread(target=work, daemon=True).start()

    def _snapshot_options(self):
        """อ่านค่าจากหน้าจอใน main thread แล้วส่งให้ thread ใช้ (Tk ห้ามแตะจาก thread อื่น)"""
        return {
            "out": self.var_out.get().strip() or DEFAULTS["out_dir"],
            "format": FORMATS.get(from_display(self.var_format.get(), FORMATS), FORMATS[DEFAULTS["format"]]),
            "res": RESOLUTIONS.get(from_display(self.var_res.get(), RESOLUTIONS), 0),
            "cookies": self._cookie_args(),
            "aria2c": self.var_aria.get(),
            "frags": to_int(self.var_frags, 16, 1, 32), "name_max": to_int(self.var_name_max, NAME_MAX, 30, 150),
            "crf": to_int(self.var_crf, DEFAULTS["crf"], 0, 51),
            "preset": self.var_preset.get(),
            "encoder": enc_name(self.var_encoder.get()) if self.bench_ready else CPU_ENC,
            "container": self.var_container.get(),
        }

    def build_args(self, url, opts, pathfile=None, extra=(), outtmpl=None, aria=True):
        args = [YTDLP, "--newline", "--no-colors", "--no-warnings", "--no-playlist", "--encoding", "utf-8",
                "--ffmpeg-location", BIN_DIR, "--js-runtimes", "deno",
                "-P", opts["out"], "-o", outtmpl or default_outtmpl(opts.get("name_max", NAME_MAX)),
                # ไม่ใช้ --trim-filenames: มันตัดพาธของไฟล์ --print-to-file ด้วย (แอปอยู่ในโฟลเดอร์ลึกๆ แล้วหาไฟล์ที่โหลดไม่เจอ)
                # ความยาวชื่อคุมจาก -o อยู่แล้ว
                # โหลดซ้ำ (force) = เขียนทับไฟล์เดิม / ปกติ = ไม่เขียนทับไฟล์ที่มีอยู่
                "--force-overwrites" if opts.get("force") else "--no-overwrites",
                "--progress-template",
                "download:[P]%(progress._percent_str)s|%(progress._speed_str)s|%(progress._eta_str)s"
                "|%(progress.downloaded_bytes)s",
                # connection ที่เงียบเกิน 20 วิ ให้ตัดแล้วลองชิ้นนั้นใหม่ (ไม่งั้นค้างตลอดไปที่ 99.x%)
                "--socket-timeout", str(WEB_TIMEOUT)]
        # "อัตโนมัติ" ปรับตามเว็บให้เอง: YouTube เอาชัดสุดเสมอ (คลิปยาวไฟล์ใหญ่ก็ยอม)
        # เว็บอื่นจำกัดที่ 1080p (ถ้าไม่มีจะได้ 720p) เพราะสูงกว่านั้นมักเป็นไฟล์อัปสเกลที่ใหญ่เกินจำเป็น
        auto = opts["format"] == FORMATS[AUTO_FMT]
        res = opts.get("res") or 0
        if auto and is_youtube(url):
            opts = dict(opts, format=FORMATS[BEST_FMT])  # ความชัดตามที่ผู้ใช้ตั้ง ("สูงสุด" = ไม่จำกัด)
        elif auto and not res:
            res = AUTO_RES
        fmt = list(opts["format"])
        if opts.get("exclude"):
            # ตัดไฟล์ที่เพิ่งโหลดไม่ผ่านออก ให้ yt-dlp เลือกตัวที่ดีรองลงมา
            i = fmt.index("-f") + 1
            # ใช้ !~= (regex) เพราะ != ใช้กับ format_id ไม่ได้ผลใน yt-dlp
            ex = "".join(f"[format_id!~='^{re.escape(x)}$']" for x in opts["exclude"])
            fmt[i] = "/".join("+".join(p + ex if n == 0 else p for n, p in enumerate(alt.split("+")))
                              for alt in fmt[i].split("/"))
        args += fmt + opts["cookies"] + list(extra)
        # ห้ามข้ามชิ้นที่โหลดไม่ได้ (ไม่งั้นได้วิดีโอที่ขาดเป็นช่วงๆ) โดน 429 ให้รอนานขึ้นเรื่อยๆ แล้วลองใหม่
        args += ["--abort-on-unavailable-fragments", "--fragment-retries", "30",
                 "--retry-sleep", "fragment:exp=1:30", "--retries", "10"]
        if res:
            # เลือกตัวที่ชัดที่สุดที่ไม่เกินที่ตั้งไว้ ถ้าไม่มีจะเอาตัวที่ใกล้ที่สุดแทน (ไม่ error)
            # ถ้ารูปแบบที่เลือกมี -S ของตัวเองอยู่แล้ว ต้องเอาข้อจำกัดความชัดไปไว้หน้าสุดของอันนั้น
            if "-S" in args:
                i = args.index("-S") + 1
                args[i] = f"res:{res}," + args[i]
            else:
                args += ["-S", f"res:{res}"]
        if opts["aria2c"] and aria:
            args += ["--downloader", "aria2c", "--downloader-args", "aria2c:-x 16 -s 16 -k 1M"]
        # เว็บสตรีม (m3u8) จำกัดความเร็วต่อ connection ยิ่งโหลดหลายชิ้นพร้อมกันยิ่งเร็ว
        args += ["-N", str(opts.get("frags", 16))]
        if pathfile:
            args += ["--print-to-file", "after_move:filepath", pathfile]
        args.append(url)
        return args

    def start(self):
        if self.running or self.busy_updating:
            return
        if not any(it["status"] in (WAIT, WAIT_CONV) for it in self.items):
            self.var_status.set("ไม่มีลิงก์ที่รอโหลด")
            return
        self.opts = self._snapshot_options()
        os.makedirs(self.opts["out"], exist_ok=True)
        self.save_settings()
        self.running = True
        self.stopping = False
        self.btn_start.configure(state="disabled")
        self.btn_update.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        self._schedule()

    def _schedule(self):
        """ตัวจัดคิว: เรียกจาก main thread เท่านั้น เลยไม่ต้องล็อก"""
        if not self.running:
            return
        if not self.stopping:
            max_dl = to_int(self.var_max_dl, 3, 1, 8)
            max_conv = to_int(self.var_max_conv, 1, 1, 4)
            for it in self.items:
                if self.active_dl >= max_dl:
                    break
                if it["status"] == WAIT and self._check_existing(it):
                    continue
                if it["status"] == WAIT and it["progress"] == "กำลังดึงชื่อ ...":
                    # รอจนกว่าจะได้ชื่อ (หรือดึงไม่ได้) จะได้ตั้งชื่อไฟล์ไม่ให้ชนกับคลิปอื่นที่ชื่อเหมือนกัน
                    # ตัวดึงชื่อส่งผลกลับมาเสมอ ไม่ว่าสำเร็จหรือไม่ แถวนี้เลยไม่ค้างตลอดไป
                    continue
                if it["status"] == WAIT:
                    it["status"], it["progress"] = DL, "เริ่ม ..."
                    self._refresh(it)
                    self.active_dl += 1
                    name = it["title"] if it.get("custom_title") else ""
                    stem = pick_name(it["id"], self._dest(it), it["title"], it["url"],
                                     self.opts.get("name_max", NAME_MAX)) if it["title"] else ""
                    threading.Thread(target=self._download_job,
                                     args=(it["id"], it["url"], dict(self.opts, force=it["force"], name=name,
                                                                     stem=stem, out=self._dest(it))),
                                     daemon=True).start()
            for it in self.items:
                if self.active_conv >= max_conv:
                    break
                if it["status"] == WAIT_CONV and self.bench_ready:
                    it["status"], it["progress"] = CONV, "0%"
                    self._refresh(it)
                    self.active_conv += 1
                    o = dict(self.opts, encoder=enc_name(self.var_encoder.get()))
                    threading.Thread(target=self._convert_job, args=(it["id"], it["file"], o),
                                     daemon=True).start()
        self._update_summary()
        if self.active_dl == 0 and self.active_conv == 0 and (
                self.stopping or not any(i["status"] in (WAIT, WAIT_CONV) for i in self.items)):
            self._finish()

    def push_error_logs(self, wait=False):
        """ส่ง error log ขึ้น repo private (เบื้องหลัง) ถ้ามีไฟล์ใหม่"""
        def work():
            n = upload_error_logs()
            if n:
                self.events.put(("log", f"ส่ง error log ขึ้น GitHub แล้ว {n} ไฟล์"))

        t = threading.Thread(target=work, daemon=True)
        t.start()
        if wait:
            t.join(15)

    def _finish(self):
        self.running = False
        self.btn_start.configure(state="normal")
        self.btn_update.configure(state="normal")
        self.btn_stop.configure(state="disabled")
        failed = sum(1 for i in self.items if i["status"] == FAIL)
        self.var_status.set("หยุดแล้ว" if self.stopping else
                            f"คิวเสร็จแล้ว{f' (ล้มเหลว {failed})' if failed else ''}")
        self.save_queue()
        self.push_error_logs()
        if self.pending_update and not self.stopping:
            self.var_status.set("คิวเสร็จแล้ว กำลังอัปเดตแอป ...")
            self.after(1500, self._apply_app_update)

    def _update_summary(self):
        if not self.running:
            return
        cnt = lambda st: sum(1 for i in self.items if i["status"] == st)
        self.var_status.set(f"โหลด {cnt(DL)} | รอโหลด {cnt(WAIT)} | แปลง {cnt(CONV)} | รอแปลง {cnt(WAIT_CONV)}"
                            f" | เสร็จแล้ว {self.done_count}")

    def _download_job(self, item_id, url, opts):
        force = opts.get("force", False)
        post = lambda status, prog="": self.events.put(("item", item_id, status, prog, {}))
        pathfile = os.path.join(TMP_DIR, f"{item_id}.txt")
        try:
            os.remove(pathfile)
        except OSError:
            pass

        last = {"out": ""}

        def attempt(target, extra=(), outtmpl=None, aria=True, exclude=None):
            if opts.get("stem"):  # ชื่อที่เลือกไว้แล้ว ไม่ชนกับคลิปอื่นที่ชื่อเหมือนกัน
                outtmpl = opts["stem"].replace("%", "%%") + ".%(ext)s"
            elif opts.get("name"):  # ผู้ใช้ตั้งชื่อเอง
                outtmpl = safe_filename(opts["name"], opts.get("name_max", NAME_MAX)) + ".%(ext)s"
            o = dict(opts, exclude=exclude) if exclude else opts
            args = self.build_args(target, o, pathfile, extra, outtmpl, aria)
            self.events.put(("log", f"[#{item_id}] > " + subprocess.list2cmdline(args[1:])))
            out = []
            st = {"t": time.time(), "bytes": None, "active": False, "stalled": False, "gone": 0}

            def on_line(line):
                m = PROG_RE.match(line.strip())
                if m:
                    pct, spd, eta, got = m.groups()
                    if got != st["bytes"]:
                        st["bytes"], st["t"] = got, time.time()
                    st["active"] = float(pct) < 100
                    post(DL, f"{float(pct):.1f}%  {spd.strip()}  ETA {eta.strip()}")
                    return
                st["active"] = False  # ช่วงรวมไฟล์/แก้ไฟล์ไม่มี progress ไม่นับว่าค้าง
                if "Retrying fragment" in line and ("404" in line or "410" in line):
                    st["gone"] += 1
                    if st["gone"] == DEAD_FRAGS:
                        # ชิ้นไฟล์หายจริงๆ รอไปก็ไม่มา ตัดเลยแล้วไปลอง server อื่น
                        self.events.put(("log", f"[#{item_id}] ชิ้นไฟล์หาย (404) หลายรอบ "
                                                f"สตรีมนี้น่าจะตายแล้ว ข้ามไปลอง server อื่น"))
                        with self.procs_lock:
                            pr = self.procs.get(("dl", item_id))
                        if pr and pr.poll() is None:
                            subprocess.run(["taskkill", "/PID", str(pr.pid), "/T", "/F"],
                                           capture_output=True, creationflags=NO_WINDOW)
                out.append(line)
                self.events.put(("log", f"[#{item_id}] {line}"))
                if "[Merger]" in line:
                    post(DL, "กำลังรวมไฟล์ ...")
                elif "aria2c" in line:
                    post(DL, "aria2c ...")

            def watchdog(done):
                """ถ้าขนาดไฟล์ไม่เพิ่มเลย STALL_SEC วินาที ให้ฆ่า yt-dlp (แล้วค่อยรันใหม่ให้โหลดต่อจากเดิม)"""
                while not done.wait(5):
                    if st["active"] and time.time() - st["t"] > STALL_SEC and not self.stopping:
                        st["stalled"] = True
                        with self.procs_lock:
                            p = self.procs.get(("dl", item_id))
                        if p and p.poll() is None:
                            subprocess.run(["taskkill", "/PID", str(p.pid), "/T", "/F"],
                                           capture_output=True, creationflags=NO_WINDOW)
                        return

            for n in range(STALL_RETRIES + 1):
                st.update(t=time.time(), active=False, stalled=False)
                done = threading.Event()
                threading.Thread(target=watchdog, args=(done,), daemon=True).start()
                try:
                    rc = self._run_proc(args, on_line, key=("dl", item_id))
                except OSError as e:
                    self.events.put(("log", f"[#{item_id}] รันไม่ได้: {e}"))
                    rc = -1
                finally:
                    done.set()
                if not st["stalled"] or self.stopping or n == STALL_RETRIES:
                    break
                # yt-dlp จำชิ้นที่โหลดแล้วไว้ในไฟล์ .ytdl รันใหม่ด้วยคำสั่งเดิมจะโหลดต่อจากที่ค้าง
                self.events.put(("log", f"[#{item_id}] ค้างไม่ขยับ {STALL_SEC} วินาที "
                                        f"ตัดแล้วโหลดต่อจากเดิม (ครั้งที่ {n + 1}/{STALL_RETRIES})"))
                post(DL, f"ค้าง โหลดต่อจากเดิม ({n + 1}/{STALL_RETRIES}) ...")
            if st["stalled"] and rc != 0:
                out.append("ERROR: stalled - ค้างหลายรอบ")
            last["out"] = "\n".join(out[-50:])
            return rc, last["out"]

        def attempt_lower(target, extra=(), outtmpl=None, aria=True):
            """โหลดแบบปกติ ถ้าโดน 403/404 ที่ตัวไฟล์ ให้ตัดไฟล์นั้นออกแล้วเอาตัวที่ชัดรองลงมา (บางเว็บบล็อกเฉพาะตัวชัดสุด)"""
            rc, out = attempt(target, extra, outtmpl, aria)
            failed = []
            for _ in range(3):
                if rc == 0 or self.stopping or not re.search(r"HTTP Error 40[34]|unable to download video data", out):
                    break
                ids = re.findall(r"Downloading \d+ format\(s\): (\S+)", out)
                if not ids:
                    break
                failed.append(ids[-1].split("+")[0])
                self.events.put(("log", f"[#{item_id}] ไฟล์ความชัดนี้ (format {failed[-1]}) โหลดไม่ได้ "
                                        f"({fail_reason(out)}) ลองตัวที่ชัดรองลงมา"))
                post(DL, "ลองความชัดรองลงมา ...")
                rc, out = attempt(target, extra, outtmpl, aria, exclude=failed)
            return rc, out

        def via_page():
            """เว็บที่ yt-dlp ไม่รู้จัก: อ่านหน้าเว็บเอง หาลิงก์วิดีโอจากทุก server
            เลือก server ที่ชัดที่สุดก่อน ถ้าโหลดไม่ผ่านค่อยเปลี่ยน server ถัดไป"""
            note = lambda m: (self.events.put(("notice", f"[#{item_id}] {m}")), post(DL, m.split(" ...")[0] + " ..."))
            post(DL, "กำลังหาลิงก์วิดีโอในหน้าเว็บ ...")
            cur = url  # ลิงก์ที่ใช้จริง (เว็บอาจย้ายวันที่ใน URL ไปแล้ว)
            page = fetch_page(cur, notify=lambda m: note("กำลังผ่าน Cloudflare ..."))
            if page and GONE_TITLE_RE.search(page_title(page) or ""):
                post(DL, "หน้าคลิปย้ายที่ กำลังค้นหาใหม่ ...")
                moved = find_moved_url(cur)
                if moved:
                    self.events.put(("log", f"[#{item_id}] หน้าคลิปย้ายไปที่ {moved} โหลดจากที่ใหม่"))
                    cur, page = moved, fetch_page(moved)
                if not page or GONE_TITLE_RE.search(page_title(page) or ""):
                    self.events.put(("log", f"[#{item_id}] หน้าคลิปนี้ไม่มีบนเว็บแล้ว (404)"))
                    return PAGE_GONE
            title = opts.get("name") or page_title(page)
            if title and not opts.get("name"):
                self.events.put(("title", item_id, title))
                f = "" if force else find_existing(opts["out"], title, url)
                if f:
                    self.events.put(("log", f"[#{item_id}] มีไฟล์อยู่แล้ว ไม่โหลดซ้ำ: {f}"))
                    return "have:" + f
            gone = [False]  # เว็บบอกเองว่าคลิปถูกลบ ไม่ต้องลองซ้ำ

            def gather(page):
                """หาลิงก์วิดีโอจากหน้านี้ คืน (ตัวหลักของแต่ละ server, ลิงก์สำรองของ player เดียวกัน)"""
                cands, spare = [], []
                media = find_media(page) if not is_7mm(cur) else ""  # 7mmtv มีคลิปตัวอย่างอื่นปนในหน้า
                if media:
                    return [("หน้าเว็บ", media, cur)], spare
                servers = get_servers(cur, page, notify=note)
                if not servers and not self.stopping:
                    self.events.put(("log", f"[#{item_id}] ยังไม่เจอ server ลองอ่านหน้าเว็บอีกรอบ"))
                    servers = get_servers(cur, fetch_page(cur) or page, notify=note)
                for name, embed in servers:
                    if self.stopping:
                        break
                    post(DL, f"กำลังเช็ค server {name} ...")
                    links, ref, dead = resolve_embed_links(embed, cur)
                    if not links and not dead and not fetch_with_referer(embed, cur):
                        self.events.put(("log", f"[#{item_id}] server {name}: หน้า player ไม่ตอบอะไรเลย"))
                    if dead:
                        self.events.put(("log", f"[#{item_id}] server {name}: เว็บบอกว่าคลิปนี้ถูกลบ"
                                                f"หรือหมดอายุไปแล้ว"))
                        gone[0] = True
                    if links:
                        cands.append((name, links[0], ref))
                        for n, alt in enumerate(links[1:3]):  # ลิงก์สำรองของ player ตัวเดียวกัน
                            spare.append((f"{name} (สำรอง {n + 1})", alt, ref))
                    else:
                        self.events.put(("log", f"[#{item_id}] server {name}: หาลิงก์วิดีโอไม่เจอ"))
                return cands, spare

            fname = None
            if title and not opts.get("stem"):
                fname = pick_name(item_id, opts["out"], title, url,
                                  opts.get("name_max", NAME_MAX)).replace("%", "%%")
            rc, cands = -1, []
            # โฮสต์ของ CDN สุ่มใหม่ทุกครั้งที่เปิดหน้าเว็บ ถ้าชุดนี้ล่มทั้งหมด ขอชุดใหม่แล้วลองอีกรอบ
            for rnd in range(2):
                if self.stopping:
                    break
                if rnd:
                    self.events.put(("log", f"[#{item_id}] ลิงก์ชุดนี้ใช้ไม่ได้ทั้งหมด ขอลิงก์ชุดใหม่จากเว็บอีกรอบ"))
                    post(DL, "ขอลิงก์ชุดใหม่ ...")
                    page = fetch_page(cur) or page
                cands, spare = gather(page)
                if not cands:
                    if gone[0]:
                        break
                    continue
                if len(cands) > 1:
                    scored = []
                    for name, m, ref in cands:
                        post(DL, f"กำลังเช็คความชัด server {name} ...")
                        q = probe_quality(m, ref, opts.get("res", 0))
                        self.events.put(("log", f"[#{item_id}] server {name}: " +
                                         (f"{q[0]}p {q[1]:.0f}k" if q else "ใช้ไม่ได้")))
                        if q:
                            scored.append((q, name, m, ref))
                    scored.sort(key=lambda x: x[0], reverse=True)
                    cands = [(n, m, r) for _, n, m, r in scored] or cands
                for name, m, ref in cands + spare:
                    if self.stopping:
                        break
                    self.events.put(("log", f"[#{item_id}] โหลดจาก server {name}: {m}"))
                    origin = re.match(r"https?://[^/]+", ref).group(0)
                    extra = ["--impersonate", "chrome", "--referer", ref, "--add-headers", f"Origin:{origin}"]
                    # aria2c ปลอมตัวเป็น Chrome ไม่ได้ เลยใช้ตัวโหลดของ yt-dlp แทน
                    rc = attempt_lower(m, extra, (fname + ".%(ext)s") if fname else None, aria=False)[0]
                    if rc == 0:
                        return rc
                    self.events.put(("log", f"[#{item_id}] server {name} โหลดไม่ผ่าน ลองลิงก์ถัดไป"))
            if not cands:
                if gone[0]:
                    return DEAD_CLIP
                self.events.put(("log", f"[#{item_id}] หาลิงก์วิดีโอในหน้าเว็บไม่เจอ"))
                return NO_MEDIA
            return rc

        if is_page_site(url) or url_host(url) in NO_YTDLP_HOSTS:
            rc = via_page()
        else:
            rc, out = attempt_lower(url)
            if rc != 0 and not self.stopping:
                if "Unsupported URL" in out:
                    NO_YTDLP_HOSTS.add(url_host(url))
                    rc = via_page()
                elif "impersonat" in out:
                    self.events.put(("log", f"[#{item_id}] โดน Cloudflare ลองใหม่แบบปลอมตัวเป็น Chrome"))
                    rc, out = attempt_lower(url, ["--impersonate", "chrome"], aria=False)
                    if rc != 0 and not self.stopping:
                        self.events.put(("log", f"[#{item_id}] yt-dlp อ่านเว็บนี้ไม่ได้ ลองอ่านหน้าเว็บเอง"))
                        NO_YTDLP_HOSTS.add(url_host(url))
                        rc = via_page()
        files = []
        try:
            with open(pathfile, encoding="utf-8") as f:
                files = [l.strip() for l in f if l.strip()]
            os.remove(pathfile)
        except OSError:
            pass
        file = files[-1] if files else ""
        if isinstance(rc, str) and rc.startswith("have:"):
            self.events.put(("have", item_id, rc[5:]))
            return
        reason = {NO_MEDIA: "หาลิงก์วิดีโอไม่เจอ",
                  DEAD_CLIP: "เว็บลบคลิปนี้ไปแล้ว",
                  PAGE_GONE: "หน้าคลิปนี้ไม่มีบนเว็บแล้ว"}.get(rc) or fail_reason(last["out"])
        self.events.put(("dl_done", item_id, rc, file, reason, last["out"]))

    def _convert_job(self, item_id, src, opts):
        post = lambda prog: self.events.put(("item", item_id, CONV, prog, {}))
        ext = opts["container"]
        base = os.path.splitext(src)[0]
        dst = base + "." + ext
        tmp = base + ".h265-tmp." + ext
        dur = [0.0]
        errs = []

        def on_line(line):
            m = DUR_RE.search(line)
            if m and not dur[0]:
                h, mi, se = m.groups()
                dur[0] = int(h) * 3600 + int(mi) * 60 + float(se)
            m = TIME_RE.search(line)
            if m:
                h, mi, se, spd = m.groups()
                t = int(h) * 3600 + int(mi) * 60 + float(se)
                pct = f"{min(t / dur[0] * 100, 100):.1f}%" if dur[0] else ""
                post(f"{pct}  {spd}")
            elif "error" in line.lower() or "invalid" in line.lower():
                errs.append(line)
                self.events.put(("log", f"[#{item_id}] {line}"))

        def run(enc_name):
            pre, vargs = encode_args(enc_name, opts["crf"], opts["preset"])
            args = [FFMPEG, "-hide_banner", "-y", *pre, "-i", src, "-map", "0:v:0", "-map", "0:a?",
                    *vargs, "-c:a", "aac", "-b:a", "128k"]
            if ext == "mp4":
                args += ["-tag:v", "hvc1", "-movflags", "+faststart"]
            args.append(tmp)
            self.events.put(("log", f"[#{item_id}] > ffmpeg " + subprocess.list2cmdline(args[1:])))
            try:
                return self._run_proc(args, on_line, key=("conv", item_id))
            except OSError as e:
                self.events.put(("log", f"[#{item_id}] รัน ffmpeg ไม่ได้: {e}"))
                return -1

        rc = run(opts["encoder"])
        if rc != 0 and opts["encoder"] != CPU_ENC and not self.stopping and item_id not in self.cancelled:
            self.events.put(("log", f"[#{item_id}] แปลงด้วย {opts['encoder']} ไม่ผ่าน ลองใหม่ด้วย CPU"))
            rc = run(CPU_ENC)
        if rc == 0 and os.path.isfile(tmp) and item_id not in self.cancelled:
            try:
                os.remove(src)
                os.replace(tmp, dst)
                self.events.put(("log", f"[#{item_id}] แปลงเสร็จ: {dst}"))
            except OSError as e:
                self.events.put(("log", f"[#{item_id}] เปลี่ยนชื่อไฟล์ไม่ได้: {e}"))
                rc = 1
        else:
            try:
                os.remove(tmp)
            except OSError:
                pass
        self.events.put(("conv_done", item_id, rc, dst, f"encoder: {opts['encoder']}\n" + "\n".join(errs[-40:])))

    def stop(self):
        if not self.running:
            return
        self.stopping = True
        with self.procs_lock:
            procs = list(self.procs.values())
        for p in procs:
            if p.poll() is None:
                subprocess.run(["taskkill", "/PID", str(p.pid), "/T", "/F"],
                               creationflags=NO_WINDOW, capture_output=True)
        self.var_status.set("กำลังหยุด ...")
        self._schedule()

    # ---------- events from threads ----------
    def _pump(self):
        changed = False
        try:
            while True:
                ev = self.events.get_nowait()
                kind = ev[0]
                if kind == "log":
                    self.write_log(ev[1])
                elif kind == "title":
                    it = self._find(ev[1])
                    if it:
                        if ev[2] and not it.get("custom_title"):
                            it["title"] = ev[2]
                        if it["status"] == WAIT:
                            it["progress"] = "" if ev[2] else "ดึงชื่อไม่ได้"
                        self._refresh(it)
                        self._check_existing(it)
                        changed = True  # ได้ชื่อแล้ว เริ่มโหลดแถวที่รอชื่ออยู่ได้
                elif kind == "item":
                    _, item_id, status, prog, kw = ev
                    it = self._find(item_id)
                    if it and it["status"] == status:
                        it["progress"] = prog
                        self._refresh(it)
                elif kind == "dl_done":
                    _, item_id, rc, file, reason, detail = ev
                    self.active_dl -= 1
                    release_name(item_id)
                    it = self._find(item_id)
                    if it:
                        if file:
                            it["file"] = file
                            if rc == 0:
                                remember_source(it["url"], file)
                            if not it["title"]:
                                it["title"] = os.path.basename(file)
                        if self.stopping:
                            it["status"], it["progress"] = STOPPED, ""
                        elif rc != 0:
                            it["status"], it["progress"] = FAIL, f"โหลดไม่ได้: {reason}" if reason else f"โหลดไม่ได้ (exit {rc})"
                            log_error("download", it["progress"], detail, it["url"])
                        elif not it["convert"]:
                            it["status"], it["progress"] = DONE, "100%"
                        elif file and os.path.isfile(file):
                            it["status"], it["progress"] = WAIT_CONV, "โหลดเสร็จ รอแปลง"
                        else:
                            it["status"], it["progress"] = FAIL, "หาไฟล์ที่โหลดไม่เจอ"
                            log_error("download", it["progress"], detail, it["url"])
                        self._refresh(it)
                    changed = True
                elif kind == "expanded":
                    _, src, links, folder = ev
                    if links:
                        added = 0
                        for u in links:
                            if self._add_item(u, save=False, subdir=folder):
                                added += 1
                        self.write_log(f"คลิปจากหน้านี้จะโหลดลงโฟลเดอร์ย่อย: {folder}")
                        self.save_queue()
                        msg = (f"แกะได้ {len(links)} ลิงก์ เพิ่มเข้าคิว {added}"
                               + (f" (ซ้ำ {len(links) - added})" if len(links) - added else ""))
                    else:
                        msg = "แกะลิงก์จากหน้านี้ไม่ได้ (ไม่เจอลิงก์คลิป) ลองวางลิงก์ของคลิปแต่ละอันแทน"
                    self.write_log(f"{msg}: {src}")
                    self.var_status.set(msg)
                elif kind == "have":
                    _, item_id, f = ev
                    self.active_dl -= 1
                    release_name(item_id)
                    it = self._find(item_id)
                    if it:
                        it["status"], it["file"] = HAVE, f
                        it["progress"] = os.path.basename(f) if f else "เคยโหลดแล้ว"
                        self._refresh(it)
                    changed = True
                elif kind == "conv_done":
                    _, item_id, rc, dst, detail = ev
                    self.active_conv -= 1
                    it = self._find(item_id)
                    if it:
                        self.cancelled.discard(item_id)
                        if it["cancel_conv"]:
                            it["cancel_conv"] = False
                            it["status"], it["progress"] = DONE, "โหลดแล้ว (ยกเลิกแปลง)"
                        elif self.stopping:
                            it["status"], it["progress"] = STOPPED, "ยังไม่ได้แปลง"
                        elif rc == 0:
                            it["status"], it["progress"], it["file"] = DONE, "100% (H.265)", dst
                            it["converted"] = True
                        else:
                            it["status"], it["progress"] = FAIL, f"แปลงไม่ได้ (exit {rc})"
                            log_error("convert", it["progress"], detail, it["url"])
                        self._refresh(it)
                    changed = True
                elif kind == "ext_add":
                    _, urls, go = ev
                    self.write_log(f"รับลิงก์จาก Chrome Extension {len(urls)} ลิงก์")
                    self.add_urls("\n".join(urls))
                    if go:
                        self.autostart = True
                    if self.tray:
                        try:
                            self.tray.notify(tr(f"รับลิงก์จาก Chrome Extension {len(urls)} ลิงก์"), APP_NAME)
                        except Exception:
                            pass
                elif kind == "tray_show":
                    self.show_window()
                elif kind == "tray_start":
                    self.start()
                elif kind == "tray_exit":
                    self.show_window()
                    self.on_close()
                    return
                elif kind == "status":
                    self.var_status.set(ev[1])
                elif kind == "notice":
                    self.write_log(ev[1])
                    self.var_status.set(ev[1])
                elif kind == "encoders":
                    res = ev[1]
                    labels = [enc_label(n, f) for n, f in res]
                    best = pick_best(res)
                    self.cmb_encoder.configure(values=labels)
                    self.var_encoder.set(next(l for l in labels if enc_name(l) == best))
                    self.bench_ready = True
                    self._schedule()
                    self.write_log("ทดสอบตัวแปลง (1080p): " + " | ".join(labels) + f"  => เลือก {best}")
                elif kind == "app_update":
                    _, tag, path = ev
                    self.pending_update = path
                    if self.running:
                        self.write_log(f"โหลดแอป {tag} มาแล้ว จะติดตั้งให้ตอนคิวเสร็จ")
                    else:
                        self.write_log(f"ติดตั้งแอป {tag} แล้วเปิดใหม่ ...")
                        self.var_status.set(f"กำลังอัปเดตแอปเป็น {tag} ...")
                        self.after(1500, self._apply_app_update)
                elif kind == "update_done":
                    self.busy_updating = False
                    self.btn_start.configure(state="normal")
                    self.btn_update.configure(state="normal")
                    self.var_status.set("อัปเดตเสร็จ พร้อมโหลด" if ev[1] == 0 else "อัปเดตเครื่องมือบางตัวไม่สำเร็จ (ดู Log)")
        except queue.Empty:
            pass
        if changed:
            self.save_queue()
            self._schedule()
        self._auto_clear()
        if (self.autostart and not self.running and not self.busy_updating
                and any(i["status"] in (WAIT, WAIT_CONV) for i in self.items)):
            self.autostart = False
            self.start()
        now = time.time()
        if now - getattr(self, "_tray_t", 0) >= 1:
            self._tray_t = now
            self._update_tray()
        self.after(100, self._pump)

    def _auto_clear(self):
        """ล้างแถวที่เสร็จ/มีแล้วออกจากคิวเอง หลังโชว์ผลไว้ AUTO_CLEAR_SEC วินาที (บันทึกลง Log ไว้ดูย้อนหลัง)"""
        now = time.time()
        gone = []
        for it in self.items:
            if it["status"] in (DONE, HAVE):
                if "done_at" not in it:
                    it["done_at"] = now
                    self.done_count += 1
                    name = os.path.basename(it["file"]) if it["file"] else it["title"] or it["url"]
                    self.write_log(("✔ เสร็จ: " if it["status"] == DONE else "✔ มีแล้ว: ") + name)
                elif self.var_auto_clear.get() and now - it["done_at"] >= AUTO_CLEAR_SEC:
                    gone.append(it)
            else:
                it.pop("done_at", None)
        if gone:
            for it in gone:
                self.tree.delete(it["iid"])
                self.items.remove(it)
            self._renumber()
            self._update_summary()

    # ---------- System Tray ----------
    def _setup_tray(self):
        """ไอคอนใน System Tray: ย่อหน้าต่างแล้วไปอยู่ที่นี่ สีบอกสถานะ ชี้เมาส์ดูรายละเอียด"""
        try:
            from PIL import ImageTk
            self._win_icon = ImageTk.PhotoImage(make_status_icon(TRAY_COLORS["busy"], 32))
            self.iconphoto(True, self._win_icon)
        except Exception:
            pass
        try:
            import pystray
        except ImportError:
            return
        menu = pystray.Menu(
            pystray.MenuItem(lambda item: tr("เปิดหน้าต่าง"), lambda *a: self.events.put(("tray_show",)), default=True),
            pystray.MenuItem(lambda item: tr("เริ่มโหลด"), lambda *a: self.events.put(("tray_start",))),
            pystray.MenuItem(lambda item: tr("ออกจากโปรแกรม"), lambda *a: self.events.put(("tray_exit",))))
        self.tray = pystray.Icon(APP_NAME, make_status_icon(TRAY_COLORS["idle"]), APP_NAME, menu)
        try:
            self.tray.run_detached()
        except Exception:
            self.tray = None
            return
        self.bind("<Unmap>", self._on_unmap)
        self._update_tray()

    def _on_unmap(self, e):
        # กดย่อ (minimize) = ซ่อนหน้าต่างไปอยู่ใน System Tray
        if e.widget is self and self.tray and self.state() == "iconic":
            self.after(10, self.withdraw)

    def show_window(self):
        self.deiconify()
        self.state("normal")
        self.lift()
        self.focus_force()

    def _tray_status(self):
        cnt = lambda *st: sum(1 for i in self.items if i["status"] in st)
        dl, conv, wait = cnt(DL), cnt(CONV), cnt(WAIT, WAIT_CONV)
        fail = cnt(FAIL)
        if dl or conv:
            state = "busy"
            text = tr("กำลังโหลด") + f" {dl}" + (f" · {tr('กำลังแปลง')} {conv}" if conv else "")
            if wait:
                text += f" · {tr('รอ')} {wait}"
        elif wait:
            state, text = "wait", tr("รอโหลด") + f" {wait}"
        elif self.done_count or fail:
            state, text = "done", tr("เสร็จหมดแล้ว") + f" ({self.done_count})"
        else:
            state, text = "idle", tr("พร้อม")
        if fail:
            text += f" · {tr('ล้มเหลว')} {fail}"
        return state, f"{APP_NAME} v{APP_VERSION}\n{text}"[:127]

    def _update_tray(self):
        if not self.tray:
            return
        state, text = self._tray_status()
        if state != self.tray_state:
            self.tray_state = state
            self.tray.icon = make_status_icon(TRAY_COLORS[state])
        if self.tray.title != text:
            self.tray.title = text

    def destroy(self):
        if getattr(self, "ext_server", None):
            try:
                self.ext_server.shutdown()
            except Exception:
                pass
            self.ext_server = None
        if getattr(self, "tray", None):
            try:
                self.tray.stop()
            except Exception:
                pass
            self.tray = None
        super().destroy()

    def on_close(self):
        if self.running and not messagebox.askyesno(APP_NAME, tr("กำลังโหลด/แปลงอยู่ จะปิดและหยุดเลยไหม") + "?"):
            return
        self.stop()
        self.push_error_logs(wait=True)
        if self.pending_update:
            self._apply_app_update()
            return
        self.save_settings()
        self.save_queue()
        self.destroy()


def _install_crash_logging(app):
    import traceback

    def hook(exc_type, exc, tb):
        log_error("crash", f"{exc_type.__name__}: {exc}", "".join(traceback.format_exception(exc_type, exc, tb)))

    sys.excepthook = hook
    threading.excepthook = lambda a: hook(a.exc_type, a.exc_value, a.exc_traceback)
    app.report_callback_exception = hook


if __name__ == "__main__":
    app = App()
    _install_crash_logging(app)
    app.mainloop()
