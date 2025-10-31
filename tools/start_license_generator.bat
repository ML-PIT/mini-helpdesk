@echo off
REM ABoro-Soft License Generator Launcher
REM This starts the license generator GUI

cd /d "%~dp0"
start "" dist\license_generator.exe

REM Optional: Show a message
REM echo License Generator starting...
REM timeout /t 2 /nobreak
