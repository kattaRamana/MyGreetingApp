[app]
title = Dynamic Greeting App
package.name = greetingapp
package.domain = org.katta
source.dir = .
source.include_exts = py,png,jpg,jpeg,ttf
version = 0.1
requirements = python3,kivy,plyer,pillow
orientation = portrait
fullscreen = 1

# Android configurations
android.permissions = CAMERA, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, MOUNT_UNMOUNT_FILESYSTEMS
android.api = 33
android.minapi = 21
android.ndk_api = 21
android.archs = arm64-v8a, armeabi-v7a
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
