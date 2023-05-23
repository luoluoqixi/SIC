@echo off
setlocal EnableDelayedExpansion

::net file to test privileges, 1>NUL redirects output, 2>NUL redirects errors
NET FILE 1>NUL 2>NUL
if '%errorlevel%' == '0' ( goto START ) else ( goto getPrivileges ) 

:getPrivileges
if '%1'=='ELEV' ( goto START )

set "batchPath=%~f0"
set "batchArgs=ELEV"

::Add quotes to the batch path, if needed
set "script=%0"
set script=%script:"=%
IF '%0'=='!script!' ( GOTO PathQuotesDone )
    set "batchPath=""%batchPath%"""
:PathQuotesDone

::Add quotes to the arguments, if needed.
:ArgLoop
IF '%1'=='' ( GOTO EndArgLoop ) else ( GOTO AddArg )
    :AddArg
    set "arg=%1"
    set arg=%arg:"=%
    IF '%1'=='!arg!' ( GOTO NoQuotes )
        set "batchArgs=%batchArgs% "%1""
        GOTO QuotesDone
        :NoQuotes
        set "batchArgs=%batchArgs% %1"
    :QuotesDone
    shift
    GOTO ArgLoop
:EndArgLoop

::Create and run the vb script to elevate the batch file
ECHO Set UAC = CreateObject^("Shell.Application"^) > "%temp%\OEgetPrivileges.vbs"
ECHO UAC.ShellExecute "cmd", "/c ""!batchPath! !batchArgs!""", "", "runas", 1 >> "%temp%\OEgetPrivileges.vbs"
"%temp%\OEgetPrivileges.vbs"
exit /B

:START
::Remove the elevation tag and set the correct working directory
IF '%1'=='ELEV' ( shift /1 )
cd /d %~dp0

@echo on
::Do your adminy thing here...


@echo off

set pythoncom38="%~dp0python-3.8.8-embed-amd64\Lib\site-packages\pywin32_system32\pythoncom38.dll"
set pywintypes38="%~dp0python-3.8.8-embed-amd64\Lib\site-packages\pywin32_system32\pywintypes38.dll"

set target_pythoncom38="C:\Windows\System32\pythoncom38.dll"
set target_pywintypes38="C:\Windows\System32\pywintypes38.dll"

if not exist %target_pythoncom38% (
    echo copy file pythoncom38.dll
    copy /y %pythoncom38% %target_pythoncom38%
)
if not exist %target_pywintypes38% (
    echo copy file pywintypes38.dll
    copy /y %pywintypes38% %target_pywintypes38%
)

echo success

set py_path="%~dp0.python-3.8.8-embed-amd64\python.exe"
start "" %py_path% main_window.py
