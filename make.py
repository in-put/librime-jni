#!/usr/bin/env python3
"""
Android NDK 跨平台构建工具
支持 build, clean 和 format 命令
"""

import argparse
import os
import subprocess
import sys
import platform
import shutil
from pathlib import Path

# 默认配置
DEFAULT_CONFIG = {
    "arch": "arm64-v8a",
    "min_api": 25,
    "build_type": "Release",
    "build_dir": "build-android",
    "ndk_path": "",
    "jni_dir": "librime_jni",
}


def detect_ndk_path():
    """自动检测 NDK 安装路径"""
    # 1. 检查环境变量
    env_vars = [
        "ANDROID_NDK_HOME",
        "ANDROID_NDK_ROOT",
        "ANDROID_NDK",
        "NDK_HOME",
        "NDK_ROOT",
    ]
    for var in env_vars:
        if var in os.environ:
            path = Path(os.environ[var])
            if (path / "build/cmake/android.toolchain.cmake").exists():
                return str(path)

    # 2. 检查常见安装位置
    common_paths = []
    if platform.system() == "Windows":
        common_paths.extend(
            [
                Path(os.environ.get("LOCALAPPDATA", "")) / "Android/Sdk/ndk",
                Path(os.environ.get("ProgramFiles", "")) / "Android/android-sdk/ndk",
                Path.home() / "AppData/Local/Android/Sdk/ndk",
            ]
        )
    else:
        common_paths.extend(
            [
                Path.home() / "Android/Sdk/ndk",
                Path.home() / "Library/Android/sdk/ndk",
                Path("/opt/android-sdk/ndk"),
            ]
        )

    # 查找最新版本
    for base_path in common_paths:
        if base_path.exists():
            versions = sorted(base_path.iterdir(), key=os.path.getmtime, reverse=True)
            for version in versions:
                if (version / "build/cmake/android.toolchain.cmake").exists():
                    return str(version)

    return ""


def build_project(args):
    """构建项目"""
    config = DEFAULT_CONFIG.copy()

    # 处理参数
    if args.ndk:
        config["ndk_path"] = args.ndk
    if args.arch:
        config["arch"] = args.arch
    if args.release:
        config["build_type"] = "Release"
    if args.debug:
        config["build_type"] = "Debug"
    if args.min_api:
        config["min_api"] = args.min_api

    # 验证 NDK 路径
    ndk_path = Path(config["ndk_path"])
    toolchain_file = ndk_path / "build/cmake/android.toolchain.cmake"
    if ndk_path != Path(""):
        if not toolchain_file.exists():
            print(f"错误: 无效的 NDK 路径 - 未找到 {toolchain_file}")
            sys.exit(1)
    else:
        # 自动检测 NDK 路径
        detected_ndk = detect_ndk_path()
        if detected_ndk:
            config["ndk_path"] = detected_ndk
            toolchain_file = Path(detected_ndk) / "build/cmake/android.toolchain.cmake"
            print(f"自动检测到 NDK 路径: {detected_ndk}")
        else:
            print("错误: 未指定 NDK 路径且无法自动检测")
            print("请使用 --ndk 指定路径或设置 ANDROID_NDK_HOME 环境变量")
            sys.exit(1)

    # 准备构建目录
    build_dir = config["build_dir"]
    # 创建构建目录
    build_path = Path(build_dir) / config["arch"]
    if not build_path.exists():
        build_path.mkdir(parents=True, exist_ok=True)
    build_dir = str(build_path)

    # 生成 CMake 命令
    cmake_cmd = ["cmake", ".", "-B", build_dir, "-G", "Ninja"]

    # 添加 CMake 选项
    cmake_cmd.extend(
        [
            f"-DCMAKE_TOOLCHAIN_FILE={toolchain_file}",
            f"-DANDROID_ABI={config['arch']}",
            f"-DCMAKE_BUILD_TYPE={config['build_type']}",
            f"-DANDROID_NATIVE_API_LEVEL={config['min_api']}",
            "-DCMAKE_ANDROID_NDK_TOOLCHAIN_VERSION=clang",
            "-DCMAKE_SYSTEM_NAME=Android",
            "-DCMAKE_SYSTEM_VERSION=14",
            "-DCMAKE_EXPORT_COMPILE_COMMANDS=1",
        ]
    )

    # 运行 CMake 配置
    print("\n" + "=" * 50)
    print("配置 Android 构建")
    print(f"  架构: {config['arch']}")
    print(f"  最低 API 级别: {config['min_api']}")
    print(f"  构建类型: {config['build_type']}")
    print(f"  NDK: {config['ndk_path']}")
    print(f"  构建目录: {build_dir}")
    print("=" * 50 + "\n")

    # 运行 CMake 命令
    res = subprocess.run(cmake_cmd)
    if res.returncode != 0:
        print("错误: CMake 配置失败")
        sys.exit(1)

    # 构建命令
    build_cmd = ["cmake", "--build", build_dir]

    # 运行构建
    print("\n" + "=" * 50)
    print("开始构建")
    print("=" * 50 + "\n")
    res = subprocess.run(build_cmd)
    if res.returncode != 0:
        print("错误: 构建失败")
        sys.exit(1)

    build_cmd[1] = "--install"
    res = subprocess.run(build_cmd)
    if res.returncode != 0:
        print("错误: 安装失败")
        sys.exit(1)


