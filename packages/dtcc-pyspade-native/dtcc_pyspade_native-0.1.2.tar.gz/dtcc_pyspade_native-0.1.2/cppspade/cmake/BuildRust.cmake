# BuildRust.cmake
# Helper module to build the Rust FFI library from source

include(ExternalProject)

function(build_spade_rust SOURCE_DIR OUTPUT_DIR)
    set(SPADE_RUST_SHARED_LIBRARY "" PARENT_SCOPE)
    set(SPADE_RUST_IMPORT_LIBRARY "" PARENT_SCOPE)
    set(SPADE_RUST_STATIC_LIBRARY "" PARENT_SCOPE)
    # Check if Rust/Cargo is available
    find_program(CARGO_EXECUTABLE cargo)

    if(NOT CARGO_EXECUTABLE)
        message(STATUS "Cargo not found. Cannot build Rust library from source.")
        set(SPADE_RUST_BUILD_SUCCESS FALSE PARENT_SCOPE)
        return()
    endif()

    message(STATUS "Found Cargo: ${CARGO_EXECUTABLE}")

    # Determine the output library name based on platform
    if(CMAKE_SYSTEM_NAME STREQUAL "Linux")
        set(LIB_NAME "libspade_ffi.so")
        set(STATIC_LIB_NAME "libspade_ffi.a")
        set(IMPORT_LIB_NAME "")
    elseif(CMAKE_SYSTEM_NAME STREQUAL "Darwin")
        set(LIB_NAME "libspade_ffi.dylib")
        set(STATIC_LIB_NAME "libspade_ffi.a")
        set(IMPORT_LIB_NAME "")
    elseif(CMAKE_SYSTEM_NAME STREQUAL "Windows")
        set(LIB_NAME "spade_ffi.dll")
        set(STATIC_LIB_NAME "spade_ffi.lib")
        set(IMPORT_LIB_NAME "spade_ffi.dll.lib")
    endif()

    set(RUST_TARGET_DIR "${SOURCE_DIR}/target")

    # Determine the appropriate Cargo target triple when cross-compiling.
    set(RUST_TARGET_TRIPLE "")
    if(CMAKE_SYSTEM_NAME STREQUAL "Windows")
        if(CMAKE_SIZEOF_VOID_P EQUAL 8)
            set(RUST_TARGET_TRIPLE "x86_64-pc-windows-msvc")
        elseif(CMAKE_SIZEOF_VOID_P EQUAL 4)
            set(RUST_TARGET_TRIPLE "i686-pc-windows-msvc")
        endif()
    elseif(CMAKE_SYSTEM_NAME STREQUAL "Linux")
        if(CMAKE_SYSTEM_PROCESSOR MATCHES "aarch64|arm64")
            set(RUST_TARGET_TRIPLE "aarch64-unknown-linux-gnu")
        endif()
    elseif(CMAKE_SYSTEM_NAME STREQUAL "Darwin")
        if(CMAKE_SYSTEM_PROCESSOR MATCHES "aarch64|arm64")
            set(RUST_TARGET_TRIPLE "aarch64-apple-darwin")
        endif()
    endif()

    set(RUST_OUTPUT_DIR "${RUST_TARGET_DIR}/release")
    set(RUST_BUILD_ARGS build --release --manifest-path ${SOURCE_DIR}/Cargo.toml)

    if(RUST_TARGET_TRIPLE)
        list(APPEND RUST_BUILD_ARGS --target ${RUST_TARGET_TRIPLE})
        set(RUST_OUTPUT_DIR "${RUST_TARGET_DIR}/${RUST_TARGET_TRIPLE}/release")

        # Ensure the requested target triple is installed (idempotent if already present).
        find_program(RUSTUP_EXECUTABLE rustup)
        if(RUSTUP_EXECUTABLE)
            execute_process(
                COMMAND ${RUSTUP_EXECUTABLE} target add ${RUST_TARGET_TRIPLE}
                RESULT_VARIABLE RUSTUP_RESULT
                OUTPUT_QUIET
                ERROR_QUIET
            )
            if(NOT RUSTUP_RESULT EQUAL 0)
                message(WARNING "rustup target add ${RUST_TARGET_TRIPLE} failed; build may not find the correct toolchain")
            endif()
        endif()
    endif()

    # Build the Rust library
    message(STATUS "Building Rust FFI library...")

    execute_process(
        COMMAND ${CARGO_EXECUTABLE} ${RUST_BUILD_ARGS}
        WORKING_DIRECTORY ${SOURCE_DIR}
        RESULT_VARIABLE BUILD_RESULT
        OUTPUT_VARIABLE BUILD_OUTPUT
        ERROR_VARIABLE BUILD_ERROR
    )

    if(BUILD_RESULT EQUAL 0)
        message(STATUS "Successfully built Rust FFI library")

        # Copy the built library to the output directory
        if(EXISTS "${RUST_OUTPUT_DIR}/${LIB_NAME}")
            file(COPY "${RUST_OUTPUT_DIR}/${LIB_NAME}"
                 DESTINATION "${OUTPUT_DIR}")
            set(SPADE_RUST_SHARED_LIBRARY "${OUTPUT_DIR}/${LIB_NAME}" PARENT_SCOPE)
        endif()

        if(STATIC_LIB_NAME AND EXISTS "${RUST_OUTPUT_DIR}/${STATIC_LIB_NAME}")
            file(COPY "${RUST_OUTPUT_DIR}/${STATIC_LIB_NAME}"
                 DESTINATION "${OUTPUT_DIR}")
            set(SPADE_RUST_STATIC_LIBRARY "${OUTPUT_DIR}/${STATIC_LIB_NAME}" PARENT_SCOPE)
        endif()

        if(IMPORT_LIB_NAME AND EXISTS "${RUST_OUTPUT_DIR}/${IMPORT_LIB_NAME}")
            file(COPY "${RUST_OUTPUT_DIR}/${IMPORT_LIB_NAME}"
                 DESTINATION "${OUTPUT_DIR}")
            set(SPADE_RUST_IMPORT_LIBRARY "${OUTPUT_DIR}/${IMPORT_LIB_NAME}" PARENT_SCOPE)
        endif()

        set(SPADE_RUST_BUILD_SUCCESS TRUE PARENT_SCOPE)
    else()
        message(STATUS "Failed to build Rust FFI library: ${BUILD_ERROR}")
        set(SPADE_RUST_BUILD_SUCCESS FALSE PARENT_SCOPE)
    endif()
