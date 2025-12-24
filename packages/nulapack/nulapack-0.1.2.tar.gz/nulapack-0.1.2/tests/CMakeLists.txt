get_property(FORTRAN_SOURCES GLOBAL PROPERTY FORTRAN_SOURCES)
get_property(HEADER_FILES GLOBAL PROPERTY HEADER_FILES)

add_library(fortran_objs OBJECT ${FORTRAN_SOURCES})

add_executable(test_gauss_seidel_c test_gauss_seidel.c $<TARGET_OBJECTS:fortran_objs>)
target_include_directories(test_gauss_seidel_c PRIVATE ${CMAKE_SOURCE_DIR}/interface)

add_executable(test_gauss_seidel_cxx test_gauss_seidel.cpp $<TARGET_OBJECTS:fortran_objs>)
target_include_directories(test_gauss_seidel_cxx PRIVATE ${CMAKE_SOURCE_DIR}/interface)
target_link_libraries(test_gauss_seidel_cxx PRIVATE m Catch2::Catch2WithMain)

enable_testing()
