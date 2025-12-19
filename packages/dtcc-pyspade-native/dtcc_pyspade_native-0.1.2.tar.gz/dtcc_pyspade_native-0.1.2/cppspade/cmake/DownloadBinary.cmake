# DownloadBinary.cmake
# Helper module to download pre-built Spade FFI binaries

include(FetchContent)

function(download_spade_binary VERSION OUTPUT_DIR)
    set(SPADE_BINARY_BASE_URL "https://github.com/dtcc-platform/dtcc-wrapper-spade/releases/download")
    set(SPADE_BINARY_IMPORT_PATH "" PARENT_SCOPE)

    # Detect platform
    if(CMAKE_SYSTEM_NAME STREQUAL "Linux")
        set(PLATFORM_NAME "linux")
        set(LIB_PREFIX "lib")
        set(LIB_SUFFIX ".so")
    elseif(CMAKE_SYSTEM_NAME STREQUAL "Darwin")
        set(PLATFORM_NAME "macos")
        set(LIB_PREFIX "lib")
        set(LIB_SUFFIX ".dylib")
    elseif(CMAKE_SYSTEM_NAME STREQUAL "Windows")
        set(PLATFORM_NAME "windows")
        set(LIB_PREFIX "")
        set(LIB_SUFFIX ".dll")
    else()
        message(STATUS "Unsupported platform for binary download: ${CMAKE_SYSTEM_NAME}")
        return()
    endif()

    # Detect architecture
    if(CMAKE_SYSTEM_PROCESSOR MATCHES "AMD64|x86_64")
        set(ARCH_NAME "x86_64")
    elseif(CMAKE_SYSTEM_PROCESSOR MATCHES "arm64|aarch64")
        set(ARCH_NAME "arm64")
    else()
        message(STATUS "Unsupported architecture for binary download: ${CMAKE_SYSTEM_PROCESSOR}")
        return()
    endif()

    # Construct binary name and URL
    set(BINARY_NAME "${LIB_PREFIX}spade_ffi-${VERSION}-${PLATFORM_NAME}-${ARCH_NAME}${LIB_SUFFIX}")
    set(BINARY_URL "${SPADE_BINARY_BASE_URL}/v${VERSION}/${BINARY_NAME}")
    set(BINARY_PATH "${OUTPUT_DIR}/${LIB_PREFIX}spade_ffi${LIB_SUFFIX}")

    set(IMPORT_NAME "")
    set(IMPORT_URL "")
    set(IMPORT_PATH "")
    if(CMAKE_SYSTEM_NAME STREQUAL "Windows")
        set(IMPORT_NAME "spade_ffi-${VERSION}-${PLATFORM_NAME}-${ARCH_NAME}.dll.lib")
        set(IMPORT_URL "${SPADE_BINARY_BASE_URL}/v${VERSION}/${IMPORT_NAME}")
        set(IMPORT_PATH "${OUTPUT_DIR}/spade_ffi.dll.lib")
    endif()

    macro(_spade_download_import)
        if(IMPORT_URL)
            file(DOWNLOAD
                "${IMPORT_URL}"
                "${IMPORT_PATH}"
                STATUS IMPORT_DOWNLOAD_STATUS
                SHOW_PROGRESS
            )

            if(IMPORT_DOWNLOAD_STATUS)
                list(GET IMPORT_DOWNLOAD_STATUS 0 IMPORT_RESULT)
            else()
                set(IMPORT_RESULT 1)
            endif()

            if(IMPORT_RESULT EQUAL 0 AND EXISTS "${IMPORT_PATH}")
                message(STATUS "Successfully downloaded import library to: ${IMPORT_PATH}")
                set(SPADE_BINARY_IMPORT_PATH "${IMPORT_PATH}" PARENT_SCOPE)
            else()
                message(STATUS "Import library not available for download: ${IMPORT_URL}")
            endif()
        endif()
    endmacro()

    # Check if binary already exists
    if(EXISTS "${BINARY_PATH}")
        message(STATUS "Pre-built binary already exists: ${BINARY_PATH}")
        set(SPADE_BINARY_FOUND TRUE PARENT_SCOPE)
        set(SPADE_BINARY_PATH "${BINARY_PATH}" PARENT_SCOPE)
        _spade_download_import()
        return()
    endif()

    message(STATUS "Attempting to download pre-built binary from: ${BINARY_URL}")

    # Download the binary
    file(DOWNLOAD
        "${BINARY_URL}"
        "${BINARY_PATH}"
        STATUS DOWNLOAD_STATUS
        SHOW_PROGRESS
    )

    list(GET DOWNLOAD_STATUS 0 DOWNLOAD_RESULT)
    list(GET DOWNLOAD_STATUS 1 DOWNLOAD_ERROR)

    if(DOWNLOAD_RESULT EQUAL 0)
        message(STATUS "Successfully downloaded pre-built binary to: ${BINARY_PATH}")

        # Make the binary executable on Unix-like systems
        if(UNIX)
            execute_process(COMMAND chmod +x "${BINARY_PATH}")
        endif()

        set(SPADE_BINARY_FOUND TRUE PARENT_SCOPE)
        set(SPADE_BINARY_PATH "${BINARY_PATH}" PARENT_SCOPE)
        _spade_download_import()
    else()
        message(STATUS "Failed to download pre-built binary: ${DOWNLOAD_ERROR}")
        file(REMOVE "${BINARY_PATH}")
        set(SPADE_BINARY_FOUND FALSE PARENT_SCOPE)
    endif()
endfunction()

# Function to verify binary integrity (optional SHA256 check)
function(verify_spade_binary BINARY_PATH EXPECTED_HASH)
    file(SHA256 "${BINARY_PATH}" ACTUAL_HASH)
    if(NOT "${ACTUAL_HASH}" STREQUAL "${EXPECTED_HASH}")
        message(WARNING "Binary hash mismatch! Expected: ${EXPECTED_HASH}, Got: ${ACTUAL_HASH}")
        return()
    endif()
    message(STATUS "Binary integrity verified")
endfunction()