endfunction()

# Alternative: Use ExternalProject_Add for more complex scenarios
function(add_spade_rust_external PROJECT_NAME SOURCE_DIR BINARY_DIR)
    # Check for Cargo
    find_program(CARGO_EXECUTABLE cargo)
    if(NOT CARGO_EXECUTABLE)
        message(FATAL_ERROR "Cargo is required but not found")
    endif()

    # Determine build type
    if(CMAKE_BUILD_TYPE STREQUAL "Debug")
        set(RUST_BUILD_TYPE "")
    else()
        set(RUST_BUILD_TYPE "--release")
    endif()

    ExternalProject_Add(${PROJECT_NAME}
        SOURCE_DIR ${SOURCE_DIR}
        BINARY_DIR ${BINARY_DIR}
        CONFIGURE_COMMAND ""
        BUILD_COMMAND ${CARGO_EXECUTABLE} build ${RUST_BUILD_TYPE} --manifest-path ${SOURCE_DIR}/Cargo.toml
        BUILD_IN_SOURCE 1
        INSTALL_COMMAND ""
        BUILD_BYPRODUCTS
            ${SOURCE_DIR}/target/release/libspade_ffi.so
            ${SOURCE_DIR}/target/release/libspade_ffi.dylib
            ${SOURCE_DIR}/target/release/libspade_ffi.a
            ${SOURCE_DIR}/target/release/spade_ffi.dll
            ${SOURCE_DIR}/target/release/spade_ffi.lib
    )
endfunction()

# Function to check Rust toolchain version
function(check_rust_version MIN_VERSION)
    execute_process(
        COMMAND rustc --version
        OUTPUT_VARIABLE RUST_VERSION_OUTPUT
        OUTPUT_STRIP_TRAILING_WHITESPACE
    )

    if(RUST_VERSION_OUTPUT MATCHES "rustc ([0-9]+\\.[0-9]+\\.[0-9]+)")
        set(RUST_VERSION ${CMAKE_MATCH_1})
        if(RUST_VERSION VERSION_LESS MIN_VERSION)
            message(WARNING "Rust version ${RUST_VERSION} is older than required ${MIN_VERSION}")
            set(RUST_VERSION_OK FALSE PARENT_SCOPE)
        else()
            message(STATUS "Rust version ${RUST_VERSION} meets requirements")
            set(RUST_VERSION_OK TRUE PARENT_SCOPE)
        endif()
    else()
        message(WARNING "Could not determine Rust version")
        set(RUST_VERSION_OK FALSE PARENT_SCOPE)
    endif()
endfunction()
