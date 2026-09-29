@echo off
cd /d "%~dp0"
title Student Fuel Server
cls
echo ===============================================
echo           STUDENT FUEL - ЗАПУСК
echo ===============================================
echo.
where py >nul 2>nul
if %errorlevel%==0 (
    py -3 app.py
) else (
    python app.py
)
echo.
echo Сервер остановлен.
pause
