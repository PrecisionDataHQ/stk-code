#!/bin/sh
set -eu
: "${JOYORBIT_STK_SOURCE:?Set to the prepared SuperTuxKart-1.5-src directory}"
: "${ANDROID_SDK_ROOT:?Set Android SDK path}"
: "${JAVA_HOME:?Use JDK 17}"
export SDK_PATH="$ANDROID_SDK_ROOT"
export NDK_PATH="$ANDROID_SDK_ROOT/ndk"
export STK_NDK_VERSION=28.2.13676358
export COMPILE_ARCH=aarch64 BUILD_TYPE=debug PROJECT_VERSION=1.5
cd "$JOYORBIT_STK_SOURCE/android"
sh make_deps.sh
sh make.sh
