cmake_minimum_required(VERSION 3.0)
project(ear)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)
set(CMAKE_INCLUDE_CURRENT_DIR ON)

find_package(Qt5 COMPONENTS
        Core
        Gui
        Qml
        Quick
        Multimedia
        REQUIRED)

find_package(PkgConfig REQUIRED)
pkg_check_modules(TAGLIB REQUIRED IMPORTED_TARGET taglib)

add_executable(music main.cpp resources.qrc audio_player.cpp audio_player.h song.h playlist_model.cpp playlist_model.h app_state.cpp app_state.h metadata_loader.cpp metadata_loader.h cover_image_provider.cpp cover_image_provider.h)

target_link_libraries(music
        Qt5::Core
        Qt5::Gui
        Qt5::Qml
        Qt5::Quick
        Qt5::Multimedia
        PkgConfig::TAGLIB)
