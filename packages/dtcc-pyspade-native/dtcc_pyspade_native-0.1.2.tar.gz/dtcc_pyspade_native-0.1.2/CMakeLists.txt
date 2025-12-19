cmake_minimum_required(VERSION 3.15)
project(pyspade_native VERSION 0.1.1 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Build the C++ Spade wrapper library
set(SPADE_BUILD_EXAMPLES OFF CACHE BOOL "")
set(SPADE_BUILD_PYTHON OFF CACHE BOOL "")
set(SPADE_AUTO_BUILD ON CACHE BOOL "")
set(SPADE_AUTO_DOWNLOAD ON CACHE BOOL "")

# Add the cppspade library
add_subdirectory(cppspade)

# Determine installation directory (managed by scikit-build-core)
if(DEFINED SKBUILD_PLATLIB_DIR)
    set(INSTALL_PREFIX "${SKBUILD_PLATLIB_DIR}/pyspade_native")
else()
    set(INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")
endif()

# On Windows, enable automatic symbol export so an import library is generated
if(WIN32)
    set_target_properties(spade_wrapper PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()

# Install the C++ library and headers
# Note: RUNTIME (DLLs) goes to lib/ so all library files are in one place
install(
    TARGETS spade_wrapper
    COMPONENT spade_cpp
    LIBRARY DESTINATION "${INSTALL_PREFIX}/lib"
    ARCHIVE DESTINATION "${INSTALL_PREFIX}/lib"
    RUNTIME DESTINATION "${INSTALL_PREFIX}/lib"
)

# Install headers
install(
    DIRECTORY cppspade/include/
    COMPONENT spade_cpp
    DESTINATION "${INSTALL_PREFIX}/include"
    FILES_MATCHING PATTERN "*.h"
)

# Install the Rust FFI library
if(TARGET spade_wrapper)
    # Find and install the FFI library
    set(FFI_LIBS "")
    if(DEFINED SPADE_FFI_LIBRARY AND EXISTS "${SPADE_FFI_LIBRARY}")
        list(APPEND FFI_LIBS "${SPADE_FFI_LIBRARY}")
    endif()
    if(DEFINED SPADE_FFI_RUNTIME_LIBRARY AND EXISTS "${SPADE_FFI_RUNTIME_LIBRARY}")
        list(APPEND FFI_LIBS "${SPADE_FFI_RUNTIME_LIBRARY}")
    endif()

    set(FFI_SEARCH_PATHS
        "${CMAKE_CURRENT_BINARY_DIR}/cppspade/lib"
        "${CMAKE_CURRENT_SOURCE_DIR}/cppspade/target/release"
        "${CMAKE_CURRENT_BINARY_DIR}/cppspade/target/release"
    )

    if(NOT FFI_LIBS)
        foreach(SEARCH_PATH ${FFI_SEARCH_PATHS})
            file(GLOB FFI_LIB_CANDIDATES
                "${SEARCH_PATH}/libspade_ffi.so"
                "${SEARCH_PATH}/libspade_ffi.dylib"
                "${SEARCH_PATH}/libspade_ffi.a"
                "${SEARCH_PATH}/spade_ffi.dll"
                "${SEARCH_PATH}/spade_ffi.lib"
                "${SEARCH_PATH}/spade_ffi.dll.lib"
            )
            if(FFI_LIB_CANDIDATES)
                list(APPEND FFI_LIBS ${FFI_LIB_CANDIDATES})
                break()
            endif()
        endforeach()
    endif()

    if(FFI_LIBS)
        list(REMOVE_DUPLICATES FFI_LIBS)
    endif()

    if(FFI_LIBS AND APPLE)
        foreach(FFI_LIB ${FFI_LIBS})
            get_filename_component(FFI_NAME "${FFI_LIB}" NAME)
            if(FFI_NAME MATCHES "\\.dylib$")
                execute_process(
                    COMMAND install_name_tool -id "@rpath/${FFI_NAME}" "${FFI_LIB}"
                    RESULT_VARIABLE INSTALL_NAME_RESULT
                    ERROR_VARIABLE INSTALL_NAME_ERROR
                )
                if(NOT INSTALL_NAME_RESULT EQUAL 0)
                    message(WARNING "install_name_tool failed for ${FFI_LIB}: ${INSTALL_NAME_ERROR}")
                endif()
            endif()
        endforeach()
    endif()

    if(FFI_LIBS)
        install(
            FILES ${FFI_LIBS}
            COMPONENT spade_cpp
            DESTINATION "${INSTALL_PREFIX}/lib"
        )
    endif()
endif()

# Create and install CMake package config
include(CMakePackageConfigHelpers)

configure_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/cmake/pyspade_native-config.cmake.in"
    "${CMAKE_CURRENT_BINARY_DIR}/pyspade_native-config.cmake"
    @ONLY
)

write_basic_package_version_file(
    "${CMAKE_CURRENT_BINARY_DIR}/pyspade_native-config-version.cmake"
    VERSION ${PROJECT_VERSION}
    COMPATIBILITY SameMajorVersion
)

install(
    FILES
        "${CMAKE_CURRENT_BINARY_DIR}/pyspade_native-config.cmake"
        "${CMAKE_CURRENT_BINARY_DIR}/pyspade_native-config-version.cmake"
    COMPONENT spade_cpp
    DESTINATION "${INSTALL_PREFIX}/cmake"
)
