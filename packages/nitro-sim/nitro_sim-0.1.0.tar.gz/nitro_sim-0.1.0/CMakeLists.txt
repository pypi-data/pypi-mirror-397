cmake_minimum_required(VERSION 3.15)
project(nitro)

# Set C++ standard (allow GNU extensions for RocketSim compatibility)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_EXTENSIONS ON)

# Build RocketSim library
add_subdirectory(RocketSim)

# RocketSim needs to be compiled as position-independent code for shared library
set_target_properties(RocketSim PROPERTIES POSITION_INDEPENDENT_CODE ON)

# Add compiler flags to RocketSim for constexpr compatibility
if(CMAKE_CXX_COMPILER_ID MATCHES "Clang")
    # Clang: suppress invalid constexpr warning
    target_compile_options(RocketSim PRIVATE -Wno-invalid-constexpr)
elseif(CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
    # GCC: Use C++23 mode where constexpr with reinterpret_cast is allowed (P2280R4)
    target_compile_options(RocketSim PRIVATE -std=gnu++23)
endif()

# Find Python and pybind11
find_package(Python COMPONENTS Interpreter Development.Module REQUIRED)
find_package(pybind11 CONFIG REQUIRED)

# Create Python extension module
pybind11_add_module(nitro src/bindings.cpp)
target_link_libraries(nitro PRIVATE RocketSim)

# Include directories - only include RocketSim/src
# Bullet headers are included via relative paths from RocketSim headers
target_include_directories(nitro PRIVATE 
    ${CMAKE_CURRENT_SOURCE_DIR}/RocketSim/src
)

# Install the module and type stubs
install(TARGETS nitro DESTINATION .)
install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/src/nitro.pyi DESTINATION .)
