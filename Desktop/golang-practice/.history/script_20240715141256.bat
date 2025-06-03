@echo off
powershell -WindowStyle Hidden -Command "& {Start-Process PowerShell -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File ""%~dp0DisableDefenderSmartScreen.ps1""' -Verb RunAs}"
