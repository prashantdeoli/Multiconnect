#pragma once

// Unified logging macros for native code.
// - On Android, logs route to Logcat.
// - Off Android (host/unit tests), logs route to stderr.

#if defined(__ANDROID__)
#include <android/log.h>
#define MC_LOG_TAG "MultiConnectNative"
#define MC_LOGI(...) __android_log_print(ANDROID_LOG_INFO, MC_LOG_TAG, __VA_ARGS__)
#define MC_LOGW(...) __android_log_print(ANDROID_LOG_WARN, MC_LOG_TAG, __VA_ARGS__)
#define MC_LOGE(...) __android_log_print(ANDROID_LOG_ERROR, MC_LOG_TAG, __VA_ARGS__)
#else
#include <cstdio>
#define MC_LOGI(...)                            \
    do {                                        \
        std::fprintf(stderr, "[I] ");          \
        std::fprintf(stderr, __VA_ARGS__);      \
        std::fprintf(stderr, "\n");           \
    } while (0)
#define MC_LOGW(...)                            \
    do {                                        \
        std::fprintf(stderr, "[W] ");          \
        std::fprintf(stderr, __VA_ARGS__);      \
        std::fprintf(stderr, "\n");           \
    } while (0)
#define MC_LOGE(...)                            \
    do {                                        \
        std::fprintf(stderr, "[E] ");          \
        std::fprintf(stderr, __VA_ARGS__);      \
        std::fprintf(stderr, "\n");           \
    } while (0)
#endif
