#----------------------------------------------------------------
# Generated CMake target import file for configuration "Debug".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "ScenarioRunner::glslc" for configuration "Debug"
set_property(TARGET ScenarioRunner::glslc APPEND PROPERTY IMPORTED_CONFIGURATIONS DEBUG)
set_target_properties(ScenarioRunner::glslc PROPERTIES
  IMPORTED_LOCATION_DEBUG "${_IMPORT_PREFIX}/bin/glslc"
  )

list(APPEND _cmake_import_check_targets ScenarioRunner::glslc )
list(APPEND _cmake_import_check_files_for_ScenarioRunner::glslc "${_IMPORT_PREFIX}/bin/glslc" )

# Import target "ScenarioRunner::dds_utils" for configuration "Debug"
set_property(TARGET ScenarioRunner::dds_utils APPEND PROPERTY IMPORTED_CONFIGURATIONS DEBUG)
set_target_properties(ScenarioRunner::dds_utils PROPERTIES
  IMPORTED_LOCATION_DEBUG "${_IMPORT_PREFIX}/bin/dds_utils"
  )

list(APPEND _cmake_import_check_targets ScenarioRunner::dds_utils )
list(APPEND _cmake_import_check_files_for_ScenarioRunner::dds_utils "${_IMPORT_PREFIX}/bin/dds_utils" )

# Import target "ScenarioRunner::scenario-runner" for configuration "Debug"
set_property(TARGET ScenarioRunner::scenario-runner APPEND PROPERTY IMPORTED_CONFIGURATIONS DEBUG)
set_target_properties(ScenarioRunner::scenario-runner PROPERTIES
  IMPORTED_LOCATION_DEBUG "${_IMPORT_PREFIX}/bin/scenario-runner"
  )

list(APPEND _cmake_import_check_targets ScenarioRunner::scenario-runner )
list(APPEND _cmake_import_check_files_for_ScenarioRunner::scenario-runner "${_IMPORT_PREFIX}/bin/scenario-runner" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
