#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "ModelConverter::model-converter" for configuration "Release"
set_property(TARGET ModelConverter::model-converter APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(ModelConverter::model-converter PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/bin/model-converter.exe"
  )

list(APPEND _cmake_import_check_targets ModelConverter::model-converter )
list(APPEND _cmake_import_check_files_for_ModelConverter::model-converter "${_IMPORT_PREFIX}/bin/model-converter.exe" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
