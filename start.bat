@echo off
py -m pip install -r "%~dp0requirements.txt"
py "%~dp0hui_server.py"
pause
