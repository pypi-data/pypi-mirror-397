#----------------------------------------------------------------
# Generated CMake target import file for configuration "Debug".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "VGF::vgf" for configuration "Debug"
set_property(TARGET VGF::vgf APPEND PROPERTY IMPORTED_CONFIGURATIONS DEBUG)
set_target_properties(VGF::vgf PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_DEBUG "CXX"
  IMPORTED_LOCATION_DEBUG "${_IMPORT_PREFIX}/lib/libvgf.a"
  )

list(APPEND _cmake_import_check_targets VGF::vgf )
list(APPEND _cmake_import_check_files_for_VGF::vgf "${_IMPORT_PREFIX}/lib/libvgf.a" )

# Import target "VGF::vgf_dump" for configuration "Debug"
set_property(TARGET VGF::vgf_dump APPEND PROPERTY IMPORTED_CONFIGURATIONS DEBUG)
set_target_properties(VGF::vgf_dump PROPERTIES
  IMPORTED_LOCATION_DEBUG "${_IMPORT_PREFIX}/bin/vgf_dump"
  )

list(APPEND _cmake_import_check_targets VGF::vgf_dump )
list(APPEND _cmake_import_check_files_for_VGF::vgf_dump "${_IMPORT_PREFIX}/bin/vgf_dump" )

# Import target "VGF::vgf_updater" for configuration "Debug"
set_property(TARGET VGF::vgf_updater APPEND PROPERTY IMPORTED_CONFIGURATIONS DEBUG)
set_target_properties(VGF::vgf_updater PROPERTIES
  IMPORTED_LOCATION_DEBUG "${_IMPORT_PREFIX}/bin/vgf_updater"
  )

list(APPEND _cmake_import_check_targets VGF::vgf_updater )
list(APPEND _cmake_import_check_files_for_VGF::vgf_updater "${_IMPORT_PREFIX}/bin/vgf_updater" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
