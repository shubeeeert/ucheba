#include <algorithm>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <memory>
#include <queue>
#include <sstream>
#include <string>
#include <vector>

#ifdef _WIN32
#include <process.h>
#include <windows.h>
#endif

#include "external_sort.h"

using namespace std;
namespace fs = std::filesystem;

static const size_t READER_SIZE = 10ULL * 1024 * 1024;
static const size_t WRITER_SIZE = 10ULL * 1024 * 1024;

#pragma pack(push, 1)
struct Record {
    char name[64];      // Фамилия и имя
    char group[40];     // Обозначение учебной группы
    char dob[16];       // Дата рождения YYYY.MM.DD
    int32_t height;     // Рост, см
    float weight;       // Вес, кг
    bool expulsion;     // Признак отчисления
};
#pragma pack(pop)

static const size_t RECORD_SIZE = sizeof(Record); // 129 байт

struct MergeNode {
    Record rec;
    size_t fileIndex;
};

using Comparator = bool (*)(const Record &, const Record &);

static fs::path to_native_path(const char *text)
{
#ifdef _WIN32
    // GUI передаёт путь в UTF-8; Windows API ожидает UTF-16.
    int length = MultiByteToWideChar(CP_UTF8, 0, text, -1, nullptr, 0);
    if (length > 0) {
        wstring wide(static_cast<size_t>(length), L'\0');
        MultiByteToWideChar(CP_UTF8, 0, text, -1, &wide[0], length);
        if (!wide.empty() && wide.back() == L'\0') wide.pop_back();
        return fs::path(wide);
    }
#endif
    return fs::path(text);
}

static const Comparator comparators[2][6] = {
    { // index 0: по убыванию
        [](const Record &a, const Record &b) { return strcmp(a.name, b.name) > 0; },
        [](const Record &a, const Record &b) { return strcmp(a.group, b.group) > 0; },
        [](const Record &a, const Record &b) { return strcmp(a.dob, b.dob) > 0; },
        [](const Record &a, const Record &b) { return a.height > b.height; },
        [](const Record &a, const Record &b) { return a.weight > b.weight; },
        [](const Record &a, const Record &b) { return a.expulsion > b.expulsion; }
    },
    { // index 1: по возрастанию
        [](const Record &a, const Record &b) { return strcmp(a.name, b.name) < 0; },
        [](const Record &a, const Record &b) { return strcmp(a.group, b.group) < 0; },
        [](const Record &a, const Record &b) { return strcmp(a.dob, b.dob) < 0; },
        [](const Record &a, const Record &b) { return a.height < b.height; },
        [](const Record &a, const Record &b) { return a.weight < b.weight; },
        [](const Record &a, const Record &b) { return a.expulsion < b.expulsion; }
    }
};

static void copy_field(char *&cursor, char *destination, size_t capacity)
{
    size_t i = 0;
    while (*cursor != '\0' && *cursor != ',' && *cursor != '\n' && *cursor != '\r' && i + 1 < capacity) {
        destination[i++] = *cursor++;
    }
    destination[i] = '\0';
    if (*cursor == ',') ++cursor;
}

static bool parse_record(char *&cursor, Record &rec)
{
    while (*cursor == '\r' || *cursor == '\n') ++cursor;
    if (*cursor == '\0') return false;

    memset(&rec, 0, sizeof(rec));
    copy_field(cursor, rec.name, sizeof(rec.name));
    copy_field(cursor, rec.group, sizeof(rec.group));
    copy_field(cursor, rec.dob, sizeof(rec.dob));

    char *end = nullptr;
    rec.height = static_cast<int32_t>(strtol(cursor, &end, 10));
    cursor = end;
    if (*cursor == ',') ++cursor;

    rec.weight = strtof(cursor, &end);
    cursor = end;
    if (*cursor == ',') ++cursor;

    rec.expulsion = (strncmp(cursor, "true", 4) == 0);

    while (*cursor != '\0' && *cursor != '\n' && *cursor != '\r') ++cursor;
    if (*cursor == '\r') ++cursor;
    if (*cursor == '\n') ++cursor;
    return true;
}

static void write_field(char *&cursor, const char *value)
{
    while (*value != '\0') *cursor++ = *value++;
    *cursor++ = ',';
}

static void serialize(char *&cursor, const Record &rec)
{
    write_field(cursor, rec.name);
    write_field(cursor, rec.group);
    write_field(cursor, rec.dob);
    cursor += sprintf(cursor, "%d,%.1f,", rec.height, rec.weight);
    const char *flag = rec.expulsion ? "true" : "false";
    while (*flag != '\0') *cursor++ = *flag++;
    *cursor++ = '\n';
}

