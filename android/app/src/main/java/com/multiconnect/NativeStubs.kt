package com.multiconnect

object NativeStubs {
    init {
        System.loadLibrary("multiconnect_native")
    }

    external fun describeSyncCore(): String
    external fun describeBtRouter(): String
}
