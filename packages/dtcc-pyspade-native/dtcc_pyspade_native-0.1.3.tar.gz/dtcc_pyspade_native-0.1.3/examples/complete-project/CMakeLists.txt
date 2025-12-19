cmake_minimum_required(VERSION 3.15)
project(example_spade_usage)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find Python and pybind11
find_package(Python REQUIRED COMPONENTS Interpreter Development)
find_package(pybind11 CONFIG REQUIRED)

# Find dtcc-pyspade-native
message(STATUS "Looking for dtcc-pyspade-native...")
execute_process(
    COMMAND ${Python_EXECUTABLE} -c "import pyspade_native; print(pyspade_native.get_cmake_dir())"
    OUTPUT_VARIABLE PYSPADE_CMAKE_DIR
    OUTPUT_STRIP_TRAILING_WHITESPACE
    RESULT_VARIABLE PYSPADE_RESULT
)

if(NOT PYSPADE_RESULT EQUAL 0)
    message(FATAL_ERROR "dtcc-pyspade-native not found. Install it with: pip install dtcc-pyspade-native")
endif()

find_package(pyspade_native REQUIRED PATHS ${PYSPADE_CMAKE_DIR} NO_DEFAULT_PATH)
message(STATUS "Found dtcc-pyspade-native: ${PYSPADE_CMAKE_DIR}")

# Create the Python extension module
pybind11_add_module(_geometry_core
    src/cpp/geometry_binding.cpp
)

# Link with dtcc-pyspade-native
target_link_libraries(_geometry_core PRIVATE pyspade_native::spade_wrapper)

# Install the module
install(TARGETS _geometry_core DESTINATION ${SKBUILD_PLATLIB_DIR}/example_pkg)