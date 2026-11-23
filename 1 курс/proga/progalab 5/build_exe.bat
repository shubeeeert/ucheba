@echo off
cd /d "%~dp0"

g++ -std=c++17 -O3 -static -s external_sort.cpp external_sort_cli.cpp -o external_sort.exe
if errorlevel 1 exit /b 1

echo external_sort.exe built successfully.
