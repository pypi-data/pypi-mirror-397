# SpadeHelpers.cmake
# Utility functions for Spade C++ wrapper

include(FetchContent)
include(${CMAKE_CURRENT_LIST_DIR}/DownloadBinary.cmake)
include(${CMAKE_CURRENT_LIST_DIR}/BuildRust.cmake)

# Main function to find or build Spade FFI library
function(find_or_build_spade_ffi)
    cmake_parse_arguments(
        ARGS
        "FORCE_BUILD;FORCE_DOWNLOAD"
        "VERSION;OUTPUT_DIR"
        ""
        ${ARGN}
    )

    # Set defaults
    if(NOT ARGS_VERSION)
        set(ARGS_VERSION "0.1.1")
    endif()

    if(NOT ARGS_OUTPUT_DIR)
        set(ARGS_OUTPUT_DIR "${CMAKE_CURRENT_BINARY_DIR}/spade_ffi")
    endif()

    # Create output directory
    file(MAKE_DIRECTORY ${ARGS_OUTPUT_DIR})

    # Try strategies in order
    set(SPADE_FFI_FOUND FALSE)
    set(SPADE_FFI_RUNTIME_LIBRARY "" PARENT_SCOPE)

    # Strategy 1: Use existing library if specified
    if(DEFINED SPADE_FFI_LIBRARY AND EXISTS ${SPADE_FFI_LIBRARY})
        message(STATUS "Using provided Spade FFI library: ${SPADE_FFI_LIBRARY}")
        set(SPADE_FFI_FOUND TRUE)
        set(SPADE_FFI_LIBRARY ${SPADE_FFI_LIBRARY} PARENT_SCOPE)
        set(SPADE_FFI_RUNTIME_LIBRARY ${SPADE_FFI_LIBRARY} PARENT_SCOPE)
    endif()

    # Strategy 2: Try to download pre-built binary
    if(NOT SPADE_FFI_FOUND AND NOT ARGS_FORCE_BUILD)
        download_spade_binary(${ARGS_VERSION} ${ARGS_OUTPUT_DIR})
        if(SPADE_BINARY_FOUND)
            set(SPADE_FFI_FOUND TRUE)
            if(SPADE_BINARY_IMPORT_PATH)
                set(SPADE_FFI_LIBRARY ${SPADE_BINARY_IMPORT_PATH} PARENT_SCOPE)
                set(SPADE_FFI_RUNTIME_LIBRARY ${SPADE_BINARY_PATH} PARENT_SCOPE)
            else()
                set(SPADE_FFI_LIBRARY ${SPADE_BINARY_PATH} PARENT_SCOPE)
                set(SPADE_FFI_RUNTIME_LIBRARY ${SPADE_BINARY_PATH} PARENT_SCOPE)
            endif()
        endif()
    endif()

    # Strategy 3: Build from source
    if(NOT SPADE_FFI_FOUND AND NOT ARGS_FORCE_DOWNLOAD)
        # First, fetch Spade source if needed
        if(NOT EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/Cargo.toml")
            message(STATUS "Cargo.toml not found, cannot build from source")
        else()
            build_spade_rust(${CMAKE_CURRENT_SOURCE_DIR} ${ARGS_OUTPUT_DIR})
            if(SPADE_RUST_BUILD_SUCCESS)
                set(SPADE_FFI_FOUND TRUE)
                if(SPADE_RUST_IMPORT_LIBRARY)
                    set(SPADE_FFI_LIBRARY ${SPADE_RUST_IMPORT_LIBRARY} PARENT_SCOPE)
                    if(SPADE_RUST_SHARED_LIBRARY)
                        set(SPADE_FFI_RUNTIME_LIBRARY ${SPADE_RUST_SHARED_LIBRARY} PARENT_SCOPE)
                    endif()
                elseif(SPADE_RUST_SHARED_LIBRARY)
                    set(SPADE_FFI_LIBRARY ${SPADE_RUST_SHARED_LIBRARY} PARENT_SCOPE)
                    set(SPADE_FFI_RUNTIME_LIBRARY ${SPADE_RUST_SHARED_LIBRARY} PARENT_SCOPE)
                elseif(SPADE_RUST_STATIC_LIBRARY)
                    set(SPADE_FFI_LIBRARY ${SPADE_RUST_STATIC_LIBRARY} PARENT_SCOPE)
                    set(SPADE_FFI_RUNTIME_LIBRARY ${SPADE_RUST_STATIC_LIBRARY} PARENT_SCOPE)
                endif()
            endif()
        endif()
    endif()

    # Report result
    if(SPADE_FFI_FOUND)
        message(STATUS "Spade FFI library found/built successfully")
        set(SPADE_FFI_FOUND TRUE PARENT_SCOPE)
    else()
        message(WARNING "Could not find or build Spade FFI library")
        message(STATUS "Options to resolve:")
        message(STATUS "  1. Install Rust toolchain and run: cargo build --release")
        message(STATUS "  2. Download pre-built binary from GitHub releases")
        message(STATUS "  3. Set SPADE_FFI_LIBRARY to point to existing library")
        set(SPADE_FFI_FOUND FALSE PARENT_SCOPE)
    endif()
endfunction()

# Function to fetch Spade source from GitHub
function(fetch_spade_source)
    cmake_parse_arguments(
        ARGS
        ""
        "TAG;OUTPUT_DIR"
        ""
        ${ARGN}
    )

    if(NOT ARGS_TAG)
        set(ARGS_TAG "main")
    endif()

    if(NOT ARGS_OUTPUT_DIR)
        set(ARGS_OUTPUT_DIR "${CMAKE_CURRENT_BINARY_DIR}/spade_source")
    endif()

    message(STATUS "Fetching Spade source from GitHub (tag: ${ARGS_TAG})")

    FetchContent_Declare(
        spade_source
        GIT_REPOSITORY https://github.com/Stoeoef/spade.git
        GIT_TAG        ${ARGS_TAG}
        SOURCE_DIR     ${ARGS_OUTPUT_DIR}
    )

    FetchContent_MakeAvailable(spade_source)

    set(SPADE_SOURCE_DIR ${ARGS_OUTPUT_DIR} PARENT_SCOPE)
endfunction()

# Function to create amalgamated header
function(create_amalgamated_header OUTPUT_FILE)
    set(HEADER_DIR "${CMAKE_CURRENT_SOURCE_DIR}/include")

    file(WRITE ${OUTPUT_FILE} "// Spade C++ Wrapper - Amalgamated Header\n")
    file(APPEND ${OUTPUT_FILE} "// Auto-generated file, do not edit\n")
    file(APPEND ${OUTPUT_FILE} "#ifndef SPADE_HPP\n")
    file(APPEND ${OUTPUT_FILE} "#define SPADE_HPP\n\n")

    # Read and append spade_ffi.h (removing include guards)
    file(READ "${HEADER_DIR}/spade_ffi.h" FFI_CONTENT)
    string(REGEX REPLACE "#ifndef SPADE_FFI_H.*#define SPADE_FFI_H\n" "" FFI_CONTENT "${FFI_CONTENT}")
    string(REGEX REPLACE "#endif.*//.*SPADE_FFI_H" "" FFI_CONTENT "${FFI_CONTENT}")
    file(APPEND ${OUTPUT_FILE} "// ===== spade_ffi.h =====\n")
    file(APPEND ${OUTPUT_FILE} "${FFI_CONTENT}\n")

    # Read and append spade_wrapper.h (removing include guards and include)
    file(READ "${HEADER_DIR}/spade_wrapper.h" WRAPPER_CONTENT)
    string(REGEX REPLACE "#ifndef SPADE_WRAPPER_H.*#define SPADE_WRAPPER_H\n" "" WRAPPER_CONTENT "${WRAPPER_CONTENT}")
    string(REGEX REPLACE "#include \"spade_ffi.h\"\n" "" WRAPPER_CONTENT "${WRAPPER_CONTENT}")
    string(REGEX REPLACE "#endif.*//.*SPADE_WRAPPER_H" "" WRAPPER_CONTENT "${WRAPPER_CONTENT}")
    file(APPEND ${OUTPUT_FILE} "\n// ===== spade_wrapper.h =====\n")
    file(APPEND ${OUTPUT_FILE} "${WRAPPER_CONTENT}\n")

    file(APPEND ${OUTPUT_FILE} "\n#endif // SPADE_HPP\n")

    message(STATUS "Created amalgamated header: ${OUTPUT_FILE}")
endfunction()

# Platform-specific link libraries
function(get_platform_link_libraries OUTPUT_VAR)
    set(LINK_LIBS "")

    if(APPLE)
        list(APPEND LINK_LIBS "-framework CoreFoundation" "-framework Security")
    elseif(UNIX)
        list(APPEND LINK_LIBS pthread dl m)
    elseif(WIN32)
        list(APPEND LINK_LIBS ws2_32 userenv advapi32)
    endif()

    set(${OUTPUT_VAR} ${LINK_LIBS} PARENT_SCOPE)
endfunction()

# Function to setup Spade target
function(setup_spade_target TARGET_NAME)
    cmake_parse_arguments(
        ARGS
        "SHARED;STATIC;INTERFACE"
        "FFI_LIBRARY"
        "ADDITIONAL_LIBS"
        ${ARGN}
    )

    if(ARGS_INTERFACE)
        add_library(${TARGET_NAME} INTERFACE)
        target_include_directories(${TARGET_NAME} INTERFACE
            $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
            $<INSTALL_INTERFACE:include>
        )
        target_link_libraries(${TARGET_NAME} INTERFACE ${ARGS_FFI_LIBRARY})
    else()
        if(ARGS_STATIC)
            add_library(${TARGET_NAME} STATIC ${CMAKE_CURRENT_SOURCE_DIR}/src/spade_wrapper.cpp)
        else()
            add_library(${TARGET_NAME} SHARED ${CMAKE_CURRENT_SOURCE_DIR}/src/spade_wrapper.cpp)
        endif()

        target_include_directories(${TARGET_NAME} PUBLIC
            $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
            $<INSTALL_INTERFACE:include>
        )

        target_link_libraries(${TARGET_NAME} PRIVATE ${ARGS_FFI_LIBRARY})
    endif()

    # Add platform-specific libraries
    get_platform_link_libraries(PLATFORM_LIBS)
    target_link_libraries(${TARGET_NAME} PUBLIC ${PLATFORM_LIBS} ${ARGS_ADDITIONAL_LIBS})

    # Set C++ standard
    target_compile_features(${TARGET_NAME} PUBLIC cxx_std_17)

    # Set properties
    set_target_properties(${TARGET_NAME} PROPERTIES
        CXX_STANDARD 17
        CXX_STANDARD_REQUIRED ON
        CXX_EXTENSIONS OFF
        POSITION_INDEPENDENT_CODE ON
    )
endfunction()
