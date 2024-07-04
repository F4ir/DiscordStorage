@echo off

:: Get the directory of the batch file
set "batchDir=%~dp0"

:: Open the first Command Prompt and run pocketbase.exe serve in the pocketbase folder
start cmd /k "cd /d %batchDir% && py ds.py"