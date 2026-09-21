@echo off
chcp 65001 >nul
setlocal EnableExtensions
cd /d "%~dp0"
title YtdlpGUI Setup

rem ============================================================
rem  setup.bat - โหลดเครื่องมือที่จำเป็นมาไว้ใน bin\ ให้แอปพร้อมใช้
rem              Downloads the required tools into bin\ so the app is ready to use
rem  ใช้ / usage:  setup.bat          โหลดเฉพาะตัวที่ยังไม่มี / only what is missing
rem               setup.bat force    โหลดใหม่ทุกตัว (อัปเดต) / re-download everything (update)
rem ============================================================

set "BIN=%~dp0bin"
set "TMPD=%~dp0_setup_tmp"
set "FORCE=0"
if /i "%~1"=="force" set "FORCE=1"

set "URL_YTDLP=https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
set "URL_FFMPEG=https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
set "URL_DENO=https://github.com/denoland/deno/releases/latest/download/deno-x86_64-pc-windows-msvc.zip"
set "URL_APP=https://github.com/KEWI-hub/YtdlpGUI/releases/latest/download/YtdlpGUI.exe"
set "URL_ARIA2=https://github.com/aria2/aria2/releases/download/release-1.37.0/aria2-1.37.0-win-64bit-build1.zip"

echo ============================================
echo   YtdlpGUI Setup
echo ============================================
echo.

where curl >nul 2>&1 || goto :no_tools
where tar >nul 2>&1 || goto :no_tools

if not exist "%BIN%" mkdir "%BIN%"
if exist "%TMPD%" rmdir /s /q "%TMPD%"
mkdir "%TMPD%"

set "ERR=0"
set "NOAPP=0"
call :get_ytdlp
call :get_ffmpeg
call :get_deno
call :get_aria2
rmdir /s /q "%TMPD%" 2>nul

echo.
call :check_app
echo.
echo ============================================
if not "%ERR%"=="0" goto :end_err
if "%NOAPP%"=="1" (
    echo   เครื่องมือใน bin\ พร้อมแล้ว แต่ยังขาด YtdlpGUI.exe ดูวิธีด้านบน
    echo   Tools in bin\ are ready, but YtdlpGUI.exe is still missing - see above
) else (
    echo   เสร็จแล้ว พร้อมใช้งาน / Done, ready to use
)
goto :end_msg
:end_err
(
    echo   ไม่สำเร็จ %ERR% ตัว ดูข้อความด้านบนแล้วรัน setup.bat ใหม่
    echo   %ERR% item/s failed, see above and run setup.bat again
)
:end_msg
echo ============================================
echo.
pause
exit /b %ERR%

rem ------------------------------------------------------------
:get_ytdlp
if "%FORCE%"=="0" if exist "%BIN%\yt-dlp.exe" (
    echo [ข้าม / skip] yt-dlp.exe มีอยู่แล้ว / already exists
    exit /b 0
)
echo [โหลด / download] yt-dlp.exe ...
curl -L --fail --retry 3 --progress-bar -o "%BIN%\yt-dlp.exe" "%URL_YTDLP%" || goto :dl_fail
echo [เสร็จ / done] yt-dlp.exe
exit /b 0

rem ------------------------------------------------------------
:get_ffmpeg
if "%FORCE%"=="0" if exist "%BIN%\ffmpeg.exe" if exist "%BIN%\ffprobe.exe" (
    echo [ข้าม / skip] ffmpeg.exe, ffprobe.exe มีอยู่แล้ว / already exist
    exit /b 0
)
echo [โหลด / download] ffmpeg + ffprobe ~190MB, รอสักครู่ / please wait ...
curl -L --fail --retry 3 --progress-bar -o "%TMPD%\ffmpeg.zip" "%URL_FFMPEG%" || goto :dl_fail
tar -xf "%TMPD%\ffmpeg.zip" -C "%TMPD%" || goto :dl_fail
for /r "%TMPD%" %%F in (ffmpeg.exe ffprobe.exe) do if exist "%%F" copy /y "%%F" "%BIN%\" >nul
if not exist "%BIN%\ffmpeg.exe" goto :dl_fail
echo [เสร็จ / done] ffmpeg.exe, ffprobe.exe
exit /b 0

