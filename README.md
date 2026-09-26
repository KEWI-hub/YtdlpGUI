# YtdlpGUI

**[English](#english)** · **[ภาษาไทย](#ภาษาไทย)**

> Built with [Claude](https://claude.ai) (Anthropic) · สร้างด้วย Claude

---

## English

A Windows GUI for [yt-dlp](https://github.com/yt-dlp/yt-dlp): paste links into a queue, download several at once, and optionally convert to H.265 on your GPU.

This app, its `setup.bat` and this README were written with **Claude** (Anthropic's AI assistant, via Claude Code), based on the owner's requests and testing.

### Quick start

**Easiest: the all-in-one zip.** On the [Releases](https://github.com/KEWI-hub/YtdlpGUI/releases/latest) page grab **`YtdlpGUI-vX.Y.Z-full.zip`** (about 200 MB), extract it anywhere and double-click `YtdlpGUI.exe`. The tools in `bin\` are already inside, so nothing else has to be installed or downloaded. If you only take `YtdlpGUI.exe`, the app notices that `bin\` is empty on the first run and offers to download the missing tools for you (about 150 MB) - press **Yes** and wait; no `setup.bat` needed.

Or set it up from the repo:

1. Download or clone this repo.
2. Double-click **`setup.bat`**. It downloads the required tools into `bin\` (about 250 MB) and takes around 15–60 seconds.
3. `setup.bat` also downloads **`YtdlpGUI.exe`** from the latest **Release**. If that is not possible (e.g. the repo is private), it offers to build it with Python 3.11+ (answer `Y`).
4. Open `YtdlpGUI.exe`, paste a link with **Ctrl+V**, pick the download folder and press **▶ เริ่มโหลด** (Start).

Run `setup.bat force` later to update every tool to the newest version.

### Files that are *not* in this repo (and why)

| File / folder | Why it is not uploaded | How to get it |
|---|---|---|
| `bin\yt-dlp.exe` | Third-party program | `setup.bat` → [yt-dlp releases](https://github.com/yt-dlp/yt-dlp/releases) |
| `bin\ffmpeg.exe`, `bin\ffprobe.exe` | ~160–190 MB each, **over GitHub's 100 MB file limit** | `setup.bat` → [yt-dlp/FFmpeg-Builds](https://github.com/yt-dlp/FFmpeg-Builds/releases) (win64-gpl) |
| `bin\deno.exe` | Third-party program (~90 MB) | `setup.bat` → [deno releases](https://github.com/denoland/deno/releases) |
| `bin\aria2c.exe` | Third-party program | `setup.bat` → [aria2 releases](https://github.com/aria2/aria2/releases) |
| `YtdlpGUI.exe` | Build output, published under **Releases** instead | Releases page, or `setup.bat` builds it with Python |
| `_browser\` | The app's private Chrome profile, **contains cookies** | Created automatically |
| `settings.json`, `queue.json` | Personal settings, local paths and your download links | Created automatically |
| `_tmp\`, `build\`, downloaded videos | Temporary / personal files | — |

All of these are listed in `.gitignore`, so they are never committed by accident.

### Chrome extension (one-click download)

The `chrome-extension\` folder is a small Chrome extension that sends links straight to the app.

**Install (once).** After updating the app, press **Reload** on the extension card in `chrome://extensions` too.

**Install steps:**
1. Open `chrome://extensions` in Chrome.
2. Turn on **Developer mode** (top-right).
3. Click **Load unpacked** and select the `chrome-extension` folder of this project.
4. (Optional) Pin the extension to the toolbar.

**Use** (YtdlpGUI must be open, even minimized to the tray):
- Click the extension icon, or press **Alt+Shift+D**, to download the page you are on.
- Right-click any link → **Download link with YtdlpGUI**.
- A green ✓ badge (shown for 1 second) means the link reached the app and the download starts automatically. A red ! means the app is not running.

It only talks to `127.0.0.1:47777` on your own computer. The app accepts links only from the extension (requests must carry the `X-YtdlpGUI` header), so web pages cannot add downloads.

### System tray

Minimizing the window hides it in the system tray. The icon color shows what the app is doing, and hovering shows the details:

| Color | Meaning |
|---|---|
| 🟡 Yellow | Clips waiting to download / convert |
| 🔵 Blue | Downloading or converting |
| 🟢 Green | All done |
| ⚪ Gray | Idle, nothing in the queue |

Click the icon to open the window again. Right-click it for Start / Exit.

### Language

Menu **Language / ภาษา** → English or ไทย. English is the default. The app restarts to apply it, and the queue is kept.

### Tool updates

Every time the app starts (with "Check updates on start" ticked) it checks all tools in `bin\` against their GitHub releases and updates any that are newer: yt-dlp, ffmpeg + ffprobe (a new build almost every day, ~190 MB), deno and aria2c. Missing tools are downloaded too. New files are downloaded first and swapped in afterwards, so a failed download never breaks the old tool. The **Update tools** button runs the same check at any time.

### Error logs

- Nothing is written to disk during normal use. The Log box on screen is not saved.
- Only errors are written to `logs\errors-YYYY-MM-DD.log`: failed downloads (with the last yt-dlp output), failed conversions (with ffmpeg errors) and unexpected crashes (with a traceback). Your Windows user name in paths is replaced by `~`.
- On the owner's computer the logs are pushed to the **private** repo `KEWI-hub/YtdlpGUI-logs` (15 s after start, when the queue finishes, and on exit), so they can be analyzed and fixed. Other computers have no permission and just keep the local file.

### Automatic app updates

Every time the app starts (when "เช็คอัปเดตตอนเปิด" / check for updates on start is ticked) it compares its own version (shown in the window title, e.g. `YtdlpGUI v1.1.0`) with the latest GitHub Release:

1. If GitHub has a newer version, it downloads the new `YtdlpGUI.exe` in the background.
2. If nothing is downloading, it closes, swaps the exe and reopens by itself (queue and settings are kept). If the queue is running, it waits until the queue finishes, or installs when you close the app.
3. If GitHub cannot be reached, it just skips the check.

### Contributing (fork + pull request)

- Only the owner (**KEWI-hub**) pushes to this repo. Please do **not** ask for collaborator access.
- To change something: **Fork** → edit in your fork → open a **Pull Request** back to `main`. The owner reviews and merges.
- Keep the README (English + Thai) updated in the same PR, and never commit `bin\`, `*.exe`, `_browser\`, `settings.json` or `queue.json`.

### Releasing a new version (owner)

1. Change `APP_VERSION` at the top of `ytdlp_gui.py` (e.g. `1.2.0`) and add a changelog entry to the README.
2. Commit and push, then push a tag with the same number: `git tag v1.2.0` and `git push origin v1.2.0`.
3. GitHub Actions (`.github/workflows/release.yml`) builds `YtdlpGUI.exe` and publishes the Release. Every installed app updates itself on its next start.

### Requirements

- Windows 10 (1803+) or 11, 64-bit. `setup.bat` uses the built-in `curl` and `tar`.
- Google Chrome or Microsoft Edge, only needed for sites protected by Cloudflare.
- Optional: NVIDIA / AMD / Intel GPU for fast H.265 conversion (falls back to CPU).
- To build from source: Python 3.11+ and the packages in `requirements.txt`.

### Features

- **Queue**: Ctrl+V adds links instantly (works with the Thai keyboard layout too). Titles are fetched automatically.
- **Parallel downloads**: 1–8 links at once, plus 1–32 parallel fragments per stream (m3u8).
- **Resolution**: best / 1080p / 720p.
- **Per-clip H.265 conversion**: tick ☑ in the "แปลง" (convert) column. A separate conversion queue runs while downloads continue.
- **GPU auto-pick**: benchmarks NVENC / AMF / QSV / x265 at every start and picks the best. You can change it in the dropdown.
- **Listing pages**: paste a search / category / tag / actor / channel page and every clip link is added (follows up to 50 pages), saved into a sub-folder named after the page.
- **Sites yt-dlp does not support**: reads the page itself, finds the m3u8/mp4, tries every server and picks the sharpest one, then falls back to the next server or a lower resolution on 403. When the page's player lists several links (`hls2`/`hls3`/`hls4`), it takes the same one the player itself plays — on these sites that is 100x+ faster than the first link in the page.
- **Cloudflare**: curl_cffi first, then a hidden Chrome, then a visible Chrome window where *you* click "Verify you are human" (the app never clicks it for you).
- **No duplicates**: same clip in the queue (compared by clip ID, not raw URL) and files that already exist in the target folder are skipped ("มีแล้ว" = already have).
- **Same title, different clips**: both are downloaded. The second one is saved as `Title (2).mp4`, the third as `Title (3).mp4`, and so on. The app remembers which link each file came from (`sources.json`), so a same-title file from another link is never treated as "already have" and is never overwritten.
- **Right-click menu**: reset status, force re-download, edit link, edit name (used as the file name), open file / folder, extract links from a page.
- **Auto-clear**: finished rows disappear after 5 seconds and are logged.
- **Safe fragments**: never skips a missing fragment. It waits and retries on HTTP 429 instead of producing a broken video.
- **Tray icon** with status colors, **English / Thai UI**, **Chrome extension** for one-click downloads, **auto-updating tools**, and **error-only logs** pushed to a private repo.
- **Stall watchdog**: if a download stops growing for 90 s (e.g. stuck at 99.9%), the app restarts it and resumes from where it stopped, up to 5 times.
- Updates all tools and the app itself every time it starts, and remembers the queue between runs.

### Main settings

| Setting (Thai label) | Default | Meaning |
|---|---|---|
| โหลดลง (Save to) | — | Download folder |
| รูปแบบ (Format) | MP4 direct | Direct MP4 without m3u8, or best video+audio merged |
| ความชัด (Resolution) | best | best / 1080p / 720p (never above the limit; falls back to the nearest) |
| Cookies จาก (Cookies from) | firefox | Browser to read cookies from, for age-gated or login-only clips |
| ใช้ aria2c | on | Multi-connection downloader for normal sites |
| โหลดพร้อมกัน (Parallel links) | 3 | Links downloading at the same time |
| หน้ารวมสูงสุด (Max listing pages) | 5 | Pages to follow when extracting a listing page |
| ชื่อไฟล์ยาวสุด (Max file name) | 70 | Max file name length in characters, extension not counted. File names are the title only (no clip id) |
| ชิ้นส่วนพร้อมกัน (Parallel fragments) | 16 | m3u8 fragments per link. More is faster; lower it if you get 429 |
| ตัวแปลง (Encoder) | auto | NVENC / AMF / QSV / CPU x265 |
| ไฟล์ / คุณภาพ / Preset | mp4 / 24 / slow | Output container, quality (lower = sharper, bigger) and speed preset |
| แปลงพร้อมกัน (Parallel conversions) | 1 | 2–3 is fine on a GPU |
| ล้างอัตโนมัติ (Auto-clear) | on | Remove finished rows after 5 s |

### Troubleshooting (short)

| Problem | Fix |
|---|---|
| `HTTP 410` / `403` | Press "Update tools". With a VPN, keep the same server for the whole download |
| `HTTP 429` | Lower "parallel fragments" / "parallel links" and try again later |
| "หาลิงก์วิดีโอไม่เจอ" (video link not found) | The page hides the video with heavier JavaScript. Try the clip's own page |
| A Chrome window pops up | Cloudflare wants a human check. Click it and the app continues |
| Stuck at 99.x% | Handled automatically: after 90 s without progress the app resumes the download |
| "มีแล้ว" (already have) but you want it again | Right-click → โหลดซ้ำ (force re-download) |

The full guide below is in Thai, including every setting, how each feature works, the cmd usage of yt-dlp and the changelog.

---

## ภาษาไทย

แอปนี้ รวมถึง `setup.bat` และ README ทำด้วย **Claude** (ผู้ช่วย AI ของ Anthropic ผ่าน Claude Code) ตามที่เจ้าของสั่งและทดสอบ

โปรแกรมโหลดวิดีโอแบบมีหน้าต่าง ใช้ [yt-dlp](https://github.com/yt-dlp/yt-dlp) อยู่เบื้องหลัง
ใส่ลิงก์เข้าคิว โหลดพร้อมกันได้หลายลิงก์ และแปลงเป็น H.265 ด้วยการ์ดจอให้อัตโนมัติ

## ความสามารถ

- **คิวลิงก์** กด Ctrl+V แล้วลิงก์เข้าคิวทันที (วางหลายลิงก์พร้อมกันได้ ใช้ได้ทั้งแป้นไทยและอังกฤษ)
- **ดึงชื่อคลิปให้เอง** รองรับภาษาไทย ถ้า yt-dlp ดึงไม่ได้จะใช้ชื่อจากหน้าเว็บแทน
- **โหลดพร้อมกัน 1–8 ลิงก์** ตั้งได้ และเปลี่ยนระหว่างโหลดได้
- **เลือกความชัดได้** สูงสุด / 1080p / 720p
- **แยกคิวโหลดกับคิวแปลง** คลิปไหนโหลดเสร็จก็เข้าคิวแปลง แล้วช่องโหลดไปทำลิงก์ถัดไปทันที
- **เลือกได้ทีละคลิปว่าจะแปลงไหม** ติ๊ก ☑ ในช่อง "แปลง" ท้ายแถว (ค่าเริ่มต้นคือไม่แปลง ได้ไฟล์ตามที่เว็บส่งมา)
- **แปลงเป็น H.265 (mp4 หรือ mkv)** ด้วย NVIDIA / AMD / Intel หรือ CPU
- **ทดสอบความเร็วการ์ดจอทุกครั้งที่เปิดแอป** แล้วเลือกตัวที่ดีที่สุดให้เอง (เปลี่ยนเองได้จาก dropdown)
- **ถ้าการ์ดจอแปลงไม่ผ่าน** จะลองใหม่ด้วย CPU ให้อัตโนมัติ
- **เว็บที่ yt-dlp ไม่รองรับ** (เช่น missav, 7mmtv) แอปจะอ่านหน้าเว็บ หาลิงก์ m3u8/mp4 แล้วโหลดแบบปลอมตัวเป็น Chrome ให้
- **เว็บที่มีหลาย server** แอปจะเช็คทุก server เลือกตัวที่ชัดที่สุดก่อน ถ้าโหลดไม่ผ่านจะเปลี่ยน server ให้เอง
- **อัปเดตเครื่องมือทั้ง 5 ตัวทุกครั้งที่เปิดแอป** (yt-dlp, ffmpeg, ffprobe, deno, aria2c) และอัปเดตตัวแอปเองจาก GitHub
- **ย่อลง System Tray** สีไอคอนบอกสถานะ (เหลือง = รอ / น้ำเงิน = กำลังโหลด / เขียว = เสร็จหมด)
- **หน้าจอภาษาไทย / English** (ค่าเริ่มต้น English)
- **Chrome Extension** กดไอคอนหรือคลิกขวาที่ลิงก์ แล้วเริ่มโหลดให้เลย
- **Error log** เขียนลงไฟล์เฉพาะตอนมี error แล้ว push ขึ้น repo private
- **แกะลิงก์จากหน้ารวม** วางลิงก์หน้าค้นหา/หมวด/tag/นักแสดง/ช่อง แล้วแอปดึงลิงก์คลิปทั้งหมดเข้าคิวให้ ตามไปหลายหน้าได้ (ตั้งได้ 1–50 หน้า) และโหลดลงโฟลเดอร์ย่อยตามชื่อหน้านั้น
- **กันโหลดซ้ำ** ลิงก์ซ้ำในคิว (เทียบรหัสคลิป ไม่ใช่แค่ลิงก์) และไฟล์ที่มีอยู่แล้วในโฟลเดอร์ปลายทาง
- **ชื่อเหมือนกันแต่คนละคลิป** โหลดครบทุกอัน อันที่สองชื่อ `ชื่อ (2).mp4` อันที่สามชื่อ `ชื่อ (3).mp4` ไปเรื่อยๆ
- **คลิกขวาที่แถว** รีเซ็ตสถานะ, โหลดซ้ำ, แก้ไขลิงก์, แก้ไขชื่อ (ใช้เป็นชื่อไฟล์), เปิดไฟล์ ฯลฯ
- **ล้างคิวที่เสร็จแล้วอัตโนมัติ** แถวที่เสร็จหรือมีไฟล์แล้วจะหายไปเองหลัง 5 วินาที (ปิดได้)
- **จำคิวไว้** ปิดแอปแล้วเปิดใหม่ คิวยังอยู่ คลิปที่โหลดแล้วแต่ยังไม่แปลงจะแปลงต่อได้เลยโดยไม่ต้องโหลดใหม่

## ติดตั้ง (ครั้งแรก)

**ง่ายสุด: โหลด zip ชุดเต็ม** ที่หน้า [Releases](https://github.com/KEWI-hub/YtdlpGUI/releases/latest) เลือกไฟล์ **`YtdlpGUI-vX.Y.Z-full.zip`** (ประมาณ 200MB) แตกไฟล์ไว้ที่ไหนก็ได้ แล้วดับเบิลคลิก `YtdlpGUI.exe` ใช้ได้เลย เครื่องมือใน `bin\` แนบมาให้ครบแล้ว ไม่ต้องโหลดหรือติดตั้งอะไรเพิ่ม — ถ้าโหลดมาแค่ `YtdlpGUI.exe` ตัวเดียวก็ได้ เปิดครั้งแรกแอปจะรู้เองว่ายังไม่มี `bin\` แล้วถามว่าจะโหลดเครื่องมือให้เลยไหม (ประมาณ 150MB) กด **Yes** รอสักครู่ก็ใช้ได้เลย ไม่ต้องรัน `setup.bat`

หรือจะติดตั้งจาก repo ก็ได้:

1. โหลดหรือ clone repo นี้ลงเครื่อง
2. ดับเบิลคลิก **`setup.bat`** จะโหลดเครื่องมือที่จำเป็นมาไว้ใน `bin\` ให้เอง (ประมาณ 250MB ใช้เวลา 15–60 วินาที)
3. `setup.bat` จะโหลด **`YtdlpGUI.exe`** จาก **Release ล่าสุด** ให้ด้วย ถ้าโหลดไม่ได้ (เช่น repo เป็น private) และเครื่องมี Python 3.11 ขึ้นไป จะถามว่าจะ build เองไหม ตอบ `Y` แล้วรอประมาณ 1 นาที
4. เปิด `YtdlpGUI.exe` ได้เลย

- ถ้าไฟล์ไหนมีอยู่แล้ว `setup.bat` จะข้ามไป ไม่โหลดซ้ำ
- อยากอัปเดตเครื่องมือทุกตัวเป็นเวอร์ชันล่าสุด ให้รัน `setup.bat force`
- ต้องใช้ Windows 10 (1803 ขึ้นไป) หรือ 11 แบบ 64-bit เพราะใช้ `curl` กับ `tar` ที่มากับ Windows

### ไฟล์ที่ไม่ได้อยู่ใน repo (แต่จำเป็น)

| ไฟล์ / โฟลเดอร์ | ทำไมไม่อัปขึ้น GitHub | เอามาจากไหน |
|---|---|---|
| `bin\yt-dlp.exe` | เป็นโปรแกรมของคนอื่น | `setup.bat` โหลดให้ จาก [yt-dlp releases](https://github.com/yt-dlp/yt-dlp/releases) |
| `bin\ffmpeg.exe`, `bin\ffprobe.exe` | ไฟล์ละ 160–190MB **เกินขนาดสูงสุด 100MB ที่ GitHub รับ** | `setup.bat` โหลดให้ จาก [yt-dlp/FFmpeg-Builds](https://github.com/yt-dlp/FFmpeg-Builds/releases) (win64-gpl) |
| `bin\deno.exe` | เป็นโปรแกรมของคนอื่น (~90MB) | `setup.bat` โหลดให้ จาก [deno releases](https://github.com/denoland/deno/releases) |
| `bin\aria2c.exe` | เป็นโปรแกรมของคนอื่น | `setup.bat` โหลดให้ จาก [aria2 releases](https://github.com/aria2/aria2/releases) |
| `YtdlpGUI.exe` | เป็นไฟล์ที่ build แล้ว แนบไว้ใน **Releases** แทน | หน้า Releases หรือให้ `setup.bat` build จาก source |
| `_browser\` | profile Chrome ของแอป **มี cookie ของเว็บที่เคยเข้า** | แอปสร้างให้เอง |
| `settings.json`, `queue.json` | ค่าที่ตั้งเอง, path ในเครื่อง และลิงก์ที่โหลด | แอปสร้างให้เอง |
| `_tmp\`, `build\`, คลิปที่โหลดมา | ไฟล์ชั่วคราว / ไฟล์ส่วนตัว | - |

ทั้งหมดนี้อยู่ใน `.gitignore` แล้ว เลยไม่เผลอ commit ขึ้นไป

## Chrome Extension (กดโหลดได้ทันที)

โฟลเดอร์ `chrome-extension\` เป็น extension เล็กๆ ของ Chrome ใช้ส่งลิงก์เข้าแอปตรงๆ ไม่ต้อง copy มาวาง

**ติดตั้ง (ครั้งเดียว)** ถ้าอัปเดตแอปแล้ว extension มีเวอร์ชันใหม่ ให้กด **Reload** (ลูกศรวน) ที่การ์ดของ extension ใน `chrome://extensions` ด้วย

**ขั้นตอนติดตั้ง:**
1. เปิด `chrome://extensions` ใน Chrome
2. เปิด **Developer mode** (มุมขวาบน)
3. กด **Load unpacked** แล้วเลือกโฟลเดอร์ `chrome-extension` ในโปรเจกต์นี้
4. (ถ้าต้องการ) กดหมุดให้ไอคอนอยู่บนแถบเครื่องมือ

**ใช้งาน** (ต้องเปิดแอป YtdlpGUI ไว้ ย่อลง tray ได้):
- กดไอคอน extension หรือกด **Alt+Shift+D** = โหลดหน้าที่เปิดอยู่
- คลิกขวาที่ลิงก์ → **Download link with YtdlpGUI**
- ขึ้น ✓ สีเขียว = ส่งเข้าแอปแล้ว และเริ่มโหลดให้เอง / ขึ้น ! สีแดง = ยังไม่ได้เปิดแอป

extension คุยกับแอปผ่าน `127.0.0.1:47777` ในเครื่องเท่านั้น แอปรับลิงก์เฉพาะที่มาจาก extension (ต้องมี header `X-YtdlpGUI`) หน้าเว็บทั่วไปแอบส่งลิงก์เข้าแอปไม่ได้

## System Tray

กดย่อหน้าต่าง (minimize) แล้วแอปจะไปอยู่ที่ System Tray มุมขวาล่าง สีไอคอนบอกสถานะ เอาเมาส์ชี้จะบอกรายละเอียด

| สี | ความหมาย |
|---|---|
| 🟡 เหลือง | มีคลิปรอโหลด / รอแปลง |
| 🔵 น้ำเงิน | กำลังโหลดหรือกำลังแปลง |
| 🟢 เขียว | เสร็จหมดแล้ว |
| ⚪ เทา | ว่าง ไม่มีอะไรในคิว |

คลิกไอคอน = เปิดหน้าต่างกลับมา / คลิกขวา = เริ่มโหลด, ออกจากโปรแกรม

## ภาษา

เมนู **Language / ภาษา** ด้านบน → English หรือ ไทย ค่าเริ่มต้นเป็น English แอปจะเปิดใหม่เพื่อเปลี่ยนภาษา คิวยังอยู่ครบ

## อัปเดตเครื่องมือทุกครั้งที่เปิดแอป

ทุกครั้งที่เปิดแอป (ถ้าติ๊ก "เช็คอัปเดตตอนเปิด") แอปจะเทียบเครื่องมือใน `bin\` ทุกตัวกับ Release บน GitHub ตัวไหนใหม่กว่าจะอัปเดตให้เลย

| เครื่องมือ | ออกใหม่บ่อยแค่ไหน |
|---|---|
| yt-dlp | บ่อยมาก บางทีหลายครั้งต่อสัปดาห์ |
| ffmpeg + ffprobe | build ใหม่แทบทุกวัน (ครั้งละ ~190MB) |
| deno | ประมาณทุก 1–2 สัปดาห์ |
| aria2c | นานๆ ครั้ง |

- เครื่องมือตัวไหนหายไป จะโหลดมาให้ใหม่
- โหลดไฟล์ใหม่มาเก็บไว้ก่อนแล้วค่อยสลับ ถ้าโหลดพังกลางทาง ตัวเดิมยังใช้ได้
- ปุ่ม **อัปเดตเครื่องมือ** กดเช็คเองเมื่อไหร่ก็ได้
- ระหว่างอัปเดต ปุ่ม "เริ่มโหลด" จะกดไม่ได้ชั่วคราว

## Error log

- ใช้งานปกติ **ไม่เขียนอะไรลงไฟล์** ช่อง Log บนหน้าจอไม่ได้บันทึกเก็บ
- เขียนลงไฟล์ `logs\errors-ปี-เดือน-วัน.log` **เฉพาะตอนมี error**: โหลดไม่ผ่าน (พร้อมข้อความจาก yt-dlp ท้ายๆ), แปลงไม่ผ่าน (พร้อม error ของ ffmpeg), โปรแกรมพังแบบไม่คาดคิด (พร้อม traceback) ชื่อผู้ใช้ Windows ใน path ถูกแทนด้วย `~`
- เครื่องของเจ้าของจะ push log ขึ้น repo **private** `KEWI-hub/YtdlpGUI-logs` ให้เอง (15 วินาทีหลังเปิดแอป, ตอนคิวเสร็จ และตอนปิดแอป) เอาไว้ให้ดึงมาวิเคราะห์แก้ไข เครื่องคนอื่นไม่มีสิทธิ์ push เลยเก็บไว้แค่ในเครื่อง

## อัปเดตแอปอัตโนมัติ

ทุกครั้งที่เปิดแอป (ถ้าติ๊ก "เช็คอัปเดตตอนเปิด" ไว้) แอปจะเทียบเวอร์ชันของตัวเอง (ดูได้ที่ชื่อหน้าต่าง เช่น `YtdlpGUI v1.1.0`) กับ Release ล่าสุดบน GitHub

1. ถ้าบน GitHub ใหม่กว่า จะโหลด `YtdlpGUI.exe` ตัวใหม่มาเก็บไว้ก่อน (โหลดเบื้องหลัง)
2. ถ้าไม่มีอะไรโหลดอยู่ แอปจะปิดตัว สลับไฟล์ exe แล้วเปิดใหม่ให้เอง คิวและค่าที่ตั้งไว้ยังอยู่ครบ
3. ถ้าคิวกำลังทำงาน จะรอจนคิวเสร็จ หรือติดตั้งตอนคุณกดปิดแอป
4. ถ้าต่อ GitHub ไม่ได้ ก็ข้ามไป ใช้งานต่อได้ตามปกติ

- ถ้า repo เป็น private แอปจะยืมสิทธิ์ที่ git จำไว้ในเครื่อง (Git Credential Manager) มาเช็ค ถ้าเครื่องนั้นไม่เคยล็อกอิน GitHub จะเช็คไม่ได้
- รันจาก source (`py ytdlp_gui.py`) จะไม่อัปเดตตัวเอง ให้ใช้ `git pull` แทน

## การมีส่วนร่วม (Fork + Pull Request)

- **คนที่แก้ repo นี้ได้โดยตรงมีคนเดียวคือเจ้าของ (KEWI-hub)** ไม่ต้องขอสิทธิ์ collaborator
- ถ้าจะแก้อะไร ให้ **Fork** ไปที่บัญชีตัวเอง แก้ใน fork แล้วเปิด **Pull Request** กลับมาที่ `main` เจ้าของจะรีวิวแล้วค่อยรวม
- แก้ README (ทั้งอังกฤษและไทย) ใน PR เดียวกันด้วย และห้าม commit `bin\`, `*.exe`, `_browser\`, `settings.json`, `queue.json`

## ออกเวอร์ชันใหม่ (สำหรับเจ้าของ)

1. แก้ `APP_VERSION` บรรทัดบนๆ ของ `ytdlp_gui.py` (เช่น `1.2.0`) และเขียนประวัติการเปลี่ยนแปลงใน README
2. commit แล้ว push จากนั้นสร้าง tag เลขเดียวกันแล้ว push: `git tag v1.2.0` และ `git push origin v1.2.0`
3. GitHub Actions (`.github/workflows/release.yml`) จะ build `YtdlpGUI.exe` แล้วออก Release ให้เอง ถ้าเลขใน `APP_VERSION` ไม่ตรงกับ tag จะไม่ยอม build
4. แอปที่ติดตั้งอยู่ทุกเครื่องจะอัปเดตตัวเองตอนเปิดครั้งถัดไป

## วิธีใช้

1. เปิด `YtdlpGUI.exe`
2. รอประมาณ 10 วินาที ให้แอปเช็คอัปเดตและทดสอบการ์ดจอเสร็จ
3. copy ลิงก์ แล้วกด Ctrl+V ในช่องด้านบน
4. เลือกโฟลเดอร์ที่จะโหลดลง
5. กด **▶ เริ่มโหลด**

| ทำอะไร | วิธี |
|---|---|
| คัดลอกลิงก์ | ดับเบิลคลิกที่แถว |
| ลบลิงก์ | เลือกแถวแล้วกด Delete หรือปุ่ม "ลบที่เลือก" |
| ดึงชื่อใหม่ | เลือกแถวแล้วกด "ดึงชื่อใหม่" (ถ้าไม่เลือก = ทุกแถว) |
| โหลดหรือแปลงใหม่ | "ลองใหม่ที่ล้มเหลว" ถ้าโหลดเสร็จแล้วจะแปลงอย่างเดียว ไม่โหลดซ้ำ |
| แปลง / ไม่แปลง | คลิกช่อง ☐ ท้ายแถว, เลือกหลายแถวแล้วกด Space, หรือคลิกหัวคอลัมน์ "แปลง" = สลับทุกแถว |
| เมนูอื่นๆ | **คลิกขวา** ที่แถว (เลือกหลายแถวก่อนได้) |
| ล้างแถวที่เสร็จแล้ว | ติ๊ก **"ล้างอัตโนมัติ"** (เปิดไว้เป็นค่าเริ่มต้น) หรือกดปุ่ม "ล้างที่เสร็จแล้ว" เอง |

### ล้างอัตโนมัติ

- แถวที่ **เสร็จ** หรือ **มีแล้ว** จะค้างให้เห็น 5 วินาที แล้วหายไปจากคิวเอง แถวที่ล้มเหลว/หยุด/รอ ไม่ถูกล้าง
- ทุกแถวที่เสร็จจะมีบันทึกในช่อง Log เช่น `✔ เสร็จ: ชื่อไฟล์.mp4` ไว้ดูย้อนหลัง
- แถบสถานะนับ "เสร็จแล้ว n" รวมแถวที่ถูกล้างไปแล้วด้วย
- ถ้าอยากติ๊ก "แปลง" ให้คลิปที่โหลดเสร็จแล้ว ให้เอาติ๊ก "ล้างอัตโนมัติ" ออกก่อน ไม่งั้นแถวจะหายไปก่อน

### เมนูคลิกขวา

| เมนู | ทำอะไร |
|---|---|
| รีเซ็ตสถานะ | กลับไป "รอ" (ถ้าโหลดแล้วแต่แปลงไม่ผ่าน จะกลับไป "รอแปลง" แทน ไม่ต้องโหลดใหม่) ใช้กับแถวที่ล้มเหลว/หยุด/เสร็จ/มีแล้ว ได้หมด |
| โหลดซ้ำ | บังคับโหลดใหม่ แม้มีไฟล์อยู่ในโฟลเดอร์แล้ว |
| แก้ไขลิงก์ ... | เปลี่ยนลิงก์ของแถวนี้ แล้วดึงชื่อใหม่ให้เอง (ถ้าซ้ำกับแถวอื่นจะเตือน) |
| แก้ไขชื่อ ... | ตั้งชื่อเอง และใช้เป็น **ชื่อไฟล์** ตอนโหลด ดึงชื่อใหม่จะไม่ทับชื่อที่ตั้งเอง |
| แกะลิงก์คลิปจากหน้านี้ | เอาแถวนี้ออก แล้วดึงลิงก์คลิปทั้งหมดในหน้านั้นเข้าคิวแทน (ใช้กับหน้ารวมที่แอปไม่รู้ว่าเป็นหน้ารวม) |
| ดึงชื่อใหม่ / สลับ แปลง | เหมือนปุ่มด้านล่าง แต่ทำกับแถวที่เลือก |
| คัดลอกลิงก์ | คัดลอกลิงก์ทุกแถวที่เลือก (บรรทัดละลิงก์) |
| เปิดไฟล์ / เปิดโฟลเดอร์ที่มีไฟล์ | ใช้ได้เมื่อแถวนั้นมีไฟล์แล้ว |
| ลบออกจากคิว | ลบแค่ออกจากคิว ไฟล์ไม่ถูกลบ |

แถวที่กำลังโหลดหรือกำลังแปลงอยู่ รีเซ็ต แก้ไข หรือลบไม่ได้ (ต้องหยุดก่อน)

### ติ๊ก/เอาติ๊ก "แปลง" แล้วเกิดอะไรขึ้น

| สถานะคลิปตอนนั้น | ติ๊ก ☑ | เอาติ๊กออก ☐ |
|---|---|---|
| รอโหลด / กำลังโหลด | โหลดเสร็จแล้วจะเข้าคิวแปลง | โหลดเสร็จแล้วจบเลย ไม่แปลง |
| เสร็จ (ยังไม่เคยแปลง) | กลับไป "รอแปลง" กด ▶ แล้วแปลงได้เลย ไม่ต้องโหลดใหม่ | - |
| รอแปลง | - | เป็น "เสร็จ" ทันที เก็บไฟล์ต้นฉบับไว้ |
| กำลังแปลง | - | หยุดแปลงทันที ลบไฟล์ที่แปลงไปครึ่งทาง เก็บไฟล์ต้นฉบับไว้ |

## แกะลิงก์จากหน้ารวม

วางลิงก์หน้าที่มีหลายคลิป เช่น `https://example-site.com/?s=some+name` แอปจะดึงลิงก์คลิปทุกอันในหน้านั้นมาใส่คิวให้ (ตัวอย่างนี้ได้ 12 ลิงก์)

**แอปรู้ได้ยังไงว่าเป็นหน้ารวม** ลิงก์มีคำค้น (`?s=`, `?q=`, `?search=`, `?k=` ฯลฯ) หรือ path มีคำว่า `search`, `tag`, `category`, `genre`, `actress`, `actor`, `performer`, `idol`, `cast`, `star`, `model`, `pornstar`, `channel`, `studio`, `maker`, `series`, `playlist`, `user`, `videos`, `page` หรือเป็นช่อง/playlist ของ YouTube
ถ้าแอปไม่รู้ว่าเป็นหน้ารวม ให้คลิกขวาที่แถวนั้น → **แกะลิงก์คลิปจากหน้านี้**

**วิธีแกะ**

1. ถาม yt-dlp ก่อน (`--flat-playlist`) ใช้กับเว็บที่ yt-dlp รู้จัก เช่น ช่อง/playlist YouTube, หน้า model ของ pornhub
2. ถ้า yt-dlp แกะไม่ได้ แอปอ่านหน้าเว็บเอง เก็บลิงก์ในเว็บเดียวกัน ตัดลิงก์เมนูทิ้ง (หมวด, tag, หน้า, dmca ฯลฯ) แล้วเลือกกลุ่มลิงก์ที่ **รูปแบบเหมือนกันและมีมากที่สุด** เช่น `/2025/09/07/somename_12/` กับอีก 11 อันเป็นรูปแบบ `/ปี/เดือน/วัน/ชื่อ/` เหมือนกัน
3. ตามไปหน้าถัดไปจนครบจำนวน **"หน้ารวมสูงสุด"** (ค่าเริ่มต้น 5 หน้า ตั้งได้ 1–50) ได้ลิงก์ไม่เกิน 1000 ลิงก์ต่อครั้ง
   - หาหน้าถัดไปจากลิงก์ "next" ของเว็บ ถ้าไม่มีจะหาลิงก์เลขหน้าแทน (`/page/2/`, `?page=2`, `?paged=2`)
   - ถ้าหน้าไหนไม่มีลิงก์ใหม่เลย (หน้าสุดท้าย) จะหยุดเอง
   - ลิงก์ที่ซ้ำกันระหว่างหน้า (บางเว็บหน้า 1 กับ 2 มีคลิปซ้ำกัน) ถูกตัดออกให้

### โฟลเดอร์ย่อยของหน้ารวม

คลิปที่แกะมาจากหน้ารวมจะโหลดลง **โฟลเดอร์ย่อยตามชื่อหน้านั้น** ภายในโฟลเดอร์ "โหลดลง" (แอปสร้างให้เอง) ดูชื่อได้ในคอลัมน์ "โฟลเดอร์ย่อย"

| ลิงก์ที่วาง | โฟลเดอร์ย่อย |
|---|---|
| `example-site.com/?s=some+name` | `some name` (ใช้คำค้น) |
| `example-site.com/en/actresses/Some%20Name` | `Some Name` (ท้าย path) |
| `example-site.com/actor/some_actor/` | `some actor` |
| `example.com/tag/big-name/page/2/` | `big name` |
| `youtube.com/@RickAstleyYT/videos` | `@RickAstleyYT` |

- เช็คไฟล์ซ้ำในโฟลเดอร์ย่อยนั้นด้วย (ถ้ามีไฟล์อยู่แล้วขึ้น "มีแล้ว")
- ลิงก์ที่วางทีละอันไม่มีโฟลเดอร์ย่อย โหลดลงโฟลเดอร์หลักตามเดิม
- ถ้าลิงก์ในหน้ารวมซ้ำกับลิงก์ที่อยู่ในคิวแล้ว จะใช้แถวเดิม (โฟลเดอร์เดิม)

- ลิงก์ที่แกะได้เข้าคิวผ่านตัวกันซ้ำตามปกติ (ซ้ำกับที่อยู่ในคิวแล้วจะถูกข้าม และถ้ามีไฟล์แล้วจะขึ้น "มีแล้ว")
- ดูผลได้ใน Log เช่น `แกะได้ 12 ลิงก์ เพิ่มเข้าคิว 12`
- บางเว็บจัดหน้าแปลกๆ อาจได้ลิงก์ผิดกลุ่ม ถ้าเจอแบบนั้นให้ลบแถวที่ไม่ใช่ออก หรือวางลิงก์คลิปทีละอันแทน

## กันโหลดซ้ำ

| เช็คตอนไหน | เช็คอะไร | ผล |
|---|---|---|
| ตอนเพิ่มลิงก์ | **รหัสคลิป** ซ้ำกับแถวที่อยู่ในคิวแล้ว | ไม่เพิ่ม แถบสถานะบอก "ข้ามลิงก์ซ้ำ n" และบอกใน Log ว่าซ้ำกับแถวไหน |
| ตอนได้ชื่อคลิป และก่อนเริ่มโหลด | มีไฟล์คลิปนี้ในโฟลเดอร์ปลายทางแล้ว (เทียบจาก `sources.json` และชื่อไฟล์) | สถานะ **"มีแล้ว"** ไม่โหลด (ถ้าอยากโหลดซ้ำจริงๆ คลิกขวา → โหลดซ้ำ) |

รหัสคลิปคือ ลิงก์ที่ต่างกันแต่เป็นคลิปเดียวกัน จะนับว่าซ้ำ เช่น

- `youtu.be/xxx` = `youtube.com/watch?v=xxx&t=5`
- `pornhub.com/...viewkey=abc` = `pornhub.org/...viewkey=abc`
- `missav.ws/dm26/en/abc-123` = `missav123.com/th/abc-123` (mirror และภาษาต่างกัน)
- `7mmtv.sx/en/.../206137/...` = `7mmtv.sx/th/.../206137/...`
- เว็บอื่น: ตัด `www.`, `/` ท้ายลิงก์ และ parameter ติดตาม (`utm_`, `fbclid`, `si=` ฯลฯ) ออกก่อนเทียบ

เช็คไฟล์ในโฟลเดอร์จากชื่อไฟล์ที่ตรงกับชื่อคลิป (ไม่สนสัญลักษณ์ และยอมให้ชื่อถูกตัดสั้นได้) ใช้กับไฟล์ที่แปลง H.265 แล้วได้ด้วย ไฟล์เก่าที่มีรหัสในวงเล็บท้ายชื่อ (เช่น `[jNQXAC9IVRw]`) ก็ยังเช็คเจอ

**ชื่อเหมือนกันแต่คนละคลิป** (เช่น คลิปชื่อ "Episode 1" จากคนละช่อง)
- แอปจำว่าไฟล์ไหนโหลดมาจากลิงก์ไหน ไว้ในไฟล์ `sources.json` ข้างแอป (ไม่ล้าง)
- ไฟล์ชื่อเดียวกันที่โหลดมาจากลิงก์อื่น จะไม่นับว่า "มีแล้ว" และไม่เขียนทับ คลิปใหม่จะได้ชื่อ `ชื่อ (2)`, `ชื่อ (3)` ...
- โหลดพร้อมกันหลายอันที่ชื่อเหมือนกันก็ไม่ชนกัน (แอปจองชื่อไว้ตั้งแต่เริ่มโหลด)
- แอปรอดึงชื่อคลิปก่อนเริ่มโหลด (นานสุด 90 วินาที) จะได้ตั้งชื่อไฟล์ให้ไม่ชนกัน
- ไฟล์เก่าที่โหลดก่อน v1.2.6 แอปไม่รู้ว่ามาจากลิงก์ไหน ถ้าชื่อตรงกันจะขึ้น "มีแล้ว" เหมือนเดิม ถ้าเป็นคนละคลิปให้คลิกขวา → โหลดซ้ำ คลิปใหม่จะได้ชื่อ `(2)` ไฟล์เก่าไม่ถูกเขียนทับ

**กันโหลดซ้ำข้ามรอบ** ใช้ `sources.json` (จำว่าไฟล์ไหนมาจากลิงก์ไหน) คู่กับการเช็คชื่อไฟล์ในโฟลเดอร์ ลบหรือย้ายไฟล์ไปแล้วก็โหลดใหม่ได้
- ตั้งแต่ v1.3.2 เลิกใช้ประวัติของ yt-dlp (`--download-archive`) แล้ว เพราะคลิปที่แอปแกะลิงก์วิดีโอมาเองได้รหัสซ้ำกันหมด (ทุกคลิปเป็น `generic master`) ทำให้คลิปที่เหลือถูกข้ามทิ้งเงียบๆ
- อยากให้ลืมประวัติทั้งหมด: เมนู **เครื่องมือ > ล้างประวัติไฟล์ที่โหลด (sources.json)** ไฟล์วิดีโอไม่ถูกลบ หลังล้างแล้วการเช็ค "มีแล้ว" จะดูจากชื่อไฟล์ในโฟลเดอร์อย่างเดียว

## การตั้งค่า

| ตัวเลือก | ค่าเริ่มต้น | ความหมาย |
|---|---|---|
| รูปแบบ | อัตโนมัติ | **อัตโนมัติ** = ปรับตามเว็บให้เอง (ดูตารางด้านล่าง) / **MP4 ตรง** = บังคับไฟล์ mp4 ไฟล์เดียว ไม่ใช้ m3u8 / **ดีที่สุด** = เอาชัดสุดอย่างเดียว ไม่สนว่าเป็น m3u8 ไหม |
| ความชัด | สูงสุด | **สูงสุด** = เอาชัดที่สุดที่เว็บมี / **1080p**, **720p** = เอาตัวที่ชัดที่สุดที่ไม่เกินนี้ (ไฟล์เล็กลง โหลดเร็วขึ้น) ถ้าคลิปไม่มีความละเอียดที่ต่ำพอ จะเอาตัวที่ใกล้ที่สุดแทน ไม่ error เว็บที่มีหลาย server จะเลือก server ที่ชัดที่สุดในช่วงนี้ |
| Cookies จาก | firefox | ใช้ cookie จากเบราว์เซอร์นี้ (สำหรับคลิปที่ต้องล็อกอินหรือยืนยันอายุ) |
| ใช้ aria2c | เปิด | โหลดแบบหลาย connection ให้เร็วขึ้น (ถ้าเว็บต้องปลอมตัวเป็น Chrome แอปจะใช้ตัวโหลดของ yt-dlp แทนให้เอง) |
| โหลดพร้อมกัน | 3 | จำนวนลิงก์ที่โหลดพร้อมกัน (1–8) |
| หน้ารวมสูงสุด | 5 | ตอนแกะลิงก์จากหน้ารวม จะตามไปหน้าถัดไปได้กี่หน้า (1–50) |
| ชื่อไฟล์ยาวสุด | 70 | ความยาวชื่อไฟล์สูงสุด (ตัวอักษร ไม่นับนามสกุล) ตั้งได้ 30–150 ชื่อไฟล์เป็นชื่อเรื่องอย่างเดียว ไม่มีรหัสคลิป เช่น `Me at the zoo.mp4` |
| ชิ้นส่วนพร้อมกัน | 16 | จำนวนชิ้นของวิดีโอแบบสตรีม (m3u8) ที่โหลดพร้อมกันต่อ 1 ลิงก์ (1–32) ยิ่งเยอะยิ่งเร็ว ดูหัวข้อ "ทำไมบางเว็บโหลดช้า" |
| **ตั้งค่าการแปลง H.265** | | กรอบด้านล่าง ใช้กับทุกคลิปที่ติ๊ก ☑ แปลง (แปลงเสร็จจะลบไฟล์ต้นฉบับ) |
| ตัวแปลง | เลือกให้เอง | NVIDIA (NVENC) / AMD (AMF) / Intel (QSV) / CPU (x265) |
| ไฟล์ | mp4 | นามสกุลไฟล์ที่แปลงเสร็จ (mp4 เปิดบน iPhone/Mac ได้) |
| คุณภาพ | 24 | เลขน้อย = ชัดขึ้น ไฟล์ใหญ่ขึ้น (แนะนำ 22–28) |
| Preset | slow | ช้า = ไฟล์เล็กกว่า / เร็ว = แปลงเสร็จไวกว่า |
| แปลงพร้อมกัน | 1 | ถ้าใช้การ์ดจอ ตั้ง 2–3 ได้ |

### แอปเลือกตัวแปลงยังไง

ทุกครั้งที่เปิดแอป จะลองแปลงภาพทดสอบ 1080p ด้วยทุกตัวที่ใช้ได้ แล้ววัด fps ออกมา

1. เก็บเฉพาะตัวที่แปลงได้เร็วเกิน **60 fps** (เร็วกว่าเวลาจริง 2 เท่า)
2. ในกลุ่มนั้น เลือกตัวที่ภาพดีที่สุดเมื่อเทียบกับขนาดไฟล์: NVIDIA > Intel > AMD
3. ถ้าไม่มีตัวไหนเร็วพอ จะเลือกตัวที่เร็วที่สุด

แอปไม่เลือกตัวที่เร็วที่สุดตรงๆ เพราะการ์ดจอในตัวบางรุ่นแปลงเร็วกว่าก็จริง แต่ไฟล์ใหญ่กว่าและภาพแย่กว่า

ผลบนเครื่องนี้ (RTX 3080 Laptop + Radeon ในตัว):

| ตัวแปลง | ความเร็ว (1080p) |
|---|---|
| NVIDIA (NVENC) | ~150–250 fps ← แอปเลือกตัวนี้ |
| AMD (AMF) | ~170–200 fps |
| CPU (x265) | ~11–18 fps |

ตัวเลขนี้ใช้เปรียบเทียบกันเท่านั้น ของจริงแปลงไวกว่านี้ เพราะตอนทดสอบ ตัวสร้างภาพทดสอบเองก็ช้าอยู่แล้ว ผลแต่ละรอบต่างกันได้ตามความร้อนและรอบสัญญาณนาฬิกาของการ์ดจอ

ถ้าใช้การ์ดจอ ไฟล์จะใหญ่กว่า CPU ประมาณ 15–20% ที่เลขคุณภาพเท่ากัน ถ้าอยากได้ไฟล์เล็กลงให้เพิ่มเลขคุณภาพเป็น 26–28

## ผ่าน Cloudflare ยังไง

ถ้าต้องอ่านหน้าเว็บเอง (เว็บที่ yt-dlp ไม่รองรับ หรือตอนดึงชื่อ) แอปจะลองทีละชั้นตามนี้

1. **curl_cffi** ส่งคำขอแบบปลอมตัวเป็น Chrome เร็วที่สุด ผ่านได้เกือบทุกครั้ง
2. **Chrome แบบซ่อน** ถ้าชั้นแรกโดนบล็อก แอปจะเปิด Chrome ที่ติดตั้งในเครื่องแบบไม่มีหน้าต่าง ให้รัน JavaScript ของ Cloudflare จนผ่าน (ประมาณ 4–5 วินาที)
3. **Chrome แบบมีหน้าต่าง** ถ้าเจอหน้า "Verify you are human" แอปจะเปิดหน้าต่าง Chrome ขึ้นมาให้กดยืนยันเอง รอได้ 3 นาที แอปไม่กดให้อัตโนมัติ

- Chrome ที่แอปเปิดใช้ profile แยกของตัวเองที่ `_browser\` ไม่ยุ่งกับ Chrome ที่ใช้อยู่ ไม่เห็น cookie หรือรหัสผ่านของคุณ และเปิด Chrome ของคุณค้างไว้ได้ตามปกติ
- พอยืนยันผ่านแล้ว cookie จะถูกเก็บไว้ใน `_browser\` ครั้งต่อไปจะผ่านแบบซ่อนได้เลย
- ถ้าเครื่องไม่มี Chrome จะใช้ Edge แทน
- ถ้าใช้ VPN แบบ datacenter จะโดน Cloudflare ตรวจหนักกว่าเน็ตบ้าน

## เว็บที่มีหลาย server (เช่น 7mmtv)

1. อ่านหน้าเว็บ แล้วให้ Chrome แบบซ่อนกดปุ่มเลือก server ทุกปุ่มด้วย JavaScript ของเว็บเอง เพื่อดูว่าแต่ละ server ใช้ player ตัวไหน
2. เปิด player ของแต่ละ server หาลิงก์ m3u8/mp4 (ถ้ามี iframe ซ้อนอยู่ จะตามเข้าไปได้อีก 2 ชั้น) ถ้า player เก็บลิงก์ไว้หลายตัว (`links = {"hls2":..,"hls4":..}`) จะเลือกตัวเลขมากสุดก่อน เพราะเป็นตัวที่ player ใช้เล่นจริงและเร็วกว่ามาก (ดูหัวข้อ "ทำไมบางเว็บโหลดช้า")
3. ถาม yt-dlp ว่าแต่ละ server ชัดแค่ไหน แล้วเรียงจากชัดสุด (ความละเอียดก่อน แล้วค่อยดู bitrate)
4. โหลดจาก server ที่ชัดที่สุดก่อน ถ้าไม่ผ่านจะเปลี่ยนไป server ถัดไปเอง

ดูได้ในช่อง Log ว่าแต่ละ server ชัดแค่ไหน และโหลดจาก server ไหน เช่น

```
server SW: ใช้ไม่ได้
server TV: 1080p 1206k
server VH: 1080p 2837k
server SP: 0p 0k
โหลดจาก server VH: https://...master.m3u8
```

ใช้เวลาเตรียมประมาณ 15–30 วินาทีต่อลิงก์ก่อนเริ่มโหลด ตอนนี้กดปุ่มเลือก server ได้เฉพาะ 7mmtv เว็บอื่นแอปจะตาม iframe ในหน้าเว็บให้แทน

## ทำไมบางเว็บโหลดช้า

**เช็คก่อนว่าได้ลิงก์ที่ถูกตัวไหม** ตัวเล่นวิดีโอ (jwplayer) ของบางเว็บเก็บลิงก์ไว้หลายตัวในตัวแปร `links = {"hls2":..., "hls3":..., "hls4":...}` แล้วเล่นจาก `hls4` ก่อน ตัวแรก (`hls2`) มักเป็นลิงก์ที่เซิร์ฟเวอร์จำกัดความเร็วไว้ (มี `sp=500` ในโทเคน) วัดจริงกับ pornavhd ต่างกันมหาศาล

| ลิงก์ที่ใช้ | ความเร็ว |
|---|---|
| `hls2` (ลิงก์แรกในหน้า) | 0.02–0.06 MB/s |
| `hls4` (ตัวที่ player ใช้จริง) | **34.8 MB/s** |

ตั้งแต่ v1.2.8 แอปเลือก `hls4` ให้เอง (เรียงจากเลขมากไปน้อย) ถ้าเจอว่าเว็บไหนยังช้าผิดปกติ ให้เทียบกับความเร็วที่โหลดผ่านเบราว์เซอร์/IDM ดู

เว็บสตรีมอย่าง 7mmtv หรือ missav ส่งวิดีโอมาเป็นชิ้นเล็กๆ (m3u8) และจำกัดความเร็วไว้ประมาณ **0.4 MiB/s ต่อ 1 connection** ต่อให้เน็ตเร็วแค่ไหนก็ช่วยไม่ได้ ทางแก้คือโหลดหลายชิ้นพร้อมกัน

ผลวัดจริงกับคลิปจาก 7mmtv (วัดตอนที่มีอีกคลิปโหลดอยู่ด้วย):

| ชิ้นส่วนพร้อมกัน | server SW | server VH |
|---|---|---|
| 8 (ค่าเดิม) | 3.2 MiB/s | 3.0 MiB/s |
| 16 (ค่าเริ่มต้นตอนนี้) | 6.5 MiB/s | 5.7 MiB/s |
| 24 | 8.0 MiB/s | 7.6 MiB/s |

- ถ้าอยากได้เร็วกว่านี้ เพิ่ม "ชิ้นส่วนพร้อมกัน" เป็น 24–32 ได้ แต่บางเว็บอาจบล็อกถ้าเปิด connection เยอะเกินไป ถ้าเริ่มโหลดไม่ผ่านหรือค้างให้ลดลง
- โหลดหลายลิงก์พร้อมกัน ("โหลดพร้อมกัน" 3–5) ก็ช่วยให้คิวโดยรวมเสร็จเร็วขึ้น เพราะแต่ละลิงก์มีโควต้าความเร็วของตัวเอง
- aria2c ใช้กับเว็บที่ต้องปลอมตัวเป็น Chrome ไม่ได้ เว็บพวกนี้เลยใช้ตัวโหลดของ yt-dlp ตามจำนวน "ชิ้นส่วนพร้อมกัน" แทน

## ถ้าโหลดไม่ผ่าน แอปทำอะไรให้บ้าง

1. **ไฟล์ความชัดสูงสุดโดนบล็อก (403/404)** เช่น 7mmtv บาง server ให้ดู 1080p ไม่ได้ แต่ 720p ได้ แอปจะตัดไฟล์นั้นออกแล้วเลือกตัวที่ชัดรองลงมา (สูงสุด 3 ครั้ง)
2. **server นั้นโหลดไม่ได้เลย** เปลี่ยนไป server ถัดไป (เว็บที่มีหลาย server)
3. **เว็บตอบ 429 (ขอถี่เกินไป) ระหว่างโหลด** รอแล้วลองชิ้นนั้นใหม่ เว้นนานขึ้นเรื่อยๆ (1, 2, 4 … สูงสุด 30 วินาที) ได้ 30 ครั้ง
4. **ค้างไม่ขยับ (เช่น ค้างที่ 99.9%)** บางชิ้นของวิดีโอค้างกลางทาง connection เงียบไปเฉยๆ
   - ตัด connection ที่เงียบเกิน 20 วินาทีแล้วลองชิ้นนั้นใหม่ (`--socket-timeout 20`)
   - ถ้าขนาดไฟล์ไม่เพิ่มเลย 90 วินาที แอปจะหยุด yt-dlp แล้วเริ่มใหม่ **โหลดต่อจากเดิม** (ชิ้นที่โหลดแล้วไม่ต้องโหลดใหม่) ทำได้ 5 ครั้งต่อคลิป
   - ดูได้ใน Log: `ค้างไม่ขยับ 90 วินาที ตัดแล้วโหลดต่อจากเดิม (ครั้งที่ 1/5)`
5. **ไม่ข้ามชิ้นที่โหลดไม่ได้เด็ดขาด** ถ้าลองครบแล้วยังไม่ได้ จะขึ้นว่าล้มเหลว แทนที่จะได้ไฟล์วิดีโอที่ขาดเป็นช่วงๆ

สถานะ "ล้มเหลว" จะบอกสาเหตุด้วย เช่น `โหลดไม่ได้: HTTP 403`, `โหลดไม่ได้: HTTP 429`, `โหลดไม่ได้: หาลิงก์วิดีโอไม่เจอ`

## โครงสร้างไฟล์

```
YtdlpGUI\
├── YtdlpGUI.exe      ตัวแอป
├── ytdlp_gui.py      source code
├── README.md
├── setup.bat         โหลดเครื่องมือใน bin\ ให้ (และ build YtdlpGUI.exe ถ้ามี Python)
├── requirements.txt  library ที่ต้องใช้ตอน build
├── .gitignore        ไฟล์ที่ไม่อัปขึ้น GitHub
├── .github\workflows\release.yml  build exe และออก Release ให้อัตโนมัติเมื่อ push tag
├── i18n.py           คำแปลภาษาอังกฤษของข้อความในแอป
├── chrome-extension\ Chrome Extension (manifest.json, background.js, icons\)
├── logs\             error log ในเครื่อง (ไม่อัปขึ้น repo นี้)
├── settings.json     ค่าที่ตั้งไว้ (สร้างเองอัตโนมัติ)
├── sources.json      ไฟล์ไหนโหลดมาจากลิงก์ไหน ใช้แยกคลิปที่ชื่อเหมือนกัน (สร้างเองอัตโนมัติ)
├── queue.json        คิวที่ค้างอยู่ (สร้างเองอัตโนมัติ)
├── _tmp\             ไฟล์ชั่วคราวระหว่างโหลด
├── _browser\         profile Chrome ของแอป (เก็บ cookie ที่ผ่าน Cloudflare แล้ว)
└── bin\
    ├── yt-dlp.exe    ตัวโหลด
    ├── ffmpeg.exe    รวมไฟล์และแปลง H.265
    ├── ffprobe.exe
    ├── aria2c.exe    โหลดแบบหลาย connection
    └── deno.exe      ใช้แก้ challenge ของ YouTube
```

ต้องมีโฟลเดอร์ `bin\` อยู่ข้าง `YtdlpGUI.exe` เสมอ ถ้าจะย้ายแอปไปที่อื่นให้ย้ายไปทั้งโฟลเดอร์

### ย้ายไปเครื่องอื่น

copy ไปแค่ `YtdlpGUI.exe`, `bin\` และ `README.md` ก็เปิดใช้ได้เลย ไม่ต้องติดตั้ง Python
หรือ clone repo นี้แล้วรัน `setup.bat` บนเครื่องใหม่
ไม่ต้อง copy `queue.json`, `settings.json`, `_browser\`, `_tmp\` เพราะแอปจะสร้างใหม่เองตอนเปิด

## Build ใหม่จาก source

ต้องมี Python 3.11 ขึ้นไป (หรือให้ `setup.bat` build ให้ก็ได้)

```bash
py -3.11 -m pip install -r requirements.txt
```

```bash
py -3.11 -m PyInstaller --noconfirm --onefile --windowed --collect-all curl_cffi --hidden-import websocket --name YtdlpGUI --distpath . --workpath build --specpath build ytdlp_gui.py
```

ต้องปิดแอปก่อน build ไม่งั้นจะเขียนทับ `YtdlpGUI.exe` ไม่ได้ ถ้าจะรันจาก source โดยไม่ build ใช้ `py -3.11 ytdlp_gui.py`

## แก้ปัญหา

| อาการ | วิธีแก้ |
|---|---|
| HTTP Error 410 / 403 | กด "อัปเดตเครื่องมือ" แล้วลองใหม่ ถ้าใช้ VPN ต้องเปิดค้างไว้และใช้ server เดิมตลอด (ลิงก์ผูกกับ IP) |
| WARNING m3u8 410 แต่ยังโหลดต่อได้ | ไม่ต้องสนใจ แอปจะเลือกไฟล์ mp4 แทนให้เอง |
| อ่าน cookie ไม่ได้ | ปิดเบราว์เซอร์นั้นก่อน หรือเปลี่ยน Cookies เป็น firefox / ไม่ใช้ |
| โหลดด้วย aria2c ไม่ผ่าน | เอาติ๊ก "ใช้ aria2c" ออก |
| หาลิงก์วิดีโอในหน้าเว็บไม่เจอ | เว็บนั้นซ่อนลิงก์ด้วย JavaScript ที่ซับซ้อนกว่าที่แอปแกะได้ |
| เว็บสตรีมโหลดช้า (3 MiB/s) | เพิ่ม "ชิ้นส่วนพร้อมกัน" (ดูหัวข้อ "ทำไมบางเว็บโหลดช้า") |
| ขึ้น "โหลดไม่ได้: HTTP 403" | เว็บบล็อกไฟล์นั้น แอปลองตัวที่ชัดรองลงมาให้แล้ว (สูงสุด 3 ครั้ง) และลอง server อื่นแล้ว ถ้ายังไม่ได้ ลองใหม่ทีหลัง หรือเปลี่ยน VPN |
| ขึ้น "โหลดไม่ได้: HTTP 429" | เว็บบอกว่าขอถี่เกินไป ลด "ชิ้นส่วนพร้อมกัน" หรือ "โหลดพร้อมกัน" แล้วรอสักพักค่อยลองใหม่ |
| ค้างที่ 99.x% ไม่ขยับ | แอปจัดการให้เองหลัง 90 วินาที (โหลดต่อจากเดิม) ถ้าขึ้น "ค้างหลายรอบ" ให้คลิกขวา → รีเซ็ตสถานะ แล้วเริ่มใหม่ทีหลัง ไฟล์ที่โหลดไปแล้วไม่หาย |
| ขึ้น "หาลิงก์วิดีโอไม่เจอ" | แอปอ่านหน้าเว็บแล้ว (ลอง 2 รอบ) ไม่เจอ server หรือลิงก์วิดีโอ เปิดลิงก์ในเบราว์เซอร์ดูว่ายังดูได้ไหม |
| server บางตัวขึ้น "ใช้ไม่ได้" | ปกติ (เช่น StreamWish บางครั้งตอบ 404) แอปจะข้ามไปใช้ server อื่นเอง |
| ขึ้น "มีแล้ว" แต่อยากโหลดใหม่ | คลิกขวา → โหลดซ้ำ |
| ลิงก์ที่ล้มเหลว อยากลองใหม่ | คลิกขวา → รีเซ็ตสถานะ แล้วกด ▶ เริ่มโหลด (หรือปุ่ม "ลองใหม่ที่ล้มเหลว") |
| วางหน้าค้นหาแล้วไม่ได้ลิงก์ | ขึ้น "แกะลิงก์จากหน้านี้ไม่ได้" แปลว่าหน้านั้นโหลดรายการด้วย JavaScript หรือไม่มีลิงก์ที่รูปแบบซ้ำกัน ให้วางลิงก์คลิปทีละอัน |
| แถวที่เสร็จหายไปเอง | เป็นเพราะ "ล้างอัตโนมัติ" ดูชื่อไฟล์ย้อนหลังได้ในช่อง Log ถ้าไม่อยากให้หายให้เอาติ๊กออก |
| ติ๊ก "แปลง" แล้วไม่แปลง | ถ้าคิวหยุดอยู่ ต้องกด ▶ เริ่มโหลด อีกครั้ง |
| หน้าต่าง Chrome เด้งขึ้นมาเอง | Cloudflare ต้องการให้กดยืนยัน ให้กดในหน้าต่างนั้น แล้วแอปจะทำงานต่อเอง |
| ผ่าน Cloudflare ไม่ได้แม้เปิด Chrome แล้ว | ลบโฟลเดอร์ `_browser\` แล้วลองใหม่ หรือเปลี่ยน server VPN |
| ชื่อภาษาไทยหาย (คิวเก่า) | เลือกแถวแล้วกด "ดึงชื่อใหม่" |
| การ์ดจอแปลงไม่ผ่าน | แอปจะลองใหม่ด้วย CPU ให้เอง ดูรายละเอียดได้ในช่อง Log |
| ปิดแอประหว่างแปลง | ไม่หาย เปิดแอปใหม่แล้วกด ▶ เริ่มโหลด จะแปลงต่อจากคิวเดิม (คลิปที่แปลงค้างอยู่จะเริ่มแปลงใหม่ตั้งแต่ต้น) |
| หยุดแปลงคลิปเดียว | เอาติ๊ก "แปลง" ของคลิปนั้นออก |
| HTTP Error 403 (ใช้ผ่าน cmd) | ใส่ `--cookies-from-browser firefox` (เว็บต้องยืนยันอายุหรือล็อกอิน) |
| Cloudflare anti-bot challenge (ใช้ผ่าน cmd) | เติม `--impersonate chrome` (ใช้กับ aria2c ไม่ได้) |
| IDM ขึ้น 410 ตั้งแต่เริ่มโหลด | IDM จับได้แค่ลิงก์ m3u8 ที่ใช้ไม่ได้ ให้ใช้แอปนี้หรือ yt-dlp แทน |

## ใช้ yt-dlp ผ่าน cmd (ไม่ใช้แอป)

เปิด cmd ที่โฟลเดอร์ `bin\` แล้วใช้คำสั่งตามนี้ yt-dlp จะหา ffmpeg, aria2c และ deno ที่อยู่ในโฟลเดอร์เดียวกันเจอเอง

### คำสั่งพื้นฐาน

อัปเดต yt-dlp (ถ้าโหลดไม่ได้ให้ลองข้อนี้ก่อนเสมอ):

```bash
yt-dlp -U
```

โหลดแบบปกติ:

```bash
yt-dlp.exe --js-runtimes deno --cookies-from-browser firefox "ลิงก์วิดีโอ"
```

โหลด Live ตั้งแต่ต้น:

```bash
yt-dlp.exe --js-runtimes deno --cookies-from-browser firefox --live-from-start "ลิงก์วิดีโอ Live"
```

### บังคับเป็นไฟล์ mp4 ลงโฟลเดอร์ PH

```bash
yt-dlp -f "b[ext=mp4][protocol^=http]/b[ext=mp4]" -P PH --no-warnings "ลิงก์วิดีโอ"
```

| ส่วนของคำสั่ง | ความหมาย |
|---|---|
| `-f "b[ext=mp4][protocol^=http]/b[ext=mp4]"` | เลือก mp4 แบบโหลดตรงที่ชัดที่สุด ถ้าไม่มีค่อยเอา mp4 แบบไหนก็ได้ |
| `-P PH` | บันทึกลงโฟลเดอร์ `PH` (สร้างให้เองถ้ายังไม่มี) |
| `--no-warnings` | ซ่อน WARNING เช่น m3u8 410 |

ถ้าไม่แปลง ส่วนใหญ่จะได้ mp4 ที่เป็น H.264 แต่ YouTube อาจได้ VP9/AV1 อยู่ในไฟล์ mp4

### โหลดเร็วขึ้นด้วย aria2c

```bash
yt-dlp -f "b[ext=mp4][protocol^=http]/b[ext=mp4]" -P PH --no-warnings --downloader aria2c --downloader-args "aria2c:-x 16 -s 16 -k 1M" "ลิงก์วิดีโอ"
```

ถ้าเว็บไม่ยอมให้โหลดหลาย connection (ขึ้น 403/410) ให้ลดเหลือ `-x 4 -s 4` หรือเอาส่วน `--downloader` ออก

### แปลงเป็น H.265

แปลงด้วย CPU ได้ไฟล์ .mkv (yt-dlp ไม่แปลงถ้านามสกุลเหมือนต้นฉบับ .mp4 → .mp4 ถ้าอยากได้ .mp4 ให้ใช้แอป):

```bash
yt-dlp -f "b[ext=mp4][protocol^=http]/b[ext=mp4]" -P PH --no-warnings --recode-video mkv --ppa "VideoConvertor:-c:v libx265 -crf 24 -preset slow -c:a aac -b:a 128k" "ลิงก์วิดีโอ"
```

แปลงด้วยการ์ดจอ NVIDIA ให้เปลี่ยนส่วน `--ppa` เป็น:

```
--ppa "VideoConvertor:-c:v hevc_nvenc -preset p5 -cq 26 -c:a copy"
```

### ตั้งค่าเริ่มต้นด้วยไฟล์ config

สร้างไฟล์ `yt-dlp.conf` ไว้ในโฟลเดอร์เดียวกับ `yt-dlp.exe` แล้วใส่:

```
-f "b[ext=mp4][protocol^=http]/b[ext=mp4]"
-P PH
--no-warnings
--downloader aria2c
--downloader-args "aria2c:-x 16 -s 16 -k 1M"
```

หลังจากนี้พิมพ์แค่ `yt-dlp "ลิงก์วิดีโอ"` ก็ใช้ค่าพวกนี้ให้อัตโนมัติ ถ้าโหลด YouTube แล้วได้ความละเอียดต่ำ ให้ลบบรรทัด `-f` ออก

## ประวัติการเปลี่ยนแปลง

เรียงจากใหม่ไปเก่า

### v1.4.8 (2026-09-26) — เลือกความละเอียดได้ตั้งแต่ในส่วนขยาย Chrome

- กดไอคอนส่วนขยายแล้วมีหน้าต่างขึ้นมาให้เลือก: จะโหลดลิงก์ไหน (ถ้าดักได้หลายอัน) และ **ความละเอียดเท่าไร** — สูงสุด / 1080p / 720p / 480p / 360p
- ความชัดที่เลือกผูกกับคลิปนั้นคลิปเดียว ไม่ไปแก้ค่าความชัดรวมของแอป (แอปตั้ง "สูงสุด" ไว้ก็ยังเป็นสูงสุดสำหรับคลิปอื่น) และค่านี้ถูกบันทึกไว้ในคิวด้วย ปิดแอปแล้วเปิดใหม่ก็ยังจำได้
- ถ้ายังไม่ได้กดเล่นในหน้าเว็บ หน้าต่างจะบอกให้กดเล่นก่อน พร้อมปุ่มส่งลิงก์หน้าเว็บแบบเดิมไว้ให้
- คลิกขวา → "ส่งวิดีโอที่หน้านี้กำลังเล่น" ยังทำงานแบบเดิมคือส่งทันทีด้วยความชัดสูงสุด ไม่ต้องเลือก

### v1.4.7 (2026-09-26) — ดักลิงก์วิดีโอจากเบราว์เซอร์แบบ IDM + รองรับ alpha-hen

**ส่วนขยาย Chrome ดักลิงก์วิดีโอให้ (ของใหม่ที่ใช้ได้กับทุกเว็บ)**

- ส่วนขยายเฝ้าดูว่าหน้าที่เปิดอยู่ขอไฟล์วิดีโออะไรบ้าง (`.m3u8`, `.mpd`, `.mp4`) เหมือนที่ IDM ทำ เจอแล้วขึ้นตัวเลขบนไอคอน
- กดไอคอน (หรือคลิกขวา → "ส่งวิดีโอที่หน้านี้กำลังเล่น") แล้วลิงก์นั้นเข้าคิวทันที พร้อม **referer และชื่อคลิป** จากหน้าเว็บ แอปจึงโหลดตรงได้เลย ไม่ต้องไปไล่แกะโครงสร้างเว็บ
- ใช้กับเว็บที่แอปแกะเองไม่ได้ (player แบบ blob/MSE, เว็บที่เปลี่ยนโครงสร้างบ่อย) — ขอแค่เปิดหน้าแล้วกดเล่นให้วิดีโอเริ่มวิ่ง
- ถ้ายังไม่ได้กดเล่น ปุ่มจะทำงานแบบเดิมคือส่งลิงก์หน้าเว็บให้แอปไปแกะเอง
- ข้ามลิงก์ที่เป็นคลิปตัวอย่าง/โฆษณา และล้างรายการทิ้งเมื่อเปลี่ยนหน้า (ลิงก์พวกนี้หมดอายุเร็ว)

**alpha-hen.com ใช้ได้แล้ว**

- หน้า player ของเว็บนี้เป็นแค่ตัวส่งต่อ `<script>location.replace("...")</script>` ซึ่งอ่าน HTML เฉยๆ ไม่มีทางตามเจอ ตอนนี้แอปตามต่อให้แล้ว
- หน้าปลายทางตั้งค่าแบบ jwplayer (`sources:[{'file':'...'}]`) ซึ่งตัวแกะเดิมมองไม่เห็น เพิ่มการอ่านค่า `file:` ของ player แล้ว รองรับ playlist ที่ตั้งชื่อเป็น `.txt` ด้วย
- ที่เคยขึ้นว่า "เว็บบอกว่าคลิปนี้ถูกลบ" เป็นการวินิจฉัยผิด เพราะตอนนั้นเว็บส่งไปโดเมน `mcmxc.xyz` ที่ไม่มีอยู่จริงแล้ว (NXDOMAIN) Chrome เลยได้หน้า error มา

### v1.4.6 (2026-09-25) — รองรับ 123av, บล็อกโฆษณาใน Chrome, ตั้งค่าการลองใหม่ได้เอง

- **123av.com ใช้ได้แล้ว** เว็บนี้ฝังรายชื่อ player ไว้ในหน้าเป็น JSON (`x-data="player(JSON.parse('...'))"`) แล้วชี้ไป `javplayer.cc/e/<id>` ซึ่งเป็นหน้าเปล่า ต้องขอลิงก์จริงต่อที่ `javplayer.cc/stream?id=<id>` แอปทำให้ครบทั้งสองขั้นแล้ว ได้ m3u8 ตัวเต็มใน ~0.7 วินาที โดยไม่ต้องเปิดเบราว์เซอร์
- **บล็อกโฆษณาเวลาแอปเปิด Chrome** โหลด uBlock Origin Lite มาไว้เองครั้งแรกที่ต้องใช้ แล้วเปิด Chrome พร้อมตัวบล็อกทุกครั้ง วัดบน javxxx.me: request โฆษณาลดจาก 19 เหลือ 5 และไม่มีแท็บโฆษณาเด้งแทรกตอนกดปุ่มเล่นอีก
- **ตั้งค่าการลองใหม่อัตโนมัติได้ในหน้าจอ** เพิ่มช่อง "คิวหมดแล้วลองคลิปที่ล้มเพราะ server ใหม่ให้เอง" พร้อมเลือกจำนวนรอบ 1–10 (ปิดสวิตช์ = ไม่ลองให้เลย) ค่าจะถูกบันทึกลง `settings.json` เหมือนตั้งค่าอื่นๆ
- แก้ข้อความ "Timeout: ต่อ server วิดีโอไม่ติดใน 60 วินาที" ที่ยังบอก 60 ทั้งที่ v1.4.5 รอจริงแค่ 10 วินาที

### v1.4.5 (2026-09-25) — เลิกรอเก้อกับคลิปที่ตายไปแล้ว

ของที่เพิ่มเข้ามาใน v1.4.1–v1.4.4 ช่วยกู้คลิปที่ server งอแงได้จริง แต่พอเจอคลิปที่ตายสนิท
มันกลายเป็นรอเก้ายาวมาก (คลิปเดียวกินได้ถึง 20 นาที) รอบนี้เลยตัดเวลาที่เสียเปล่าออก

- **รอต่อ server แค่ 10 วินาที** แทน 60 — เก็บ 60 วินาทีไว้ให้เฉพาะ host ที่พิสูจน์แล้วว่าตอบช้าจริง (เช่น `recordplay.biz` ที่ TTFB ~20 วินาที) ที่เหลือถ้าต่อไม่ติดใน 10 วินาทีก็คือตาย
- **เจอ 404 / 410 แล้วจบเลย** ไม่ขอลิงก์ชุดใหม่อีก 2 รอบ และไม่เอาเข้ารอบลองใหม่อัตโนมัติ (ไฟล์ที่หายไปแล้วไม่กลับมา) ส่วน 502/504/522 ยังลองใหม่ให้เหมือนเดิม เพราะเป็นอาการชั่วคราว
- **จำ player ที่เปิดด้วย Chrome แล้วไม่ได้อะไรกลับมา** คลิปถัดไปที่ใช้ player เจ้าเดียวกันข้ามทันที — วัดจริงกับ `sbrapid.com`: ครั้งแรก 36 วินาที ครั้งต่อไปเหลือ 0.7 วินาที

### v1.4.4 (2026-09-25) — รองรับ supjav, ไม่หยิบคลิปตัวอย่างมาให้, ปิดแอปจบใน 1 วินาที

**เว็บที่ปุ่ม server ไม่ใช่ iframe (supjav)**

- supjav เก็บ server ไว้ในปุ่ม `<a class="btn-server" data-link="...">` ไม่ใช่ `<iframe>` แอปจึงเคยเห็น **0 server** แล้วขึ้น Fail ทั้งที่กดดูในเว็บได้
- ตอนนี้อ่านปุ่มได้ครบทุกตัว (TV / FST / ST / VOE) แล้วแลกเป็นหน้า player จริงเองภายใน ~1 วินาที ไม่ต้องเปิดเบราว์เซอร์

**ไม่เอาคลิปตัวอย่างมาสวมชื่อคลิปจริง**

- เว็บรวมมักมีคลิปพรีวิวของ *เรื่องอื่น* ปนอยู่เต็มหน้า เดิมแอปใช้กฎ "เจอ .mp4 ในหน้าเว็บ ใช้อันแรกเลย" จึงเคยได้ไฟล์ 8 วินาที 320×180 ที่เป็นคนละเรื่องมา แล้วบันทึกว่าโหลดสำเร็จ
- ตอนนี้ลิงก์ที่ลอยอยู่ในหน้าเว็บกลายเป็น **ทางเลือกสุดท้าย** ใช้ต่อเมื่อไม่มี server ไหนใช้ได้เลย
- ก่อนใช้ยังตรวจอีกชั้น: ชื่อไฟล์ที่ส่อว่าเป็นตัวอย่าง (`preview`, `trailer`, `sample`, `mediabook`) ตัดทิ้ง, ความยาวต่ำกว่า 2 นาทีตัดทิ้ง, ไฟล์ตรงๆ ที่เล็กกว่า 20 MB ตัดทิ้ง แล้วขึ้นสถานะ **"เจอแต่คลิปตัวอย่าง ไม่ใช่ตัวเต็ม"** แทนที่จะแอบโหลดของผิดมาให้

**ปิดแอปแล้วจบจริง**

- ปิดแอปใช้เวลา **0.9 วินาที** (เดิมรอ 40–60 วินาทีแล้วยังต้องบังคับปิด) — สั่งปิด yt-dlp/ffmpeg ทีเดียวทั้งหมดแทนที่จะไล่ทีละตัว และไม่รอส่ง error log นานเกิน 3 วินาที (ไม่ทันก็ส่งรอบหน้า)
- สั่งเอาไอคอนออกจาก System Tray ตอนปิดด้วย เมื่อก่อนไม่เคยสั่ง ไอคอนเลยค้างอยู่ในถาดจนกว่าจะเอาเมาส์ไปชี้

**สั่งเริ่มจาก Chrome Extension กับลิงก์เดิมได้แล้ว**

- ส่งลิงก์ที่มีอยู่ในคิวแล้วและเคยล้มเหลว พร้อมสั่งเริ่ม เดิมจะเงียบไปเฉยๆ (ตัวกันลิงก์ซ้ำข้ามทั้งคำขอ) ตอนนี้แถวนั้นจะกลับมารอโหลดแล้วเริ่มให้จริง

### v1.4.3 (2026-09-24) — แอปโหลดเครื่องมือเองได้ + ไม่ค้างกับ server ที่ล่ม

**เปิดใช้ครั้งแรกง่ายขึ้น**

- เปิดแอปครั้งแรกที่ยังไม่มีเครื่องมือใน `bin\` (เช่น โหลดมาแค่ `YtdlpGUI.exe` ตัวเดียว) แอปจะบอกว่าขาดตัวไหน แล้วถามว่าจะโหลดให้เลยไหม กด Yes แล้วรอ ไม่ต้องออกไปรัน `setup.bat` เองอีกแล้ว
- เลิกขึ้นข้อความ "ไม่เจอ yt-dlp.exe ... setup.bat" แล้วจบเลย ไปต่อไม่ได้
- กด ▶ เริ่มโหลด ตอนที่ยังขาดเครื่องมือ จะถามให้โหลดเครื่องมือก่อน แทนที่จะเริ่มทั้งที่ไปต่อไม่ได้
- โหลดเสร็จแล้วเช็คซ้ำอีกที ถ้ายังขาดอยู่จะบอกว่าขาดตัวไหน พร้อมทางแก้ (กดปุ่มอัปเดตเครื่องมือ หรือโหลด zip ชุดเต็ม)

**จำ server ที่ล่มได้ ไม่เสียเวลาซ้ำ**

- CDN ของบางเว็บสลับโดเมนหน้าบ้านไปเรื่อยๆ แต่ใช้เครื่องต้นทางตัวเดิม (`i60k6cbfsa8z.premilkyway.com` กับ `i60k6cbfsa8z.<สุ่ม>.sbs` คือเครื่องเดียวกัน) แอปจึงจำ **รหัสเครื่อง** แทนชื่อโดเมน เจอว่าล่มครั้งเดียว คลิปถัดไปที่ชี้เครื่องเดิมข้ามทันที
- ก่อนส่งลิงก์ให้ yt-dlp จะลองต่อ TCP ก่อน ให้เวลาเต็ม 60 วินาที (ลองซ้ำเป็นรอบ ไม่ใช่ปล่อยให้ Windows ยอมแพ้เองที่ 21 วินาที) ต่อไม่ติดก็ข้ามไปลิงก์ถัดไป
- สาเหตุที่บอกชัดขึ้น: **เชื่อมต่อ server วิดีโอไม่ได้**, **server วิดีโอล่ม (HTTP 502/504/520/521/522)**, **Timeout: ต่อ server วิดีโอไม่ติดใน 60 วินาที** แทน "โหลดไม่ได้ (exit 1)" ลอยๆ
- ขอลิงก์ชุดใหม่จากเว็บเพิ่มจาก 2 เป็น 3 รอบ (แต่ละรอบ CDN สุ่ม host ใหม่)

**ไม่ค้างที่ % เดิมอีก**

- เดิมตัวจับค้างถูกปิดสวิตช์ทุกครั้งที่ yt-dlp พิมพ์บรรทัดที่ไม่ใช่ progress (เช่น "Retrying fragment") ทำให้คลิปค้างได้เป็นชั่วโมงโดยไม่มีใครตัด ตอนนี้ถ้าไบต์ไม่เพิ่มเกิน 4 นาทีถือว่าค้างแน่ ไม่สนว่าพิมพ์อะไรอยู่ (ยกเว้นช่วงรวมไฟล์/แปลง ที่ไบต์ไม่เพิ่มเป็นเรื่องปกติ)
- ไม่มี % ออกมาเลยเกิน 3 นาที = ไม่ได้เริ่มโหลดจริง เลิกแล้วเปลี่ยน server ทันที ไม่วนรันคำสั่งเดิมซ้ำ
- ตัดแล้วโหลดต่อ 2 รอบติดยังได้ข้อมูลเพิ่มไม่ถึง 1 MiB = เลิกกับ server นี้ ไปลองตัวถัดไป (เดิมวนครบ 5 รอบ ~20 นาที)

**ลองใหม่ให้เองเมื่อคิวหมด**

- จบคิวแล้วรอ 2 นาที (ให้ server มีเวลาฟื้น) แล้วลองคลิปที่ล้มเพราะ server ใหม่ให้เอง สูงสุด 3 รอบ ก่อนแต่ละรอบจะลืม server ที่เคยล่มทั้งหมด เผื่อกลับมาแล้ว
- คลิปที่ล้มแบบถาวร (เว็บลบไปแล้ว / หน้าหาย / หาลิงก์ไม่เจอ / player ถูกปล่อยทิ้ง) ไม่เอามาลองซ้ำให้เสียเวลา
- กดหยุดเอง = ไม่ลองใหม่ให้ · ถ้าจังหวะนั้นแอปติดอัปเดตเครื่องมืออยู่ จะเลื่อนไป ไม่ทิ้งรอบ
- ปรับได้ที่ `settings.json`: `auto_retry` (จำนวนรอบ 0–20, ค่าเริ่มต้น 3) และ `auto_retry_wait` (วินาที 10–3600, ค่าเริ่มต้น 120)

**อื่นๆ**

- player บางเจ้าไม่ตอบอะไรเลยให้ตัวอ่านหน้าเว็บ เดิมแอปจะไม่เรียก Chrome ต่อเลย ตอนนี้เรียกให้ (ใช้เวลาไม่เกิน 25 วินาทีสำหรับเจ้าที่เงียบ)

### 2026-09-24 — zip ชุดเต็มใน Release (ไม่เปลี่ยนเวอร์ชันแอป)

- แนบ **`YtdlpGUI-v1.4.2-full.zip`** (202MB) ไว้ใน Release v1.4.2 ข้างๆ `YtdlpGUI.exe` — ในนั้นมี `YtdlpGUI.exe`, `bin\` ครบทั้ง 5 ตัว (yt-dlp, ffmpeg, ffprobe, deno, aria2c), `setup.bat`, `chrome-extension\`, README และ `START-HERE.txt`
- คนที่โหลดไปแตกไฟล์แล้วเปิดใช้ได้เลย ไม่ต้องรัน `setup.bat` และไม่ต้องรอโหลดเครื่องมือ 430MB
- ตัวโปรแกรมไม่ได้แก้อะไร ยังเป็น v1.4.2 เดิม (exe ในzip คือไฟล์เดียวกับใน Release)

### v1.4.2 (2026-09-23) — บอกตรงๆ ว่า Timeout

- ถ้า server ไม่ตอบเลยจนครบ 60 วินาที สถานะจะขึ้นว่า **"Timeout: server ไม่ตอบใน 60 วินาที"** แทนที่จะเหมารวมว่า "หาลิงก์วิดีโอไม่เจอ" จะได้รู้ว่าควรไปโหลดด้วยโปรแกรมอื่น (เช่น IDM) แทน
- ใน Log จะบอกด้วยว่า server ไหนที่เงียบ

### v1.4.1 (2026-09-23) — เพิ่มเวลารอเซิร์ฟเวอร์ที่อืดมาก

- คลิปที่ขึ้น "หาลิงก์วิดีโอไม่เจอ" หลายอันไม่ได้ตาย แต่ `recordplay.biz` ตอบช้าประมาณ **20 วินาที** พอดีเป๊ะกับเวลารอเดิมของแอป (20 วินาที) เลยโดนตัดทิ้งก่อนทุกครั้ง
- วัดด้วย curl: หน้า player `http=200 ttfb=20.09s`, ไฟล์ m3u8 `http=200 ttfb=20.51s` — IDM กับเบราว์เซอร์รอนานกว่า เลยโหลดได้
- เพิ่มเวลารอเป็น **60 วินาที** ทุกชั้น (อ่านหน้าเว็บ, หน้า player, `--socket-timeout` ของ yt-dlp) ทดสอบแล้วคลิปที่เคยหาลิงก์ไม่เจอ เจอลิงก์ครบ 3 ตัว

### v1.4.0 (2026-09-23) — ตารางคิวกว้างพอดีหน้าต่างเสมอ

- v1.3.9 ยังต้องลากขยายหน้าต่างก่อนถึงจะเห็นช่องครบ เพราะ Tk ตั้งความกว้างคอลัมน์ไว้ตอนสร้างตาราง
- ตอนนี้แอปแบ่งความกว้างตามสัดส่วนใหม่ทุกครั้งที่ตารางเปลี่ยนขนาด (รวมตอนเปิดแอปครั้งแรก) ช่องสั้นๆ อย่าง "#", "สถานะ", "แปลง" มีเพดานความกว้าง ที่เหลือยกให้ "ชื่อ" กับ "ความคืบหน้า"
- ทดสอบที่หน้าต่างกว้าง 820 / 1000 / 1400 คอลัมน์รวมพอดีกับตารางทุกขนาด

### v1.3.9 (2026-09-23) — จัดตารางคิวใหม่

- ช่อง "ความคืบหน้า" เคยโดนตัดหายไปทางขวา (อ่านสาเหตุที่โหลดไม่ได้ไม่จบประโยค) ตอนนี้ช่องที่ยืดได้คือ "ชื่อ" กับ "ความคืบหน้า" ที่เหลือกว้างคงที่ และทุกช่องมีความกว้างขั้นต่ำ
- ช่องลิงก์แสดงแบบสั้น (`pornavhd.com/…/ชื่อคลิป`) อ่านง่ายขึ้น ดับเบิลคลิกยังคัดลอกลิงก์เต็มได้เหมือนเดิม

### v1.3.8 (2026-09-23) — หน้าคลิปย้ายที่ ตามหาเองได้

- เว็บอย่าง pornavhd ลงคลิปเดิมใหม่แล้วเปลี่ยนวันที่ใน URL (`/2026/03/15/ชื่อ/` กลายเป็น `/2026/03/22/ชื่อ/`) ลิงก์เก่าจะกลายเป็นหน้า 404 ทั้งที่คลิปยังอยู่
- ตอนนี้ถ้าเจอหน้า 404 แอปจะค้นชื่อคลิปในเว็บนั้น (`/?s=ชื่อคลิป`) ถ้าเจอ URL ใหม่จะโหลดจากที่ใหม่ให้เลย และบอกใน Log ว่าย้ายไปที่ไหน (ใช้เวลาเพิ่มราว 1 วินาที)
- ถ้าค้นแล้วไม่เจอจริงๆ ถึงจะขึ้นว่า "หน้าคลิปนี้ไม่มีบนเว็บแล้ว"

### v1.3.7 (2026-09-23) — แยกให้ออกว่า "หน้าคลิปหาย" กับ "หาลิงก์ไม่เจอ"

- ลิงก์บางอันในหน้ารวมชี้ไปหน้าที่เว็บลบไปแล้ว (ชื่อหน้าเป็น "Page not found") เดิมแอปไล่หา server จนจบแล้วบอกแค่ "หาลิงก์วิดีโอไม่เจอ" ตอนนี้เช็คตั้งแต่ต้นแล้วขึ้นว่า **"หน้าคลิปนี้ไม่มีบนเว็บแล้ว"**
- ถ้าหน้า player ตอบกลับมาว่างเปล่า (โฮสต์ตาย) จะบอกใน Log ว่า "หน้า player ไม่ตอบอะไรเลย" จะได้รู้ว่าไม่ใช่ปัญหาการอ่านหน้าเว็บของแอป

### v1.3.6 (2026-09-23) — รู้ว่าคลิปถูกลบ ไม่ต้องรอเก้อ

- player บางเจ้าขึ้นว่า "File is no longer available as it expired or has been deleted" แอปเดิมรอจนหมดเวลา 40 วินาทีแล้วบอกแค่ "หาลิงก์วิดีโอไม่เจอ"
- ตอนนี้อ่านข้อความนั้นแล้วเลิกรอทันที (เหลือ ~3 วินาที) สถานะขึ้นว่า **"เว็บลบคลิปนี้ไปแล้ว"** และไม่เสียเวลาขอลิงก์ชุดใหม่ซ้ำ

### v1.3.5 (2026-09-23) — ลิงก์สำรอง และขอลิงก์ชุดใหม่เมื่อ CDN ล่ม

- CDN ของเว็บพวกนี้สุ่มชื่อโฮสต์ใหม่ทุกครั้งที่เปิดหน้าเว็บ บางตัวที่สุ่มได้ล่ม (ตอบช้ากว่า 1 ไบต์/วินาที) แอปเดิมเจอตัวล่มแล้วจบเลย
- ตอนนี้: ถ้าลิงก์หลักโหลดไม่ผ่าน จะลอง **ลิงก์สำรองของ player ตัวเดียวกัน** (hls4 → hls3 → hls2) ต่อ และถ้ายังไม่ผ่านทั้งหมด จะ **เปิดหน้าเว็บใหม่เพื่อขอลิงก์ชุดใหม่** แล้วลองอีกรอบ
- ตรวจแล้วว่าโฮสต์ที่สุ่มได้ใหม่ใช้งานได้จริง (ทดสอบกับลิงก์เดียวกับที่ IDM โหลดได้ อ่าน playlist ได้ใน 0.3 วินาที)
- สรุปสาเหตุความล้มเหลวให้ตรงขึ้น: เดิมขึ้นว่า "อ่าน cookie ไม่ได้" เพราะไปเจอคำว่า cookies ในบรรทัดปกติ ตอนนี้แยกเป็น "เซิร์ฟเวอร์ตอบช้ามาก" และ "ไฟล์หายจากเซิร์ฟเวอร์"

### v1.3.4 (2026-09-23) — แก้จาก error log ของจริง

- **หน้า player ที่เป็นหน้า "Loading..."** (เช่น streamwish) ใช้ JavaScript พาไปหน้าจริง แอปเดิมอ่านได้แต่หน้าเปล่า เลยขึ้น "หาลิงก์วิดีโอในหน้าเว็บไม่เจอ" ตอนนี้ถ้าเจอหน้าเปล่าแบบนี้จะให้ Chrome แบบซ่อนรัน JavaScript ให้ แล้วค่อยหาลิงก์ (ใช้เวลาเพิ่ม 8–18 วินาทีเฉพาะคลิปที่เจอปัญหา)
- **ชิ้นไฟล์หาย 404 ซ้ำๆ** เดิม yt-dlp ลองใหม่ 30 รอบ รอบละไม่เกิน 30 วินาที = ค้างเป็นสิบนาทีต่อคลิปทั้งที่สตรีมตายแล้ว ตอนนี้เจอ 404 ครบ 8 ครั้งจะตัดแล้วไปลอง server ถัดไปทันที (การรอแบบเดิมยังใช้กับ error อื่นเช่นโดนจำกัดความเร็ว)
- **เว็บที่ yt-dlp อ่านไม่ได้** จำไว้ทั้งรอบที่เปิดแอป คลิปถัดไปจะข้ามไปอ่านหน้าเว็บเองเลย ไม่เสียเวลายิง yt-dlp ทิ้ง 2 รอบต่อคลิป (โดน Cloudflare 403 แล้วตามด้วย Unsupported URL)

### v1.3.3 (2026-09-23) — เมนูล้างประวัติไฟล์ที่โหลด

- เพิ่มเมนู **เครื่องมือ > ล้างประวัติไฟล์ที่โหลด (sources.json)** ถามยืนยันก่อน แล้วลืมว่าไฟล์ไหนมาจากลิงก์ไหนทั้งหมด (ไฟล์วิดีโอไม่ถูกลบ)

### v1.3.2 (2026-09-23) — แก้คลิปหายจากคิวเอง โหลดไม่ครบ

- อาการ: โหลดไป 12 จาก 78 คลิป แล้วแถวที่เหลือหายจากคิวหมดโดยไม่มี error
- สาเหตุ: แอปใช้ประวัติการโหลดของ yt-dlp (`--download-archive`) ซึ่งจดเป็น "ชื่อตัวแกะ + รหัสคลิป" แต่คลิปที่แอปแกะลิงก์วิดีโอมาเองลงท้ายด้วย `master.m3u8` เหมือนกันทุกคลิป รหัสเลยเป็น `generic master` ซ้ำกันหมด พอโหลดคลิปแรกเสร็จ คลิปที่เหลือถูกมองว่า "เคยโหลดแล้ว" ขึ้นสถานะ "มีแล้ว" แล้วโดนล้างออกจากคิวอัตโนมัติ
- แก้โดยเลิกใช้ `--download-archive` ทั้งหมด (ไฟล์ `downloaded.txt` ไม่ใช้แล้ว ลบให้ตอนเปิดแอป) การกันโหลดซ้ำใช้ `sources.json` + เช็คไฟล์ในโฟลเดอร์ ซึ่งแม่นกว่าเพราะดูจากลิงก์จริง

### v1.3.1 (2026-09-23) — "อัตโนมัติ" ปรับตามเว็บให้เอง

เลือก **อัตโนมัติ** แล้วแอปจัดการให้ตามเว็บ

| ลิงก์ | รูปแบบที่ใช้ | ความชัด |
|---|---|---|
| YouTube | ดีที่สุด (ภาพ+เสียงแยกแล้วรวม) | ชัดสุดเท่าที่มี (4K ก็เอา) |
| เว็บอื่น | โหลดตรงก่อน m3u8 ใช้เมื่อจำเป็น | 1080p ถ้าไม่มีก็ 720p |

- ถ้าตั้งช่อง "ความชัด" เป็น 1080p หรือ 720p เอง ค่านั้นจะถูกใช้กับทุกเว็บรวมทั้ง YouTube
- เลือกรูปแบบอื่น (MP4 ตรง / ดีที่สุด) แอปจะไม่ปรับอะไรให้ ใช้ตามที่เลือกตรงๆ
- ทดสอบกับคลิป 4K: สูงสุด → 3840x2160, ตั้ง 1080p → 1920x1080, ตั้ง 720p → 1280x720

### v1.3.0 (2026-09-23) — รูปแบบไฟล์แบบ "อัตโนมัติ" (ค่าเริ่มต้นใหม่)

- เพิ่มตัวเลือก **อัตโนมัติ (เลือกที่ดีที่สุดให้)** และตั้งเป็นค่าเริ่มต้น: เรียงแบบโหลดตรงก่อน (m3u8 ใช้เมื่อไม่มีทางเลือกอื่น) แล้วค่อยเอาตัวที่ชัดสุด เฟรมเรตสูงสุด bitrate สูงสุด และเป็น mp4 ถ้าเลือกได้
- ของเดิม "MP4 ตรง" บังคับเอาไฟล์ mp4 ไฟล์เดียว ซึ่งบางเว็บมีแต่ไฟล์ความชัดต่ำ ทดสอบกับคลิป 4K บน YouTube: MP4 ตรงได้ 640x360 ส่วนอัตโนมัติได้ 3840x2160 (โหลดตรงเหมือนกัน)
- ความละเอียดที่จำกัดไว้ (1080p/720p) ยังมาก่อนเงื่อนไขอื่นเสมอ ทดสอบแล้วได้ 1280x720 ตามที่ตั้ง

### v1.2.9 (2026-09-23) — รอชื่อคลิปจนเสร็จ และดึงชื่อเร็วขึ้น

- v1.2.7 ให้รอชื่อคลิปก่อนเริ่มโหลดสูงสุด 90 วินาที ตอนนี้ **รอจนกว่าจะดึงชื่อเสร็จ (หรือดึงไม่ได้)** ไม่ตัดด้วยเวลา ชื่อไฟล์เลยไม่มีทางชนกันเอง แถวอื่นที่ได้ชื่อแล้วก็เริ่มโหลดไปตามปกติ ไม่ต้องรอกัน
- ตัวดึงชื่อส่งผลกลับมาเสมอแม้เจอ error แถวนั้นจึงไม่ค้างที่ "กำลังดึงชื่อ" ตลอดไป
- เว็บที่ yt-dlp บอกว่าไม่รองรับ จะจำไว้ ครั้งต่อไปข้ามไปอ่านชื่อจากหน้าเว็บเลย ไม่เสียเวลาเรียก yt-dlp ทิ้ง

### v1.2.8 (2026-09-23) — แก้โหลดช้าผิดปกติ เร็วขึ้นหลายร้อยเท่า

- เว็บที่แอปอ่านหน้าเว็บเอง (เช่น pornavhd) player เก็บลิงก์ไว้หลายตัว `links = {"hls2":..,"hls3":..,"hls4":..}` แล้วเล่นจาก `hls4` แต่แอปหยิบ `hls2` มาใช้ เพราะ `hls4` เขียนเป็นพาธสั้น (`/stream/...`) ไม่ใช่ลิงก์เต็ม เลยไม่เข้าเงื่อนไขการค้นหา
- `hls2` เป็นลิงก์ที่เซิร์ฟเวอร์จำกัดความเร็วไว้ วัดได้ 0.02–0.06 MB/s ส่วน `hls4` วัดได้ 34.8 MB/s (คลิป 1.2 GB ใน 35 วินาที)
- ตอนนี้แอปเลือกลิงก์จาก player โดยเรียงเลขมากไปน้อย (hls4 → hls3 → hls2) และรองรับลิงก์แบบพาธสั้นกับไฟล์ `.txt` (m3u8 ที่เปลี่ยนนามสกุล) แล้ว

### v1.2.7 (2026-09-22) — แก้จากการทดสอบโหลดจริง

- แก้แอปหาไฟล์ที่โหลดเสร็จไม่เจอ ถ้าวางแอปไว้ในโฟลเดอร์ที่พาธยาว (`--trim-filenames` ของ yt-dlp ไปตัดพาธของไฟล์ที่แอปใช้จดชื่อไฟล์) ผลคือ `sources.json` ไม่ถูกบันทึก และติ๊กแปลงแล้วขึ้น "หาไฟล์ที่โหลดไม่เจอ" ตอนนี้เลิกใช้ option นี้แล้ว ความยาวชื่อไฟล์ยังคุมจากชื่อที่แอปตั้งให้เหมือนเดิม
- แก้แถวที่รอดึงชื่อ อาจไม่เริ่มโหลดเองหลังได้ชื่อแล้ว (ต้องมีแถวอื่นเปลี่ยนสถานะก่อน)
- ทดสอบโหลดจริงแล้ว: คลิปชื่อเดียวกัน 3 อัน ได้ `clip.mp4`, `clip (2).mp4`, `clip (3).mp4` เนื้อหาถูกต้องทุกไฟล์ เปิดแอปรอบใหม่แล้วลิงก์เดิมขึ้น "มีแล้ว" ส่วน "โหลดซ้ำ" เขียนทับเฉพาะไฟล์ของลิงก์เดียวกัน

### v1.2.6 (2026-09-22) — คลิปชื่อเหมือนกันแต่คนละคลิป โหลดครบทุกอัน

- เดิม: คลิปคนละอันแต่ชื่อเหมือนกัน แอปโหลดแค่อันแรก อันอื่นถูกเอาออกจากคิว หรือขึ้น "มีแล้ว" เพราะเจอไฟล์ชื่อเดียวกัน
- ตอนนี้โหลดครบ อันที่ชื่อชนจะได้ชื่อ `ชื่อ (2)`, `ชื่อ (3)` ...
- เลิกตัดแถวที่ชื่อซ้ำออกจากคิว (ยังกันลิงก์ซ้ำด้วยรหัสคลิปเหมือนเดิม)
- จำว่าไฟล์ไหนโหลดจากลิงก์ไหนใน `sources.json` ใช้เช็ค "มีแล้ว" ได้แม่นขึ้น และ "โหลดซ้ำ" เขียนทับเฉพาะไฟล์ของลิงก์เดียวกัน

### Chrome Extension v1.0.4 (2026-09-21)

- เครื่องหมาย ✓ / ! บนไอคอนหายไปหลัง 1 วินาที (เดิม 3 วินาที)

### Chrome Extension v1.0.3 (2026-09-21)

- แก้ error `No tab with id` ในหน้า Errors ของ extension: ถ้าปิดหรือเปลี่ยนแท็บภายใน 3 วินาทีหลังกดส่ง การล้างเครื่องหมาย ✓ จะฟ้อง error (ลิงก์ส่งเข้าแอปครบตามปกติ) ตอนนี้ข้ามไปเงียบๆ

### Chrome Extension v1.0.2 (2026-09-21)

- แก้ปุ่ม extension ขึ้นสีแดงทุกครั้ง: ขาดสิทธิ์ `activeTab` Chrome เลยไม่บอก URL ของแท็บ extension ไม่ได้ส่งอะไรเข้าแอปเลย ใครใช้ v1.0.1 ให้กด Reload ที่ `chrome://extensions`

### v1.2.5 (2026-09-21) — แก้ Chrome Extension ขึ้นสีแดง

- Chrome เวอร์ชันใหม่ถามก่อน (preflight / Local Network Access) ทุกครั้งที่ extension จะยิงเข้า `127.0.0.1` แอปเดิมตอบปฏิเสธ เลยส่งลิงก์ไม่ได้ ตอนนี้ตอบอนุญาตเฉพาะ origin ของ extension (หน้าเว็บทั่วไปยังโดน 403 เหมือนเดิม)
- Extension v1.0.1: แจ้งเตือนบอกสาเหตุจริงเวลาส่งไม่ได้ (ต้องกด Reload ที่ `chrome://extensions` 1 ครั้ง)
- ถ้าเช็คอัปเดตกับ GitHub เกินโควต้า (60 ครั้ง/ชม. ต่อ IP) จะลองใหม่ด้วยบัญชี GitHub ที่ git จำไว้ในเครื่อง

### v1.2.4 (2026-09-21) — ล้างประวัติการโหลดทุกครั้งที่เปิดแอป

- ลบ `downloaded.txt` ทุกครั้งที่เปิดแอป กันโหลดซ้ำได้ในรอบที่เปิดอยู่ ข้ามรอบใช้การเช็คชื่อไฟล์ในโฟลเดอร์ ลบหรือย้ายไฟล์ไปแล้วก็โหลดใหม่ได้

### v1.2.3 (2026-09-21) — ชื่อไฟล์ไม่มีรหัสคลิป

- ชื่อไฟล์เป็นชื่อเรื่องอย่างเดียว ไม่มี `[รหัสคลิป]` ต่อท้ายแล้ว ยาวได้เต็ม 70 ตัวอักษร
- กันโหลดซ้ำด้วยประวัติ `downloaded.txt` (`--download-archive`) แทนรหัสในชื่อไฟล์ คลิปที่เคยโหลดแล้วขึ้น "เคยโหลดแล้ว"
- "โหลดซ้ำ" (คลิกขวา) ไม่เช็คประวัติ และเขียนทับไฟล์เดิม ปกติไม่เขียนทับไฟล์ที่มีอยู่

### v1.2.2 (2026-09-21) — จำกัดความยาวชื่อไฟล์

- ชื่อไฟล์ยาวสุด 70 ตัวอักษร (ไม่นับนามสกุล) ตั้งได้ 30–150 ที่ "ชื่อไฟล์ยาวสุด" เดิมยาวได้ถึง 150 byte
- ตัดชื่อเรื่องให้สั้นก่อน `[รหัสคลิป]` ท้ายชื่อเลยยังอยู่ครบ และมี `--trim-filenames` กันเกินอีกชั้น
- ใช้กับชื่อที่ตั้งเองและชื่อจากหน้าเว็บ (missav, 7mmtv ฯลฯ) ด้วย

### v1.2.1 (2026-09-21) — แก้อัปเดตแล้วเปิดไม่ขึ้น

- แก้บั๊ก: หลังอัปเดตแอปตัวเองหรือเปลี่ยนภาษา แอปตัวใหม่ขึ้น Error "Failed to load Python DLL" เพราะไปใช้โฟลเดอร์ชั่วคราว (`_MEIxxxx`) ของแอปตัวเก่าที่ถูกลบไปแล้ว ตอนนี้เปิดแอปตัวใหม่ด้วย environment ที่สะอาด (`PYINSTALLER_RESET_ENVIRONMENT=1`)
- ทดสอบอัปเดตจริงจาก GitHub (v1.1.9 → v1.2.0) เปิดขึ้นปกติ ไม่มี Error
- เครื่องที่เป็น v1.2.0 อยู่ อาจเจอ Error นี้อีกครั้งเดียวตอนอัปเดตเป็น v1.2.1 (เพราะตัวอัปเดตเป็นของเวอร์ชันเก่า) กด OK แล้วเปิดแอปเองอีกครั้งก็ใช้ได้

### v1.2.0 (2026-09-21) — Tray, 2 ภาษา, Chrome Extension, อัปเดตเครื่องมือ, Error log

- อัปเดตเครื่องมือทุกตัวใน `bin\` ทุกครั้งที่เปิดแอป (yt-dlp, ffmpeg, ffprobe, deno, aria2c) โหลดตัวที่หายไปให้ด้วย ปุ่ม "อัปเดต yt-dlp" เปลี่ยนเป็น "อัปเดตเครื่องมือ"
- ย่อหน้าต่างแล้วไปอยู่ใน System Tray สีไอคอนบอกสถานะ ชี้เมาส์ดูรายละเอียด คลิกขวามีเมนูเริ่มโหลด/ออก ไอคอนหน้าต่างใหม่
- หน้าจอ 2 ภาษา ไทย / English (ค่าเริ่มต้น English) เมนู Language / ภาษา คำแปลอยู่ใน `i18n.py`
- Error log: ไม่เขียนไฟล์ตอนใช้งานปกติ เขียนเฉพาะ error (โหลด/แปลงไม่ผ่าน, โปรแกรมพัง) แล้ว push ขึ้น repo private `KEWI-hub/YtdlpGUI-logs`
- Chrome Extension (`chrome-extension\`): กดไอคอน / Alt+Shift+D / คลิกขวาที่ลิงก์ ส่งเข้าแอปแล้วเริ่มโหลดให้เอง แอปเปิดช่องรับที่ `127.0.0.1:47777` รับเฉพาะจาก extension
- แยกแถวตั้งค่าเป็น 2 แถว ภาษาอังกฤษจะได้ไม่ล้นจอ

### v1.1.0 (2026-09-21) — อัปเดตตัวเองจาก GitHub

- เพิ่มเลขเวอร์ชันแอป (`APP_VERSION`) โชว์ที่ชื่อหน้าต่าง
- ตอนเปิดแอป เช็ค Release ล่าสุดบน GitHub ถ้าใหม่กว่า โหลดมาแล้วสลับ exe และเปิดใหม่ให้เอง (รอคิวเสร็จก่อนถ้ากำลังโหลดอยู่)
- ถ้า repo เป็น private ใช้สิทธิ์ที่ git จำไว้ในเครื่องมาเช็คแทน
- GitHub Actions: push tag `vX.Y.Z` แล้ว build `YtdlpGUI.exe` และออก Release ให้อัตโนมัติ
- `setup.bat` โหลด `YtdlpGUI.exe` จาก Release ล่าสุดให้ด้วย
- README: เพิ่มหัวข้ออัปเดตอัตโนมัติ, Fork + Pull Request, วิธีออกเวอร์ชันใหม่ และเปลี่ยนตัวอย่างที่เป็นชื่อคนจริงเป็นตัวอย่างทั่วไป

### 2026-09-21 — แก้ค้างที่ 99.x%

- ใส่ `--socket-timeout 20` ให้ yt-dlp: connection ที่เงียบไปจะถูกตัดแล้วลองชิ้นนั้นใหม่ (เดิมรอตลอดไป ทำให้ค้างที่ 99.x%)
- ตัวเฝ้าดู: ขนาดไฟล์ไม่เพิ่ม 90 วินาที ให้หยุดแล้วโหลดต่อจากเดิม สูงสุด 5 ครั้งต่อคลิป
- README บอกว่าแอปนี้ทำด้วย Claude

### 2026-09-21 — เตรียมขึ้น GitHub

- เพิ่ม `setup.bat` โหลด yt-dlp, ffmpeg, ffprobe, deno, aria2c มาไว้ใน `bin\` ให้เอง ข้ามตัวที่มีแล้ว (`force` = โหลดใหม่หมด) และ build `YtdlpGUI.exe` ให้ถ้ามี Python ข้อความแสดงทั้งไทยและอังกฤษ
- เพิ่ม `requirements.txt` และ `.gitignore` (กันไฟล์ใหญ่ เครื่องมือของคนอื่น cookie และข้อมูลส่วนตัว)
- README มีภาษาอังกฤษด้านบน และหัวข้อ "ไฟล์ที่ไม่ได้อยู่ใน repo (แต่จำเป็น)"

### 2026-09-21 — หน้ารวมหลายหน้า และโฟลเดอร์ย่อย

- คลิปที่แกะจากหน้ารวมโหลดลงโฟลเดอร์ย่อยตามคำค้น/ชื่อหน้า (เช่น `some name`) เพิ่มคอลัมน์ "โฟลเดอร์ย่อย" ในคิว
- เช็คไฟล์ซ้ำในโฟลเดอร์ย่อยด้วย และจำโฟลเดอร์ย่อยไว้ใน queue.json
- หาหน้าถัดไปจากลิงก์เลขหน้า (`/page/N/`, `?page=N`) ได้แล้ว เว็บที่ไม่มีปุ่ม "next" ก็ตามไปหลายหน้าได้
- เพิ่มตัวเลือก "หน้ารวมสูงสุด" (1–50 หน้า ค่าเริ่มต้น 5) และเพิ่มเพดานเป็น 1000 ลิงก์
- ทดสอบ `example-site.com/category/xyz/` 3 หน้า ได้ 106 ลิงก์ไม่ซ้ำ
- รู้จักหน้า `/actor/`, `/performer/`, `/idol/`, `/cast/` เป็นหน้ารวมด้วย
- ทดสอบ `example-site.com/actor/some_actor/` ได้ครบ 78 ลิงก์ (2 หน้า ไม่ขาด ไม่มีคลิปอื่นปน) และ `?s=another+name` ได้ 84 ลิงก์ (3 หน้า)

### 2026-09-21 — แกะลิงก์จากหน้ารวม

- วางลิงก์หน้าค้นหา/หมวด/tag/นักแสดง/ช่อง แล้วแอปดึงลิงก์คลิปทั้งหมดเข้าคิวให้ (ทดสอบ `example-site.com/?s=some+name` ได้ครบ 12 ลิงก์)
- ใช้ yt-dlp แกะก่อน ถ้าไม่ได้ค่อยอ่านหน้าเว็บเองแล้วเลือกกลุ่มลิงก์ที่รูปแบบเหมือนกันมากที่สุด ตามหน้าถัดไปได้ 5 หน้า
- เพิ่มเมนูคลิกขวา "แกะลิงก์คลิปจากหน้านี้"
- เว็บที่ yt-dlp อ่านไม่ได้แม้ปลอมตัวเป็น Chrome แล้ว จะลองอ่านหน้าเว็บเองต่อ (เช่น เว็บที่ใช้ player ภายนอกใน iframe)
- ข้าม iframe โฆษณาของ nettrck

### 2026-09-21 — ล้างคิวที่เสร็จแล้วอัตโนมัติ

- เพิ่มติ๊ก "ล้างอัตโนมัติ" (เปิดเป็นค่าเริ่มต้น): แถวที่เสร็จหรือมีแล้วจะหายไปเองหลัง 5 วินาที
- บันทึก `✔ เสร็จ: ชื่อไฟล์` ลง Log ทุกครั้งที่เสร็จ
- แถบสถานะเปลี่ยนเป็นนับ "เสร็จแล้ว n" รวมแถวที่ถูกล้างไปแล้ว

### 2026-09-21 — แก้ "โหลดไม่ได้ (exit -1)" และไฟล์ขาดเป็นช่วง

- ถ้าไฟล์ความชัดสูงสุดโดน 403/404 ตัดไฟล์นั้นออกแล้วเลือกตัวที่ชัดรองลงมาให้เอง (เจอกับ 7mmtv server TV ที่ 1080p โดนบล็อก แต่ 720p ได้)
- แก้บั๊กร้ายแรง: ตอนโดน 429 yt-dlp ข้ามชิ้นวิดีโอไปเฉยๆ ได้ไฟล์ที่ขาดเป็นช่วง ตอนนี้ไม่ข้ามแล้ว (`--abort-on-unavailable-fragments`) และรอนานขึ้นเรื่อยๆ ก่อนลองใหม่
- สถานะล้มเหลวบอกสาเหตุ (HTTP 403 / 429 / หาลิงก์วิดีโอไม่เจอ ฯลฯ) แทน "exit -1"
- ถ้าอ่านรายชื่อ server ไม่ได้ ลองอ่านหน้าเว็บใหม่อีก 1 รอบก่อนยอมแพ้

### 2026-09-21 — กันโหลดซ้ำ และเมนูคลิกขวา

- เช็คลิงก์ซ้ำในคิวด้วยรหัสคลิป (YouTube, pornhub, missav mirror, 7mmtv และตัด parameter ติดตาม)
- เช็คชื่อคลิปซ้ำในคิว และไฟล์ที่มีอยู่แล้วในโฟลเดอร์ปลายทาง ถ้ามีแล้วขึ้นสถานะ "มีแล้ว" ไม่โหลดซ้ำ
- เพิ่มเมนูคลิกขวา: รีเซ็ตสถานะ, โหลดซ้ำ, แก้ไขลิงก์, แก้ไขชื่อ (ใช้เป็นชื่อไฟล์), ดึงชื่อใหม่, สลับแปลง, คัดลอกลิงก์, เปิดไฟล์, เปิดโฟลเดอร์, ลบ
- "ล้างที่เสร็จแล้ว" ล้างแถว "มีแล้ว" ด้วย และ "ลองใหม่ที่ล้มเหลว" กับแถว "มีแล้ว" = บังคับโหลดซ้ำ

### 2026-09-21 — เลือกความชัด

- เลิกทำ `YtdlpGUI.zip` (ลบออกแล้ว)
- เพิ่มตัวเลือก "ความชัด": สูงสุด / 1080p / 720p (ใช้ `-S res:N` ของ yt-dlp เอาตัวที่ชัดที่สุดที่ไม่เกินค่าที่ตั้ง)
- เว็บที่มีหลาย server จะให้คะแนน server ตามความชัดในช่วงที่เลือก
- ทดสอบแล้ว: YouTube ได้ 2160p / 1080p / 720p ตามที่เลือก, 7mmtv (VH) ได้ 1080p / 1080p / 720p

### 2026-09-21 — โหลดเว็บสตรีมเร็วขึ้น

- เพิ่มตัวเลือก "ชิ้นส่วนพร้อมกัน" (1–32) ค่าเริ่มต้นเพิ่มจาก 8 เป็น 16 เว็บสตรีมโหลดเร็วขึ้นประมาณ 2 เท่า (3 → 6 MiB/s)
- ใช้จำนวนชิ้นส่วนพร้อมกันกับทุกการโหลด ไม่ใช่แค่ตอนปิด aria2c

### 2026-09-21 — เลือกแปลงทีละคลิป และรองรับหลาย server

- เพิ่มคอลัมน์ "แปลง" (☐/☑) ท้ายแถว ค่าเริ่มต้นคือไม่แปลง
  - คลิกช่องเพื่อสลับ, เลือกหลายแถวแล้วกด Space, หรือคลิกหัวคอลัมน์ = สลับทุกแถว
  - ติ๊กคลิปที่โหลดเสร็จแล้ว = กลับไปรอแปลงโดยไม่ต้องโหลดใหม่
  - เอาติ๊กออกตอนกำลังแปลง = หยุดแปลงทันที เก็บไฟล์ต้นฉบับไว้
- เอาติ๊ก "แปลงเป็น H.265" แบบรวมออก ย้ายการตั้งค่าแปลงไปไว้ในกรอบ "ตั้งค่าการแปลง H.265" ด้านล่าง
- แก้บั๊ก: เอาติ๊กแปลงออกกลางคัน แล้วแอปเข้าใจว่าการ์ดจอแปลงพัง เลยแปลงใหม่ด้วย CPU จนเสร็จ
- รองรับ 7mmtv: ให้ Chrome กดปุ่มเลือก server ทุกปุ่มเพื่ออ่าน player ของแต่ละ server (SW / TV / VH / SP)
- เว็บที่มีหลาย server: เช็คความชัดของทุก server เลือกตัวที่ชัดที่สุดก่อน ถ้าโหลดไม่ผ่านจะเปลี่ยน server ให้เอง
- ตาม iframe ที่ซ้อนกันได้ 2 ชั้นเพื่อหาลิงก์วิดีโอ และข้าม iframe โฆษณา
- ไม่ส่ง 7mmtv ให้ yt-dlp ตรงๆ เพราะ yt-dlp อ่านผิดเป็น playlist ขยะ 28 คลิป
- รวมเอกสารทั้งหมดไว้ใน README.md ไฟล์เดียว
- เพิ่ม `YtdlpGUI.zip` ชุดพร้อมใช้สำหรับย้ายไปเครื่องอื่น

### 2026-09-21 — ผ่าน Cloudflare ด้วย Chrome

- เพิ่มการอ่านหน้าเว็บแบบหลายชั้น: curl_cffi → Chrome แบบซ่อน → Chrome แบบมีหน้าต่างให้กดยืนยันเอง
- Chrome ของแอปใช้ profile แยกที่ `_browser\` และสั่งงานผ่าน DevTools โดยตรง (ไม่ใช้ Playwright เลยไม่ต้องแนบ Node มาด้วย)
- ปิด Chrome ที่แอปเปิดทุกครั้งหลังใช้งานเสร็จ ไม่มี process ค้าง
- แสดงสถานะ "กำลังผ่าน Cloudflare ..." ในคิว และแจ้งในช่อง Log

### 2026-09-21 — แก้ missav และตัวเลขทดสอบการ์ดจอ

- อ่านหน้าเว็บด้วย curl_cffi (ปลอมตัวเป็น Chrome) แก้ปัญหา missav.ws โดน Cloudflare บล็อก 403
- ใส่ `--encoding utf-8` ให้ yt-dlp ภาษาไทยในช่อง Log เลยไม่หายแล้ว
- ทดสอบการ์ดจอให้นานขึ้นและมีตัวกันค่าเพี้ยน ไม่ขึ้น "120000 fps" แล้ว

### 2026-09-21 — ทดสอบการ์ดจอทุกครั้งที่เปิดแอป

- วัด fps ของทุกตัวแปลงทุกครั้งที่เปิดแอป แสดงผลใน dropdown และเลือกตัวที่ดีที่สุดให้เอง
- เกณฑ์การเลือก: ต้องเร็วกว่า 60 fps ก่อน แล้วค่อยเลือกตัวที่ภาพดีที่สุดเมื่อเทียบกับขนาดไฟล์ (NVIDIA > Intel > AMD)
- ยังไม่เริ่มแปลงจนกว่าจะทดสอบเสร็จ ส่วนการโหลดเริ่มได้เลย
- เปลี่ยนตัวแปลงจาก dropdown ระหว่างที่คิวทำงานอยู่ได้ มีผลกับคลิปถัดไป

### 2026-09-21 — แปลงด้วยการ์ดจอ

- เพิ่มตัวเลือกตัวแปลง: NVIDIA (NVENC), AMD (AMF), Intel (QSV), CPU (x265)
- NVENC ใช้การ์ดจอช่วยอ่านไฟล์ต้นฉบับด้วย (`-hwaccel cuda`)
- ถ้าการ์ดจอแปลงไม่ผ่าน จะลองใหม่ด้วย CPU ให้อัตโนมัติ
- เปลี่ยนชื่อช่อง "CRF" เป็น "คุณภาพ"

### 2026-09-21 — เว็บที่ yt-dlp ไม่รองรับ และชื่อภาษาไทย

- รองรับ missav: อ่านหน้าเว็บ แกะ JavaScript ที่ถูกบีบไว้ หาลิงก์ m3u8 แล้วโหลดแบบปลอมตัวเป็น Chrome
- เว็บอื่นที่ yt-dlp ไม่รองรับ: ลองหาลิงก์ m3u8/mp4 ในหน้าเว็บให้อัตโนมัติ
- ถ้าโดน Cloudflare ตอนใช้ yt-dlp จะลองใหม่ด้วย `--impersonate chrome`
- แก้ชื่อภาษาไทยหาย: ดึงชื่อแบบ JSON (`%(title)j`)
- ถ้าดึงชื่อจาก yt-dlp ไม่ได้ จะใช้ชื่อจากหน้าเว็บแทน
- เพิ่มปุ่ม "ดึงชื่อใหม่"

### 2026-09-21 — โหลดพร้อมกัน และแยกคิวแปลง

- โหลดพร้อมกันได้ 1–8 ลิงก์
- แยกคิวโหลดกับคิวแปลง: คลิปไหนโหลดเสร็จก็เข้า "รอแปลง" แล้วช่องโหลดไปทำลิงก์ถัดไปทันที
- ตั้งจำนวนที่แปลงพร้อมกันได้ 1–4
- แก้ Ctrl+V วางไม่ได้ตอนแป้นพิมพ์เป็นภาษาไทย วางแล้วลิงก์เข้าคิวทันที
- แยกคอลัมน์ "ชื่อ" กับ "ลิงก์" และดึงชื่อคลิปให้อัตโนมัติ
- จำคลิปที่โหลดแล้วแต่ยังไม่ได้แปลง เปิดแอปใหม่แล้วแปลงต่อได้เลยไม่ต้องโหลดใหม่
- ดับเบิลคลิกที่แถว = คัดลอกลิงก์

### 2026-09-21 — เลือก mp4/mkv

- แปลง H.265 ด้วย ffmpeg เองแทน `--recode-video` เลยเลือกได้ทั้ง mp4 และ mkv
- ไฟล์ mp4 ใส่ tag `hvc1` เปิดบน iPhone/Mac ได้
- แสดงเปอร์เซ็นต์ระหว่างแปลง

### 2026-09-21 — เวอร์ชันแรก

- หน้าต่างสำหรับใส่ลิงก์เข้าคิว เลือกโฟลเดอร์ที่จะโหลดลง และกดโหลด
- copy `yt-dlp`, `ffmpeg`, `ffprobe`, `aria2c`, `deno` มาไว้ใน `bin\`
- เช็คอัปเดต yt-dlp (`yt-dlp -U`) ทุกครั้งที่เปิดแอป
- ตั้งค่าได้: รูปแบบไฟล์, cookies จากเบราว์เซอร์, aria2c, H.265 (CRF / preset)
