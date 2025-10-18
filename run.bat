@echo off
setlocal EnableDelayedExpansion




set VENV_PATH="%~dp0\.windows_venv"
set PYTHON_VERSION=3.10.10



echo Checking if Python is installed...

python --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo Python is already installed, moving on...
    goto :python_environment 
)

echo Python, is not installed, initiating installation procedure...

set PYTHON_DOWNLOAD_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%/python-%PYTHON_VERSION%-amd64.exe
set INSTALL_DIR=%PROGRAMFILES%\Python\%PYTHON_VERSION%
set DOWNLOAD_PATH=%TEMP%\python_installer.exe

echo Downloading Python %PYTHON_VERSION%
bitsadmin /transfer "PythonDownload" /priority HIGH /dynamic "%PYTHON_DOWNLOAD_URL%" "%DOWNLOAD_PATH%"
if %ERRORLEVEL% neq 0 (
    echo Error: Failed to download python installer.
    goto :eof
)

echo Installing Python %PYTHON_VERSION%
"%DOWNLOAD_PATH%" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 TargetDir="%INSTALL_DIR%"
if %ERRORLEVEL% neq 0 (
    echo Error: Failed to install Python
    goto :eof
)

echo Cleaning up Files
del "%DOWNLOAD_PATH%"

echo Python %PYTHON_VERSION% installed successfully in %INSTALL_DIR% 


:python_environment
echo Setting up Python environment...

REM Check if .windows_venv directory exists
if not exist "%VENV_PATH%" (
    echo Creating virtual environment...
    "%INSTALL_DIR%"\python.exe -m venv "%VENV_PATH%"
    
    REM Check if venv creation was successful
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        echo Make sure Python is installed and accessible
        pause
        exit /b 1
    )
    
    echo Virtual environment created successfully
) else (
    echo Virtual environment already exists
)

REM Activate the virtual environment
echo Activating virtual environment...
call %VENV_PATH%\Scripts\activate.bat

REM Check if activation was successful
if not defined VIRTUAL_ENV (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo Virtual environment activated successfully

REM Check if requirements.txt exists before installing
if exist "requirements.txt" (
    echo Installing requirements...
    pip install -r requirements.txt
    
    REM Check if pip install was successful
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install requirements
        pause
        exit /b 1
    )
    
    echo Requirements installed successfully
) else (
    echo No requirements.txt found, Installation Failed
    goto :eof
)

REM Check if the Python script exists before running
if exist "%~dp0app\ui\Home.py" (
    echo Running Python script...
    "%VENV_PATH%\Scripts\streamlit.cmd" run "%~dp0app\ui\Home.py"
    
) else (
    echo ERROR: Python script 'app\ui\Home.py' not found
    pause
    exit /b 1
)
pause



