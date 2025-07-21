@echo off
REM XSD Visualizer Docker Runner for Windows
REM Usage: run-xsd-visualizer.bat "C:\path\to\xsd\files" "C:\path\to\output"

setlocal EnableDelayedExpansion

echo XSD Visualizer Docker Runner
echo ============================

REM Check if Docker is running
docker version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: Docker is not running or not installed.
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

REM Check arguments
if "%~1"=="" (
    echo Usage: %0 "input_directory" "output_directory"
    echo.
    echo Examples:
    echo   %0 "C:\MyXSDFiles" "C:\MyOutput"
    echo   %0 "." ".\output"
    pause
    exit /b 1
)

if "%~2"=="" (
    echo Usage: %0 "input_directory" "output_directory"
    echo.
    echo Examples:
    echo   %0 "C:\MyXSDFiles" "C:\MyOutput"
    echo   %0 "." ".\output"
    pause
    exit /b 1
)

set INPUT_DIR=%~1
set OUTPUT_DIR=%~2

REM Convert relative paths to absolute paths
if "%INPUT_DIR:~1,1%" neq ":" (
    for %%i in ("%INPUT_DIR%") do set INPUT_DIR=%%~fi
)

if "%OUTPUT_DIR:~1,1%" neq ":" (
    for %%i in ("%OUTPUT_DIR%") do set OUTPUT_DIR=%%~fi
)

REM Check if input directory exists
if not exist "%INPUT_DIR%" (
    echo ERROR: Input directory does not exist: %INPUT_DIR%
    pause
    exit /b 1
)

REM Create output directory if it doesn't exist
if not exist "%OUTPUT_DIR%" (
    echo Creating output directory: %OUTPUT_DIR%
    mkdir "%OUTPUT_DIR%"
)

echo Input directory: %INPUT_DIR%
echo Output directory: %OUTPUT_DIR%
echo.

REM Check if XSD Visualizer image exists, build if not
echo Checking for XSD Visualizer Docker image...
docker images xsd-visualizer:latest -q >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Building XSD Visualizer Docker image...
    docker build -t xsd-visualizer:latest .
    if %ERRORLEVEL% neq 0 (
        echo ERROR: Failed to build Docker image
        pause
        exit /b 1
    )
    echo Docker image built successfully!
    echo.
)

REM Run the container
echo Running XSD analysis...
echo.
docker run --rm ^
    -v "%INPUT_DIR%":/input ^
    -v "%OUTPUT_DIR%":/output ^
    xsd-visualizer:latest

if %ERRORLEVEL% equ 0 (
    echo.
    echo SUCCESS: Analysis complete!
    echo Results are available in: %OUTPUT_DIR%
    echo.
    echo Opening output directory...
    start "" "%OUTPUT_DIR%"
) else (
    echo.
    echo ERROR: Analysis failed
)

pause