Export bool external_sort_ex(
    const char *path,
    int keyIndex,
    bool ascending,
    void (*progressCallback)(float),
    void (*timingCallback)(const char *)
)
{
    auto start_total = chrono::high_resolution_clock::now();
    auto report = [&](float value) {
        if (progressCallback) {
            if (value < 0.0f) value = 0.0f;
            if (value > 1.0f) value = 1.0f;
            progressCallback(value);
        }
    };

    if (path == nullptr || keyIndex < 0 || keyIndex > 5) {
        cerr << "[C++] Некорректные параметры сортировки.\n";
        return false;
    }

    fs::path inputPath = to_native_path(path);
    fs::path parent = inputPath.parent_path();
    if (parent.empty()) parent = fs::current_path();

    ifstream input(inputPath, ios::binary);
    if (!input.is_open()) {
        cerr << "[C++] Не удалось открыть входной файл: " << inputPath.string() << "\n";
        return false;
    }

    input.seekg(0, ios::end);
    streamoff sizeValue = input.tellg();
    if (sizeValue < 0) {
        cerr << "[C++] Не удалось определить размер входного файла.\n";
        input.close();
        return false;
    }
    size_t totalFileSize = static_cast<size_t>(sizeValue);
    input.seekg(0, ios::beg);

    fs::path outPath = parent / "sorted.txt";
    ofstream output(outPath, ios::binary | ios::trunc);
    if (!output.is_open()) {
        cerr << "[C++] Не удалось создать выходной файл: " << outPath.string() << "\n";
        input.close();
        return false;
    }

    if (totalFileSize == 0) {
        output.close();
        input.close();
        report(1.0f);
        string timing = "[C++] Входной файл пуст, sorted.txt создан.\n";
        cout << timing;
        if (timingCallback) timingCallback(timing.c_str());
        return true;
    }

#ifdef _WIN32
    unsigned long pid = GetCurrentProcessId();
#else
    long pid = static_cast<long>(getpid());
#endif
    fs::path tempDir = parent / (".lab5_cpp_tmp_" + to_string(pid));

    error_code ec;
    fs::remove_all(tempDir, ec);
    if (!fs::create_directories(tempDir, ec) && !fs::exists(tempDir)) {
        cerr << "[C++] Не удалось создать каталог временных файлов.\n";
        input.close();
        output.close();
        error_code removeError;
        fs::remove(outPath, removeError);
        return false;
    }

    vector<ifstream *> openFiles;
    auto removeOutput = [&]() {
        error_code removeError;
        fs::remove(outPath, removeError);
    };
    auto cleanup = [&]() {
        for (ifstream *file : openFiles) {
            if (file != nullptr) {
                if (file->is_open()) file->close();
                delete file;
            }
        }
        openFiles.clear();
        error_code cleanupError;
        fs::remove_all(tempDir, cleanupError);
    };

    size_t maxRecords = (totalFileSize / 100) * 4 / RECORD_SIZE;
    maxRecords = std::max<size_t>(2000, std::min<size_t>(300000, maxRecords));

    Comparator cmp = comparators[ascending ? 1 : 0][keyIndex];
    vector<Record> records;
    records.reserve(maxRecords);

    unique_ptr<char[]> readerBuffer(new char[READER_SIZE + 1]);
    size_t tempFileCount = 0;
    size_t processedBytes = 0;
    bool splitOk = true;

    auto flushChunk = [&]() -> bool {
        if (records.empty()) return true;
        sort(records.begin(), records.end(), cmp);
        fs::path chunkPath = tempDir / ("r" + to_string(tempFileCount++) + ".tmp");
        ofstream chunk(chunkPath, ios::binary | ios::trunc);
        if (!chunk.is_open()) {
            cerr << "[C++] Не удалось записать временный файл: " << chunkPath.string() << "\n";
            return false;
        }
        chunk.write(reinterpret_cast<const char *>(records.data()),
                    static_cast<streamsize>(records.size() * RECORD_SIZE));
        chunk.close();
        records.clear();
        return true;
    };

    report(0.0f);
    auto start_split = chrono::high_resolution_clock::now();

    while (true) {
        input.read(readerBuffer.get(), static_cast<streamsize>(READER_SIZE));
        streamsize bytesRead = input.gcount();
        if (bytesRead <= 0) break;

        size_t usable = static_cast<size_t>(bytesRead);
        if (bytesRead == static_cast<streamsize>(READER_SIZE) && input.good()) {
            size_t lastNewline = usable;
            while (lastNewline > 0 && readerBuffer[lastNewline - 1] != '\n') --lastNewline;
            if (lastNewline > 0 && lastNewline < usable) {
                input.seekg(-static_cast<streamsize>(usable - lastNewline), ios::cur);
                usable = lastNewline;
            }
        }

        readerBuffer[usable] = '\0';
        processedBytes += usable;

        char *cursor = readerBuffer.get();
        while (*cursor != '\0') {
            Record rec;
            if (parse_record(cursor, rec)) records.push_back(rec);
            if (records.size() >= maxRecords) {
                if (!flushChunk()) { splitOk = false; break; }
                report(static_cast<float>(min(1.0, processedBytes / static_cast<double>(totalFileSize))));
            }
        }
        if (!splitOk) break;
        report(static_cast<float>(min(1.0, processedBytes / static_cast<double>(totalFileSize))));
    }

    input.close();
    if (splitOk) splitOk = flushChunk();

    auto end_split = chrono::high_resolution_clock::now();
    chrono::duration<double> splitTime = end_split - start_split;

    if (!splitOk) {
        cleanup();
        output.close();
        removeOutput();
        return false;
    }

    if (tempFileCount == 0) {
        output.close();
        cleanup();
        report(1.0f);
        ostringstream emptyTiming;
        emptyTiming << "[C++] Этап разбиения: " << splitTime.count() << " с.\n"
                    << "[C++] Этап слияния: 0 с.\n"
                    << "[C++] Общее время: " << splitTime.count() << " с.\n";
        cout << emptyTiming.str();
        if (timingCallback) timingCallback(emptyTiming.str().c_str());
        return true;
    }

    report(0.0f);
    auto start_merge = chrono::high_resolution_clock::now();

    auto nodeComparator = [&](const MergeNode &a, const MergeNode &b) {
        return cmp(b.rec, a.rec);
    };
    priority_queue<MergeNode, vector<MergeNode>, decltype(nodeComparator)> queue(nodeComparator);

    for (size_t i = 0; i < tempFileCount; ++i) {
        fs::path chunkPath = tempDir / ("r" + to_string(i) + ".tmp");
        ifstream *file = new ifstream(chunkPath, ios::binary);
        openFiles.push_back(file);
        if (!file->is_open()) {
            cerr << "[C++] Не удалось открыть временный файл: " << chunkPath.string() << "\n";
            cleanup();
            output.close();
            removeOutput();
            return false;
        }
        Record rec;
        file->read(reinterpret_cast<char *>(&rec), static_cast<streamsize>(RECORD_SIZE));
        if (file->gcount() == static_cast<streamsize>(RECORD_SIZE)) {
            queue.push({rec, i});
        }
    }

    unique_ptr<char[]> writerBuffer(new char[WRITER_SIZE + 512]);
    char *writeCursor = writerBuffer.get();
    size_t writtenBytes = 0;
    bool mergeOk = true;

    while (!queue.empty()) {
        MergeNode top = queue.top();
        queue.pop();

        serialize(writeCursor, top.rec);
        if (static_cast<size_t>(writeCursor - writerBuffer.get()) > WRITER_SIZE) {
            streamsize chunkSize = writeCursor - writerBuffer.get();
            output.write(writerBuffer.get(), chunkSize);
            writtenBytes += static_cast<size_t>(chunkSize);
            writeCursor = writerBuffer.get();
            report(static_cast<float>(min(1.0, writtenBytes / static_cast<double>(totalFileSize))));
        }

        Record next;
        ifstream *source = openFiles[top.fileIndex];
        source->read(reinterpret_cast<char *>(&next), static_cast<streamsize>(RECORD_SIZE));
        if (source->gcount() == static_cast<streamsize>(RECORD_SIZE)) {
            queue.push({next, top.fileIndex});
        }
    }

    if (writeCursor > writerBuffer.get()) {
        streamsize chunkSize = writeCursor - writerBuffer.get();
        output.write(writerBuffer.get(), chunkSize);
        writtenBytes += static_cast<size_t>(chunkSize);
    }
    if (!output) {
        cerr << "[C++] Ошибка записи выходного файла.\n";
        mergeOk = false;
    }
    output.close();
    cleanup();
    report(1.0f);

    auto end_merge = chrono::high_resolution_clock::now();
    chrono::duration<double> mergeTime = end_merge - start_merge;
    chrono::duration<double> totalTime = end_merge - start_total;

    if (!mergeOk) {
        removeOutput();
        return false;
    }

    ostringstream timing;
    timing << "[C++] Этап разбиения: " << splitTime.count() << " с.\n"
           << "[C++] Этап слияния: " << mergeTime.count() << " с.\n"
           << "[C++] Общее время: " << totalTime.count() << " с.\n";
    cout << timing.str();
    if (timingCallback) timingCallback(timing.str().c_str());
    return true;
}

Export void external_sort(
    const char *path,
    int keyIndex,
    bool ascending,
    void (*progressCallback)(float)
)
{
    external_sort_ex(path, keyIndex, ascending, progressCallback, nullptr);
}
