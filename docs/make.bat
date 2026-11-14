@echo off
set PYTHON=python
if "%1"=="" goto help
%PYTHON% -m sphinx -M %1 . _build
if errorlevel 1 exit /b 1
goto end
:help
echo Usage: make.bat ^<builder^>
echo Example: make.bat html
goto end
:end
