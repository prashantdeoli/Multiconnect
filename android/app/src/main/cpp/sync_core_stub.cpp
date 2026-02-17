#include <jni.h>

extern "C" JNIEXPORT jstring JNICALL
Java_com_multiconnect_NativeStubs_describeSyncCore(JNIEnv* env, jobject /* this */) {
    return env->NewStringUTF("sync-core stub ready (NDK bridge active)");
}
