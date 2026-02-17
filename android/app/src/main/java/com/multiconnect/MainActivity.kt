package com.multiconnect

import android.app.Activity
import android.os.Bundle
import android.widget.TextView

class MainActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val message = listOf(
            "MultiConnect Android bootstrap",
            NativeStubs.describeSyncCore(),
            NativeStubs.describeBtRouter()
        ).joinToString(separator = "\n")

        setContentView(TextView(this).apply { text = message })
    }
}
