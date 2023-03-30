@echo off

REM Prompt the user with a description of what the script is about to do
echo This script will set the OPENSSL_ia32cap environment variable at a system level to "0x20000000" to fix a hard crash on Windows 11 machines with more recent versions of Intel processors.

REM Provide additional information about the issue
echo.
echo This fix is recommended for users who have experienced hard crashes while running Studio Library and Maya 2020+. For more information about this issue, please see the following link: https://forums.autodesk.com/t5/maya-programming/maya-2020-hard-crashes-from-urllib2/m-p/10833459#M14687
echo.

REM Prompt the user to confirm or cancel the script
set /p confirm=Do you want to continue? (y/n)

REM Check if the user wants to continue
if /i not "%confirm%"=="y" (
    echo Script cancelled.
    pause >nul
    exit /b 1
)

REM Check if the script is running with administrative privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo This script must be run as an administrator. Please right-click on the batch file and select "Run as administrator".
    pause >nul
    exit /b 1
)

REM Set the OPENSSL_ia32cap environment variable at a system level
setx OPENSSL_ia32cap "0x20000000" /m

REM Display a message indicating that the variable has been set
echo The OPENSSL_ia32cap environment variable has been set to "0x20000000".
pause >nul