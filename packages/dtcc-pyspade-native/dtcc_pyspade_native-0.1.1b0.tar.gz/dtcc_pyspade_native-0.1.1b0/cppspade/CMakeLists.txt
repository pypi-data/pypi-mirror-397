cmake_minimum_required(VERSION 3.15)
project(SpadeCppWrapper VERSION 0.1.1 LANGUAGES CXX)

# Options
option(SPADE_BUILD_EXAMPLES "Build example programs" ON)
option(SPADE_BUILD_SHARED "Build shared library" ON)
option(SPADE_BUILD_STATIC "Build static library" OFF)
option(SPADE_AUTO_DOWNLOAD "Automatically download pre-built binaries" ON)
option(SPADE_AUTO_BUILD "Automatically build from source if needed" ON)
option(SPADE_CREATE_AMALGAMATION "Create single-header amalgamation" OFF)
option(SPADE_FORCE_BUILD "Force building from source even if binaries available" OFF)
option(SPADE_FORCE_DOWNLOAD "Force downloading binaries even if Rust available" OFF)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Add our CMake modules to the path
list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/cmake)

# Debug: Check if cmake directory exists
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/cmake")
    message(STATUS "Found cmake directory at: ${CMAKE_CURRENT_SOURCE_DIR}/cmake")
    file(GLOB CMAKE_HELPERS "${CMAKE_CURRENT_SOURCE_DIR}/cmake/*.cmake")
    message(STATUS "Found cmake files: ${CMAKE_HELPERS}")
else()
    message(WARNING "cmake directory not found at: ${CMAKE_CURRENT_SOURCE_DIR}/cmake")
endif()

# Set default build type if not specified
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

# Include our CMake modules
include(SpadeHelpers)

# Create output directories
set(SPADE_OUTPUT_DIR "${CMAKE_CURRENT_BINARY_DIR}/lib")
file(MAKE_DIRECTORY ${SPADE_OUTPUT_DIR})

# =============================================================================
# Find or Build Spade FFI Library
# =============================================================================

message(STATUS "")
message(STATUS "=== Configuring Spade C++ Wrapper ===")
message(STATUS "Version: ${PROJECT_VERSION}")
message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "Platform: ${CMAKE_SYSTEM_NAME}")
message(STATUS "Architecture: ${CMAKE_SYSTEM_PROCESSOR}")
message(STATUS "Pointer size: ${CMAKE_SIZEOF_VOID_P}")
message(STATUS "")

# Three-tier strategy to get the Spade FFI library
set(SPADE_FFI_FOUND FALSE)
set(SPADE_FFI_RUNTIME_LIBRARY "")

# Tier 1: Check if user provided a pre-built library path
if(DEFINED SPADE_FFI_LIBRARY_PATH AND EXISTS ${SPADE_FFI_LIBRARY_PATH})
    message(STATUS "Using user-provided Spade FFI library: ${SPADE_FFI_LIBRARY_PATH}")
    set(SPADE_FFI_LIBRARY ${SPADE_FFI_LIBRARY_PATH})
    set(SPADE_FFI_RUNTIME_LIBRARY ${SPADE_FFI_LIBRARY_PATH})
    set(SPADE_FFI_FOUND TRUE)
endif()

# Tier 2: Try to download pre-built binary (if auto-download enabled)
if(NOT SPADE_FFI_FOUND AND SPADE_AUTO_DOWNLOAD AND NOT SPADE_FORCE_BUILD)
    message(STATUS "Attempting to download pre-built Spade FFI binary...")
    download_spade_binary(${PROJECT_VERSION} ${SPADE_OUTPUT_DIR})
    if(SPADE_BINARY_FOUND)
        if(DEFINED SPADE_BINARY_IMPORT_PATH AND EXISTS "${SPADE_BINARY_IMPORT_PATH}")
            set(SPADE_FFI_LIBRARY ${SPADE_BINARY_IMPORT_PATH})
            set(SPADE_FFI_RUNTIME_LIBRARY ${SPADE_BINARY_PATH})
        else()
            set(SPADE_FFI_LIBRARY ${SPADE_BINARY_PATH})
            set(SPADE_FFI_RUNTIME_LIBRARY ${SPADE_BINARY_PATH})
        endif()
        set(SPADE_FFI_FOUND TRUE)
        message(STATUS "Successfully downloaded pre-built binary")
    else()
        message(STATUS "Pre-built binary not available for this platform/version")
    endif()
endif()

