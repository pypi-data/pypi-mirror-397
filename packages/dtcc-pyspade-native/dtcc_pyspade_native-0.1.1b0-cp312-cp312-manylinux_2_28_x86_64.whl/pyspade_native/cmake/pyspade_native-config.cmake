# pyspade_native CMake configuration
#
# This file allows CMake projects to find the Spade C++ library
# installed via pip install dtcc-pyspade-native.
#
# Usage in your CMakeLists.txt:
#   find_package(pyspade_native REQUIRED)
#   target_link_libraries(your_target PRIVATE pyspade_native::spade_wrapper)



# Get the directory where this config file is located
get_filename_component(PYSPADE_NATIVE_CMAKE_DIR "${CMAKE_CURRENT_LIST_FILE}" PATH)

# Calculate the package root directory
get_filename_component(PYSPADE_NATIVE_ROOT "${PYSPADE_NATIVE_CMAKE_DIR}/.." ABSOLUTE)

# Set include directories
set(PYSPADE_NATIVE_INCLUDE_DIR "${PYSPADE_NATIVE_ROOT}/include")
set(PYSPADE_NATIVE_LIBRARY_DIR "${PYSPADE_NATIVE_ROOT}/lib")

# Verify installation
if(NOT EXISTS "${PYSPADE_NATIVE_INCLUDE_DIR}")
    message(FATAL_ERROR "dtcc-pyspade-native include directory not found: ${PYSPADE_NATIVE_INCLUDE_DIR}")
endif()

# Find the Spade wrapper library
find_library(PYSPADE_NATIVE_LIBRARY
    NAMES spade_wrapper libspade_wrapper
    PATHS "${PYSPADE_NATIVE_LIBRARY_DIR}"
    NO_DEFAULT_PATH
)

if(NOT PYSPADE_NATIVE_LIBRARY)
    message(FATAL_ERROR "dtcc-pyspade-native library not found in: ${PYSPADE_NATIVE_LIBRARY_DIR}")
endif()

# Find the FFI library
find_library(PYSPADE_NATIVE_FFI_LIBRARY
    NAMES spade_ffi libspade_ffi
    PATHS "${PYSPADE_NATIVE_LIBRARY_DIR}"
    NO_DEFAULT_PATH
)

# Create imported target for FFI library
if(PYSPADE_NATIVE_FFI_LIBRARY AND NOT TARGET pyspade_native::spade_ffi)
    add_library(pyspade_native::spade_ffi SHARED IMPORTED)
    if(WIN32)
        # On Windows, find_library returns the import lib (.dll.lib)
        # We need to also specify the DLL location
        find_file(PYSPADE_NATIVE_FFI_DLL
            NAMES spade_ffi.dll
            PATHS "${PYSPADE_NATIVE_LIBRARY_DIR}"
            NO_DEFAULT_PATH
        )
        set_target_properties(pyspade_native::spade_ffi PROPERTIES
            IMPORTED_IMPLIB "${PYSPADE_NATIVE_FFI_LIBRARY}"
            IMPORTED_LOCATION "${PYSPADE_NATIVE_FFI_DLL}"
        )
    else()
        set_target_properties(pyspade_native::spade_ffi PROPERTIES
            IMPORTED_LOCATION "${PYSPADE_NATIVE_FFI_LIBRARY}"
        )
    endif()
endif()

# Create imported target for wrapper library
if(NOT TARGET pyspade_native::spade_wrapper)
    add_library(pyspade_native::spade_wrapper SHARED IMPORTED)

    if(WIN32)
        # On Windows, find_library returns the import lib (.lib)
        # We need to also specify the DLL location
        find_file(PYSPADE_NATIVE_DLL
            NAMES spade_wrapper.dll
            PATHS "${PYSPADE_NATIVE_LIBRARY_DIR}"
            NO_DEFAULT_PATH
        )
        set_target_properties(pyspade_native::spade_wrapper PROPERTIES
            IMPORTED_IMPLIB "${PYSPADE_NATIVE_LIBRARY}"
            IMPORTED_LOCATION "${PYSPADE_NATIVE_DLL}"
            INTERFACE_INCLUDE_DIRECTORIES "${PYSPADE_NATIVE_INCLUDE_DIR}"
        )
    else()
        set_target_properties(pyspade_native::spade_wrapper PROPERTIES
            IMPORTED_LOCATION "${PYSPADE_NATIVE_LIBRARY}"
            INTERFACE_INCLUDE_DIRECTORIES "${PYSPADE_NATIVE_INCLUDE_DIR}"
        )
    endif()

    # Build link libraries list
    set(_SPADE_LINK_LIBS "")

    # Add FFI library
    if(TARGET pyspade_native::spade_ffi)
        list(APPEND _SPADE_LINK_LIBS pyspade_native::spade_ffi)
    endif()

    # Add platform-specific libraries
    if(APPLE)
        list(APPEND _SPADE_LINK_LIBS "-framework CoreFoundation" "-framework Security")
    elseif(WIN32)
        list(APPEND _SPADE_LINK_LIBS ws2_32 userenv advapi32)
    elseif(UNIX)
        list(APPEND _SPADE_LINK_LIBS pthread dl m)
    endif()

    # Set interface link libraries
    if(_SPADE_LINK_LIBS)
        set_target_properties(pyspade_native::spade_wrapper PROPERTIES
            INTERFACE_LINK_LIBRARIES "${_SPADE_LINK_LIBS}"
        )
    endif()
endif()

# Set output variables
set(PYSPADE_NATIVE_LIBRARIES ${PYSPADE_NATIVE_LIBRARY})
set(PYSPADE_NATIVE_INCLUDE_DIRS ${PYSPADE_NATIVE_INCLUDE_DIR})
set(PYSPADE_NATIVE_FOUND TRUE)

check_required_components(pyspade_native)
