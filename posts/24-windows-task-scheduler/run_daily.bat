@echo off
REM Blog: https://automate-lab.tistory.com/24
REM Edit the three paths below before registering in Task Scheduler.
set PYTHONUTF8=1
set VENV_PY=C:\Users\you\projects\automate-lab\.venv\Scripts\python.exe
set SCRIPT=C:\Users\you\projects\automate-lab\posts\24-windows-task-scheduler\run_daily.py
set LOGDIR=C:\Users\you\projects\automate-lab\logs
if not exist "%LOGDIR%" mkdir "%LOGDIR%"
"%VENV_PY%" "%SCRIPT%" >> "%LOGDIR%\run.log" 2>&1