# Tier 3: Build from source (if auto-build enabled)
if(NOT SPADE_FFI_FOUND AND SPADE_AUTO_BUILD AND NOT SPADE_FORCE_DOWNLOAD)
    message(STATUS "Attempting to build Spade FFI from source...")

    # Check if we have the Rust source
    if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/Cargo.toml")
        build_spade_rust(${CMAKE_CURRENT_SOURCE_DIR} ${SPADE_OUTPUT_DIR})

        if(SPADE_RUST_BUILD_SUCCESS)
            if(SPADE_RUST_IMPORT_LIBRARY)
                set(SPADE_FFI_LIBRARY ${SPADE_RUST_IMPORT_LIBRARY})
                if(SPADE_RUST_SHARED_LIBRARY)
                    set(SPADE_FFI_RUNTIME_LIBRARY ${SPADE_RUST_SHARED_LIBRARY})
                endif()
            elseif(SPADE_RUST_SHARED_LIBRARY)
                set(SPADE_FFI_LIBRARY ${SPADE_RUST_SHARED_LIBRARY})
                set(SPADE_FFI_RUNTIME_LIBRARY ${SPADE_RUST_SHARED_LIBRARY})
            elseif(SPADE_RUST_STATIC_LIBRARY)
                set(SPADE_FFI_LIBRARY ${SPADE_RUST_STATIC_LIBRARY})
                set(SPADE_FFI_RUNTIME_LIBRARY ${SPADE_RUST_STATIC_LIBRARY})
            endif()
            set(SPADE_FFI_FOUND TRUE)
            message(STATUS "Successfully built Spade FFI from source")
        else()
            message(STATUS "Failed to build from source")
        endif()
    else()
        message(STATUS "Cargo.toml not found, cannot build from source")
    endif()
endif()

# Check if we found the library
if(NOT SPADE_FFI_FOUND)
    message(FATAL_ERROR
        "\nCould not find or build Spade FFI library!\n"
        "Options to resolve:\n"
        "  1. Install Rust (https://rustup.rs/) and re-run CMake\n"
        "  2. Download pre-built binary from GitHub releases\n"
        "  3. Build manually: cargo build --release\n"
        "  4. Set -DSPADE_FFI_LIBRARY_PATH=/path/to/libspade_ffi.so\n"
    )
endif()

message(STATUS "Using Spade FFI library: ${SPADE_FFI_LIBRARY}")
if(SPADE_FFI_RUNTIME_LIBRARY AND NOT SPADE_FFI_RUNTIME_LIBRARY STREQUAL "${SPADE_FFI_LIBRARY}")
    message(STATUS "Runtime Spade FFI binary: ${SPADE_FFI_RUNTIME_LIBRARY}")
endif()

if(APPLE AND SPADE_FFI_LIBRARY AND EXISTS "${SPADE_FFI_LIBRARY}")
    get_filename_component(_spade_ffi_name "${SPADE_FFI_LIBRARY}" NAME)
    if(_spade_ffi_name MATCHES "\\.dylib$")
        execute_process(
            COMMAND install_name_tool -id "@rpath/${_spade_ffi_name}" "${SPADE_FFI_LIBRARY}"
            RESULT_VARIABLE _ffi_install_name_result
            ERROR_VARIABLE _ffi_install_name_error
        )
        if(NOT _ffi_install_name_result EQUAL 0)
            message(WARNING "install_name_tool failed for ${SPADE_FFI_LIBRARY}: ${_ffi_install_name_error}")
        endif()
    endif()
endif()

# Share the resolved FFI path with parent scopes so installation logic can reuse it.
set(SPADE_FFI_LIBRARY "${SPADE_FFI_LIBRARY}" CACHE FILEPATH "Path to Spade FFI shared library" FORCE)
if(SPADE_FFI_RUNTIME_LIBRARY)
    set(SPADE_FFI_RUNTIME_LIBRARY "${SPADE_FFI_RUNTIME_LIBRARY}" CACHE FILEPATH "Path to Spade FFI runtime binary" FORCE)
endif()

# =============================================================================
# Create C++ Wrapper Library
# =============================================================================

# Source files
set(SPADE_SOURCES
    ${CMAKE_CURRENT_SOURCE_DIR}/src/spade_wrapper.cpp
)

# Create library target(s)
if(SPADE_BUILD_SHARED)
    add_library(spade_wrapper SHARED ${SPADE_SOURCES})
    set(SPADE_PRIMARY_TARGET spade_wrapper)
endif()

if(SPADE_BUILD_STATIC)
    add_library(spade_wrapper_static STATIC ${SPADE_SOURCES})
    if(NOT SPADE_BUILD_SHARED)
        set(SPADE_PRIMARY_TARGET spade_wrapper_static)
    endif()
endif()

