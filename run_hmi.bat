@echo off
title DLP KUMAR - Industrial VFD HMI
cd /d "%~dp0vfd_hmi"
python main.py
if errorlevel 1 (
    echo.
    echo Application exited with an error.
    pause
)
