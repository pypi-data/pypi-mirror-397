@echo off
title ColorBridge Quick Start

:: Quick start ColorBridge in normal mode
cd /d "%~dp0ColorBridge"
if exist "main.py" (
    echo Starting ColorBridge...
    python main.py
) else (
    echo Error: main.py not found
    pause
)