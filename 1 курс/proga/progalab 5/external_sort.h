#pragma once

#ifdef _WIN32
#define Export __declspec(dllexport)
#else
#define Export
#endif

extern "C" {
    /* Расширенный вызов: возвращает true при успешной сортировке.
       timingCallback получает готовую строку с временами этапов. */
    Export bool external_sort_ex(
        const char *path,
        int keyIndex,
        bool ascending,
        void (*progressCallback)(float),
        void (*timingCallback)(const char *)
    );

    /* Обратная совместимость: старый вызов без кода ошибки и без таймингов. */
    Export void external_sort(
        const char *path,
        int keyIndex,
        bool ascending,
        void (*progressCallback)(float)
    );
}