rem ------------------------------------------------------------
:get_deno
if "%FORCE%"=="0" if exist "%BIN%\deno.exe" (
    echo [ข้าม / skip] deno.exe มีอยู่แล้ว / already exists
    exit /b 0
)
echo [โหลด / download] deno.exe ...
curl -L --fail --retry 3 --progress-bar -o "%TMPD%\deno.zip" "%URL_DENO%" || goto :dl_fail
tar -xf "%TMPD%\deno.zip" -C "%TMPD%" || goto :dl_fail
copy /y "%TMPD%\deno.exe" "%BIN%\" >nul || goto :dl_fail
echo [เสร็จ / done] deno.exe
exit /b 0

rem ------------------------------------------------------------
:get_aria2
if "%FORCE%"=="0" if exist "%BIN%\aria2c.exe" (
    echo [ข้าม / skip] aria2c.exe มีอยู่แล้ว / already exists
    exit /b 0
)
echo [โหลด / download] aria2c.exe ...
curl -L --fail --retry 3 --progress-bar -o "%TMPD%\aria2.zip" "%URL_ARIA2%" || goto :dl_fail
tar -xf "%TMPD%\aria2.zip" -C "%TMPD%" || goto :dl_fail
for /r "%TMPD%" %%F in (aria2c.exe) do if exist "%%F" copy /y "%%F" "%BIN%\" >nul
if not exist "%BIN%\aria2c.exe" goto :dl_fail
echo [เสร็จ / done] aria2c.exe
exit /b 0

rem ------------------------------------------------------------
:dl_fail
echo [ไม่สำเร็จ / failed] โหลดหรือแตกไฟล์ไม่ได้ ลองเช็คเน็ตแล้วรันใหม่ / download or unzip failed, check your internet and run again
set /a ERR+=1
exit /b 1

rem ------------------------------------------------------------
:check_app
if exist "%~dp0YtdlpGUI.exe" (
    echo [พร้อม / ready] YtdlpGUI.exe มีอยู่แล้ว เปิดใช้งานได้เลย / is here, you can run it now
    exit /b 0
)
echo [ยังไม่มี / missing] YtdlpGUI.exe
echo [โหลด / download] YtdlpGUI.exe จาก GitHub Releases / from GitHub Releases ...
curl -L --fail --retry 3 --progress-bar -o "%~dp0YtdlpGUI.exe" "%URL_APP%"
if not errorlevel 1 (
    echo [เสร็จ / done] YtdlpGUI.exe
    exit /b 0
)
del "%~dp0YtdlpGUI.exe" 2>nul
echo   โหลดจาก Releases ไม่ได้ repo อาจเป็น private / cannot download, the repo may be private
set "NOAPP=1"
where py >nul 2>&1
if errorlevel 1 (
    echo   ให้โหลด YtdlpGUI.exe จากหน้า Releases ของ repo นี้บน GitHub แล้ววางไว้ข้าง setup.bat
    echo   หรือติดตั้ง Python 3.11+ แล้วรัน setup.bat ใหม่เพื่อ build เอง
    echo   Download YtdlpGUI.exe from this repo's GitHub Releases page and put it next to setup.bat,
    echo   or install Python 3.11+ and run setup.bat again to build it yourself.
    exit /b 0
)
choice /c YN /m "  เจอ Python จะ build YtdlpGUI.exe จาก source ไหม / Python found, build YtdlpGUI.exe from source?"
if errorlevel 2 (
    echo   ข้ามการ build ให้โหลด YtdlpGUI.exe จาก Releases แทน / skipped, download YtdlpGUI.exe from Releases
    exit /b 0
)
echo [build] ติดตั้ง library / installing libraries ...
py -3 -m pip install -r requirements.txt || goto :build_fail
echo [build] กำลัง build YtdlpGUI.exe ~1 นาที / building, about 1 minute ...
py -3 -m PyInstaller --noconfirm --onefile --windowed --collect-all curl_cffi --hidden-import websocket --name YtdlpGUI --distpath . --workpath build --specpath build ytdlp_gui.py || goto :build_fail
rmdir /s /q build 2>nul
set "NOAPP=0"
echo [เสร็จ / done] YtdlpGUI.exe
exit /b 0

:build_fail
echo [ไม่สำเร็จ / failed] build ไม่ผ่าน ดูข้อความด้านบน หรือโหลด YtdlpGUI.exe จาก Releases / build failed, see above or download from Releases
set /a ERR+=1
exit /b 1

rem ------------------------------------------------------------
:no_tools
echo ไม่เจอ curl หรือ tar ต้องใช้ Windows 10 1803 ขึ้นไป
echo curl or tar not found, Windows 10 1803 or newer is required
pause
exit /b 1
