# Trime Prebuilt

预编译用于 Trime 的 JNI 库以及 OpenCC 数据。

## 环境准备

### 1. 克隆项目

```bash
git clone --recursive https://github.com/in-put/trime-prebuilt.git
cd trime-prebuilt
```

### 2. 安装 CMake 和 Ninja

确保已安装必需的工具：

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install cmake ninja-build

# macOS
brew install cmake ninja

# Windows
# 使用 Chocolatey
choco install cmake ninja

# 或使用 Scoop
scoop install cmake ninja
```

### 3. Android NDK 设置

下载并安装 [Android NDK](https://developer.android.com/ndk/downloads)，然后设置环境变量：

```bash
# Linux/macOS
export ANDROID_NDK_HOME=/path/to/android-ndk/[version]
export PATH=$ANDROID_NDK_HOME:$PATH

# 检查 NDK 是否正确安装
ls $ANDROID_NDK_HOME/build/cmake/android.toolchain.cmake
```
```powershell
# Windows (PowerShell)
$env:ANDROID_NDK_HOME = "C:\path\to\android-ndk\[version]"
$env:PATH += ";$env:ANDROID_NDK_HOME"

# 检查 NDK 是否正确安装
ls $env:ANDROID_NDK_HOME/build/cmake/android.toolchain.cmake
```

> 可选的环境变量：`ANDROID_NDK_ROOT`、`ANDROID_NDK`、`NDK_HOME`、`NDK_ROOT`

## 构建

**第一次构建需要以管理员身份运行**

### 基本构建

```bash
# 使用默认配置构建 (arm64-v8a, Release)
python make.py build

# 指定架构构建
python make.py build --arch arm64-v8a
python make.py build --arch armeabi-v7a
python make.py build --arch x86
python make.py build --arch x86_64

# 指定 NDK 路径
python make.py build --ndk /path/to/android-ndk/[version]

# Debug 构建
python make.py build --debug

# 指定最低 API 级别
python make.py build --min-api 25
```

### 清理缓存

```bash
# 清理所有构建文件（删除 build-android 目录）
python make.py clean
```

### 代码格式化

```bash
# 格式化 JNI 代码
python make.py format
```

## 输出产物

构建完成后，产物将存放在以下位置：

- **头文件**: `output/include/`
- **库文件**: `output/jniLibs/`

最终的发布包 `prebuilt.zip` 包含：
- `include/` - C++ 头文件
- `lib/` - 编译后的 .so 库文件  
- `opencc/` - OpenCC 字典和配置文件
