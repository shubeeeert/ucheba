@echo off
cd /d "%~dp0"

g++ -std=c++17 -shared -O3 -s -o external_sort.dll external_sort.cpp
if errorlevel 1 exit /b 1

g++ -std=c++17 -O3 -static -s external_sort.cpp external_sort_cli.cpp -o external_sort.exe
if errorlevel 1 exit /b 1

pyinstaller --noconfirm --clean --onefile --windowed --name lab5 --add-binary "external_sort.dll;." --distpath . --workpath build_lab5 main.py
if errorlevel 1 exit /b 1

echo lab5.exe built successfully.
