cd build

cmake .. \
  -DCMAKE_TOOLCHAIN_FILE="/home/cx/android-ndk-r28b/build/cmake/android.toolchain.cmake" \
  -DCMAKE_SYSTEM_NAME=Android \
  -DCMAKE_SYSTEM_VERSION=14 \
  -DCMAKE_ANDROID_NDK_TOOLCHAIN_VERSION=clang \
  -DANDROID_ABI="arm64-v8a" \
  -DANDROID_NATIVE_API_LEVEL=24 \
  -DCMAKE_BUILD_TYPE=Release

cmake --build .
cmake --install .

cd ..
