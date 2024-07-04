@echo off
pip install -r requirements.txt

start /b "" cmd /c del "%~f0" & exit