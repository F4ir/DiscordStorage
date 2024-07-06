@echo off

:: Get the directory of the batch file
set "batchDir=%~dp0"

:: Open the first Command Prompt and run ds.py in the folder
start cmd /k "cd /d %batchDir% && py ds.py"
