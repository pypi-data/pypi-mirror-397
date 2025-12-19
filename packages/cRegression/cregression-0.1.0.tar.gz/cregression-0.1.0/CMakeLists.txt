cmake_minimum_required(VERSION 3.18)
project(cRegression LANGUAGES CXX)

# Find Python and pybind11
find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)
find_package(pybind11 REQUIRED)

# Build the module from src/cRegression.cpp
pybind11_add_module(cRegression src/cRegression.cpp)

# Fix for MinGW: Statically link all MinGW runtimes (including libwinpthread)
if(MINGW)
    target_link_options(cRegression PRIVATE -static)
endif()

# Install the module into the Python package directory
install(TARGETS cRegression
        LIBRARY DESTINATION cRegression)
