cmake_minimum_required(VERSION 3.16)
project(multiconnect_native LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_library(multiconnect_core
    src/sync_math.cpp
    src/beep_generator.cpp
    src/master_ring_buffer.cpp
    src/sync_engine.cpp
    src/sync_engine_c_api.cpp
)

target_include_directories(multiconnect_core PUBLIC include)

enable_testing()

add_executable(poc_cli src/poc_cli.cpp)
target_link_libraries(poc_cli PRIVATE multiconnect_core)

add_executable(test_sync_math tests/test_sync_math.cpp)
target_link_libraries(test_sync_math PRIVATE multiconnect_core)
add_test(NAME test_sync_math COMMAND test_sync_math)

add_executable(test_ring_buffer tests/test_ring_buffer.cpp)
target_link_libraries(test_ring_buffer PRIVATE multiconnect_core)
add_test(NAME test_ring_buffer COMMAND test_ring_buffer)


add_executable(test_sync_engine tests/test_sync_engine.cpp)
target_link_libraries(test_sync_engine PRIVATE multiconnect_core)
add_test(NAME test_sync_engine COMMAND test_sync_engine)

add_executable(test_sync_engine_c_api tests/test_sync_engine_c_api.cpp)
target_link_libraries(test_sync_engine_c_api PRIVATE multiconnect_core)
add_test(NAME test_sync_engine_c_api COMMAND test_sync_engine_c_api)
