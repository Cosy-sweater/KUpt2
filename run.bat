@echo off
cd ./src

set /p "args=Pass arguments: "
py app.py %args%
pause