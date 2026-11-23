#include <windows.h>

#include <cstdio>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>

#include "external_sort.h"

namespace fs = std::filesystem;

static void print_progress(float value)
{
    static int last_percent = -1;
    int percent = static_cast<int>(value * 100.0f);
    if (percent < 0) percent = 0;
    if (percent > 100) percent = 100;

    if (percent != last_percent) {
        last_percent = percent;
        std::printf("\r[C++] Прогресс: %3d%%", percent);
        std::fflush(stdout);
    }
}

static std::string acp_to_utf8(const std::string &text)
{
    int wide_length = MultiByteToWideChar(CP_ACP, 0, text.c_str(), -1, nullptr, 0);
    std::wstring wide(static_cast<size_t>(wide_length), L'\0');
    MultiByteToWideChar(CP_ACP, 0, text.c_str(), -1, &wide[0], wide_length);
    if (!wide.empty() && wide.back() == L'\0') wide.pop_back();

    int utf8_length = WideCharToMultiByte(CP_UTF8, 0, wide.c_str(), -1, nullptr, 0, nullptr, nullptr);
    std::string utf8(static_cast<size_t>(utf8_length), '\0');
    WideCharToMultiByte(CP_UTF8, 0, wide.c_str(), -1, &utf8[0], utf8_length, nullptr, nullptr);
    if (!utf8.empty() && utf8.back() == '\0') utf8.pop_back();
    return utf8;
}

static fs::path acp_to_path(const std::string &text)
{
    int wide_length = MultiByteToWideChar(CP_ACP, 0, text.c_str(), -1, nullptr, 0);
    std::wstring wide(static_cast<size_t>(wide_length), L'\0');
    MultiByteToWideChar(CP_ACP, 0, text.c_str(), -1, &wide[0], wide_length);
    if (!wide.empty() && wide.back() == L'\0') wide.pop_back();
    return fs::path(wide);
}

static int parse_key(const std::string &s)
{
    if (s == "0" || s == "name" || s == "fio") return 0;
    if (s == "1" || s == "group") return 1;
    if (s == "2" || s == "dob" || s == "date") return 2;
    if (s == "3" || s == "height") return 3;
    if (s == "4" || s == "weight") return 4;
    if (s == "5" || s == "expulsion" || s == "ban") return 5;
    return -1;
}

static bool parse_direction(const std::string &s, bool &ok)
{
    ok = true;
    if (s == "asc" || s == "1" || s == "up" || s == "возр") return true;
    if (s == "desc" || s == "0" || s == "down" || s == "убыв") return false;
    ok = false;
    return true;
}

static void print_usage()
{
    std::cout
        << "External CSV sorter (C++)\n"
        << "Usage:\n"
        << "  external_sort.exe [file.csv] [key] [direction]\n\n"
        << "Arguments:\n"
        << "  file.csv   -- input CSV file (default: data.csv)\n"
        << "  key        -- 0=name, 1=group, 2=dob, 3=height, 4=weight, 5=expulsion\n"
        << "               (also accepts name/group/dob/height/weight/expulsion)\n"
        << "  direction  -- asc or desc (default: asc)\n\n"
        << "Result is written to sorted.txt next to the input file.\n";
}

int main(int argc, char **argv)
{
    SetConsoleOutputCP(CP_UTF8);

    std::string path = "data.csv";
    int key = 0;
    bool ascending = true;

    if (argc == 2 && (std::string(argv[1]) == "--help" || std::string(argv[1]) == "-h")) {
        print_usage();
        return 0;
    }

    if (argc > 1) path = argv[1];

    if (argc > 2) {
        key = parse_key(argv[2]);
        if (key < 0) {
            std::cerr << "Unknown key: " << argv[2] << "\n";
            print_usage();
            return 1;
        }
    }

    if (argc > 3) {
        bool ok = false;
        ascending = parse_direction(argv[3], ok);
        if (!ok) {
            std::cerr << "Unknown direction: " << argv[3] << "\n";
            print_usage();
            return 1;
        }
    }

    if (argc > 4) {
        print_usage();
        return 1;
    }

    fs::path inputPath = acp_to_path(path);
    std::ifstream check(inputPath, std::ios::binary | std::ios::ate);
    if (!check) {
        std::cerr << "Cannot open input file: " << path << "\n";
        return 1;
    }

    std::streamoff size = check.tellg();
    if (size <= 0) {
        std::cerr << "Input file is empty: " << path << "\n";
        return 1;
    }

    check.seekg(-1, std::ios::end);
    char last_char = 0;
    check.get(last_char);
    check.close();
    if (last_char != '\n') {
        std::cerr << "Input file must end with a newline character (LF).\n";
        return 1;
    }

    std::cout << "Sorting " << path << " by key " << key
              << " (" << (ascending ? "asc" : "desc") << ")...\n";

    std::string utf8_path = acp_to_utf8(path);
    bool ok = external_sort_ex(utf8_path.c_str(), key, ascending, print_progress, nullptr);
    if (!ok) {
        std::cerr << "Sorting failed.\n";
        return 1;
    }

    std::printf("\r[C++] Прогресс: 100%%\n");
    std::cout << "Done. Result: sorted.txt\n";
    return 0;
}
