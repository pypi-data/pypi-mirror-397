#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "MultiSenseWire" for configuration "Release"
set_property(TARGET MultiSenseWire APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(MultiSenseWire PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libMultiSenseWire.a"
  )

list(APPEND _cmake_import_check_targets MultiSenseWire )
list(APPEND _cmake_import_check_files_for_MultiSenseWire "${_IMPORT_PREFIX}/lib/libMultiSenseWire.a" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
