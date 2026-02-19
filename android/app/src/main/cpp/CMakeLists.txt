cmake_minimum_required(VERSION 3.22.1)
project(multiconnect_native LANGUAGES CXX)

add_library(multiconnect_native SHARED
    sync_core_stub.cpp
    bt_router_stub.cpp
)

find_library(log-lib log)

target_compile_features(multiconnect_native PRIVATE cxx_std_17)

target_link_libraries(multiconnect_native PRIVATE ${log-lib})
