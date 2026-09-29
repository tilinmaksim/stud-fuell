@echo off
cd /d "%~dp0"
set STUDEDA_NO_BROWSER=0
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 app.py
) else (
  python app.py
)
pause
