
####### Expanded from @PACKAGE_INIT@ by configure_package_config_file() #######
####### Any changes to this file will be overwritten by the next CMake run ####
####### The input file was SHERPA-MCConfig.cmake.in                            ########

get_filename_component(PACKAGE_PREFIX_DIR "${CMAKE_CURRENT_LIST_DIR}/../../" ABSOLUTE)

macro(set_and_check _var _file)
  set(${_var} "${_file}")
  if(NOT EXISTS "${_file}")
    message(FATAL_ERROR "File or directory ${_file} referenced by variable ${_var} does not exist !")
  endif()
endmacro()

macro(check_required_components _NAME)
  foreach(comp ${${_NAME}_FIND_COMPONENTS})
    if(NOT ${_NAME}_${comp}_FOUND)
      if(${_NAME}_FIND_REQUIRED_${comp})
        set(${_NAME}_FOUND FALSE)
      endif()
    endif()
  endforeach()
endmacro()

####################################################################################

SET(SHERPA-MC_VERSION 3.0.3)
SET(SHERPA-MC_VERSION_MAJOR  3)
SET(SHERPA-MC_VERSION_MINOR  0)
SET(SHERPA-MC_VERSION_PATCH  3)
include(${CMAKE_CURRENT_LIST_DIR}/SHERPATargets.cmake)

if(OFF)
  set(MPIEXEC_EXECUTABLE )
  message(STATUS "AMEGIC: Set MPIEXEC_EXECUTABLE=")
  find_package(MPI REQUIRED)
  message(STATUS "AMEGIC: Found MPIEXEC_EXECUTABLE=${MPIEXEC_EXECUTABLE}")
endif()
macro(amegic_handle_shared_library  mylib)
  if(OFF)
     target_link_libraries(${mylib} PRIVATE MPI::MPI_CXX)
  endif()
  target_link_libraries(${mylib} PRIVATE SHERPA::All)
  target_compile_features(${mylib} PRIVATE cxx_std_11)
endmacro()

