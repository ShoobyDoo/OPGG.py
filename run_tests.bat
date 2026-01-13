@echo off
REM Simple test runner for Windows

if "%1"=="" (
    echo Running all tests...
    py -m pytest tests/ -v
) else if "%1"=="unit" (
    echo Running unit tests...
    py -m pytest tests/unit/ -v
) else if "%1"=="integration" (
    echo Running integration tests...
    py -m pytest tests/integration/ -v
) else if "%1"=="quick" (
    echo Running all tests ^(short output^)...
    py -m pytest tests/ -v --tb=line
) else if "%1"=="coverage" (
    echo Running tests with coverage...
    py -m pytest tests/ --cov=opgg --cov-report=html
) else if "%1"=="help" (
    echo.
    echo Available test targets:
    echo   test            - Run all tests ^(default^)
    echo   test unit       - Run unit tests only
    echo   test integration - Run integration tests only
    echo   test quick      - Run all tests with short output
    echo   test coverage   - Run tests with coverage report
    echo.
) else (
    echo Unknown target: %1
    echo Run 'test help' for available targets
)