# Configure the primary target
if(DEFINED SPADE_PRIMARY_TARGET)
    target_include_directories(${SPADE_PRIMARY_TARGET} PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
    )

    target_link_libraries(${SPADE_PRIMARY_TARGET} PRIVATE ${SPADE_FFI_LIBRARY})

    # Platform-specific linking
    get_platform_link_libraries(PLATFORM_LIBS)
    target_link_libraries(${SPADE_PRIMARY_TARGET} PUBLIC ${PLATFORM_LIBS})

    # Set properties
    set(_spade_install_rpath "$ORIGIN")
    if(APPLE)
        set(_spade_install_rpath "@loader_path")
        set(_spade_install_name_dir "@rpath")
    endif()

    set_target_properties(${SPADE_PRIMARY_TARGET} PROPERTIES
        CXX_STANDARD 17
        CXX_STANDARD_REQUIRED ON
        CXX_EXTENSIONS OFF
        POSITION_INDEPENDENT_CODE ON
        VERSION ${PROJECT_VERSION}
        SOVERSION ${PROJECT_VERSION_MAJOR}
        INSTALL_RPATH "${_spade_install_rpath}"
        BUILD_WITH_INSTALL_RPATH ON
    )

    if(APPLE)
        set_target_properties(${SPADE_PRIMARY_TARGET} PROPERTIES
            INSTALL_NAME_DIR "${_spade_install_name_dir}"
        )
    endif()

    # Export compile commands for IDEs
    set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
endif()

# Configure static library if built
if(TARGET spade_wrapper_static)
    target_include_directories(spade_wrapper_static PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
    )

    target_link_libraries(spade_wrapper_static PRIVATE ${SPADE_FFI_LIBRARY})
    get_platform_link_libraries(PLATFORM_LIBS)
    target_link_libraries(spade_wrapper_static PUBLIC ${PLATFORM_LIBS})

    set_target_properties(spade_wrapper_static PROPERTIES
        CXX_STANDARD 17
        CXX_STANDARD_REQUIRED ON
        CXX_EXTENSIONS OFF
        POSITION_INDEPENDENT_CODE ON
    )
endif()

# =============================================================================
# Create Amalgamated Header (Optional)
# =============================================================================

if(SPADE_CREATE_AMALGAMATION)
    set(AMALGAMATED_HEADER "${CMAKE_CURRENT_BINARY_DIR}/spade.hpp")
    create_amalgamated_header(${AMALGAMATED_HEADER})

    # Install the amalgamated header
    install(FILES ${AMALGAMATED_HEADER}
        DESTINATION include
    )
endif()

# =============================================================================
# Build Examples
# =============================================================================

if(SPADE_BUILD_EXAMPLES)
    add_subdirectory(examples)
endif()

# =============================================================================
# Installation Rules
# =============================================================================

include(GNUInstallDirs)

# Install libraries
if(TARGET spade_wrapper)
    install(TARGETS spade_wrapper
        EXPORT SpadeTargets
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
        INCLUDES DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
    )
endif()

if(TARGET spade_wrapper_static)
    install(TARGETS spade_wrapper_static
        EXPORT SpadeTargets
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    )
endif()

# Install headers
install(DIRECTORY include/
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
    FILES_MATCHING PATTERN "*.h"
)

# Install Rust FFI library
install(FILES ${SPADE_FFI_LIBRARY}
    DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

# =============================================================================
# Export Configuration
# =============================================================================

# Create package configuration files
include(CMakePackageConfigHelpers)

# Generate the config file
configure_package_config_file(
    ${CMAKE_CURRENT_SOURCE_DIR}/cmake/SpadeConfig.cmake.in
    ${CMAKE_CURRENT_BINARY_DIR}/SpadeConfig.cmake
    INSTALL_DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/Spade
)

# Generate the version file
write_basic_package_version_file(
    ${CMAKE_CURRENT_BINARY_DIR}/SpadeConfigVersion.cmake
    VERSION ${PROJECT_VERSION}
    COMPATIBILITY SameMajorVersion
)

# Install the configuration files
install(FILES
    ${CMAKE_CURRENT_BINARY_DIR}/SpadeConfig.cmake
    ${CMAKE_CURRENT_BINARY_DIR}/SpadeConfigVersion.cmake
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/Spade
)

# Export targets
install(EXPORT SpadeTargets
    FILE SpadeTargets.cmake
    NAMESPACE Spade::
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/Spade
)

# =============================================================================
# Status Summary
# =============================================================================

message(STATUS "")
message(STATUS "=== Configuration Summary ===")
message(STATUS "Build shared library: ${SPADE_BUILD_SHARED}")
message(STATUS "Build static library: ${SPADE_BUILD_STATIC}")
message(STATUS "Build examples: ${SPADE_BUILD_EXAMPLES}")
message(STATUS "Create amalgamation: ${SPADE_CREATE_AMALGAMATION}")
message(STATUS "FFI library: ${SPADE_FFI_LIBRARY}")
message(STATUS "")
message(STATUS "To build: cmake --build ${CMAKE_BINARY_DIR}")
message(STATUS "To install: cmake --install ${CMAKE_BINARY_DIR}")
message(STATUS "")
