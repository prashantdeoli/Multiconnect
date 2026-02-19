#include <jni.h>

extern "C" JNIEXPORT jstring JNICALL
Java_com_multiconnect_NativeStubs_describeBtRouter(JNIEnv* env, jobject /* this */) {
    return env->NewStringUTF("bt-router stub ready (transport layer placeholder)");
}