def clean_project(args):
    """清理构建目录"""
    config = DEFAULT_CONFIG.copy()

    clean_dir = Path(config["build_dir"])
    # 执行清理
    if clean_dir.exists():
        shutil.rmtree(clean_dir)


def format_code(args):
    """格式化 JNI 代码"""
    config = DEFAULT_CONFIG.copy()

    # 确定格式化目录
    jni_dir = Path(config["jni_dir"])
    if not jni_dir.exists():
        print(f"错误: JNI 目录不存在: {jni_dir}")
        sys.exit(1)

    # 检查 clang-format
    try:
        subprocess.run(
            ["clang-format", "--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        print("错误: 未找到 clang-format, 请先安装")
        sys.exit(1)

    # 收集源文件
    source_files = []
    for ext in ("*.h", "*.hpp", "*.c", "*.cc", "*.cpp"):
        source_files.extend(jni_dir.rglob(ext))

    if not source_files:
        print(f"在 {jni_dir} 中未找到源文件")
        return

    # 格式化命令
    format_cmd = ["clang-format", "-i", "--style=file"]

    # 执行格式化
    print(f"格式化 {len(source_files)} 个文件...")
    for file in source_files:
        if args.verbose:
            print(f"格式化: {file}")
        subprocess.call(format_cmd + [str(file)])

    print("格式化完成")


def main():
    parser = argparse.ArgumentParser(
        description="Android NDK 跨平台构建工具",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--verbose", action="store_true", help="显示详细输出")

    # 子命令
    subparsers = parser.add_subparsers(dest="command", required=True)

    # build 命令
    build_parser = subparsers.add_parser("build", help="构建项目")
    build_parser.add_argument("--ndk", help="Android NDK 路径")
    build_parser.add_argument(
        "--arch", choices=["armeabi-v7a", "arm64-v8a", "x86", "x86_64"], help="目标架构"
    )
    build_parser.add_argument("--release", action="store_true", help="发布构建")
    build_parser.add_argument("--debug", action="store_true", help="调试构建")
    build_parser.add_argument("--min-api", type=int, help="最低 Android API 级别")
    build_parser.set_defaults(func=build_project)

    # clean 命令
    clean_parser = subparsers.add_parser("clean", help="清理构建目录")
    clean_parser.set_defaults(func=clean_project)

    # format 命令
    format_parser = subparsers.add_parser("format", help="格式化 JNI 代码")
    format_parser.set_defaults(func=format_code)

    # 解析参数
    args = parser.parse_args()

    # 检查 build_type 冲突
    if hasattr(args, "release") and hasattr(args, "debug"):
        if args.release and args.debug:
            print("错误: --release 和 --debug 不能同时使用")
            sys.exit(1)

    # 执行命令
    args.func(args)


if __name__ == "__main__":
    main()
