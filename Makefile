# SPDX-FileCopyrightText: 2015 - 2024 Rime community
#
# SPDX-License-Identifier: GPL-3.0-or-later


.PHONY: all clean build debug spotlessCheck spotlessApply clang-format-lint clang-format style-lint style-apply release install translate ndk android

all: release

clang-format-lint:
	./clang-format.sh -n

clang-format:
	./clang-format.sh -i

ndk:
	(cd $(mainDir); ndk-build)

android:
	cmake -Bbuild-$@ -H.\
		-DCMAKE_SYSTEM_NAME=Android \
		-DCMAKE_ANDROID_STL_TYPE=c++_static \
		-DCMAKE_SYSTEM_VERSION=14 \
		-DCMAKE_ANDROID_NDK_TOOLCHAIN_VERSION=clang \
		-DCMAKE_ANDROID_ARCH_ABI=armeabi
	${MAKE} -C build-$@ rime_jni
