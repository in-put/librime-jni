#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import subprocess
import argparse
from pathlib import Path


def merge_tw_phrases(dict_dir, scripts_dir, output_dir):
    """合并TWPhrases文件"""
    input_files = ["TWPhrasesIT.txt", "TWPhrasesName.txt", "TWPhrasesOther.txt"]

    output_file = Path(output_dir) / "TWPhrases.txt"
    merge_script = Path(scripts_dir) / "merge.py"  # 添加.py扩展名

    # 构建完整路径
    input_paths = [Path(dict_dir) / f for f in input_files]

    # 检查输入文件是否存在
    for input_path in input_paths:
        if not input_path.exists():
            print(f"错误: 输入文件不存在: {input_path}")
            return False

    # 检查merge脚本是否存在
    if not merge_script.exists():
        print(f"错误: merge脚本不存在: {merge_script}")
        return False

    # 执行merge命令，使用Python解释器
    cmd = (
        [sys.executable, str(merge_script)]
        + [str(p) for p in input_paths]
        + [str(output_file)]
    )

    try:
        print(f"执行: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"成功生成: {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"错误: merge命令执行失败: {e}")
        print(f"stderr: {e.stderr}")
        return False


def reverse_files(dict_dir, scripts_dir, output_dir):
    """生成反向文件"""
    files_to_reverse = ["TWVariants", "TWPhrases", "HKVariants", "JPVariants"]

    reverse_script = Path(scripts_dir) / "reverse.py"  # 添加.py扩展名

    # 检查reverse脚本是否存在
    if not reverse_script.exists():
        print(f"错误: reverse脚本不存在: {reverse_script}")
        return False

    success_count = 0

    for txt in files_to_reverse:
        input_file = Path(dict_dir) / f"{txt}.txt"
        output_file = Path(output_dir) / f"{txt}Rev.txt"

        # 检查输入文件是否存在
        if not input_file.exists():
            print(f"警告: 输入文件不存在，跳过: {input_file}")
            continue

        # 执行reverse命令，使用Python解释器
        cmd = [sys.executable, str(reverse_script), str(input_file), str(output_file)]

        try:
            print(f"执行: {' '.join(cmd)}")
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"成功生成: {output_file}")
            success_count += 1
        except subprocess.CalledProcessError as e:
            print(f"错误: reverse命令执行失败 ({txt}): {e}")
            print(f"stderr: {e.stderr}")

    return success_count > 0


def main():
    parser = argparse.ArgumentParser(
        description="OpenCC数据文件处理脚本",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    data_dir = "OpenCC/data"
    parser.add_argument(
        "--dict-dir", default=data_dir + "/dictionary", help="数据文件目录"
    )
    parser.add_argument("--scripts-dir", default=data_dir + "/scripts", help="脚本目录")
    parser.add_argument(
        "--output-dir", default=data_dir + "/dictionary", help="输出目录"
    )
    parser.add_argument("--merge-only", action="store_true", help="只执行merge操作")
    parser.add_argument("--reverse-only", action="store_true", help="只执行reverse操作")

    args = parser.parse_args()

    # 创建输出目录
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    success = True

    if not args.reverse_only:
        print("开始合并TWPhrases文件...")
        if not merge_tw_phrases(args.dict_dir, args.scripts_dir, args.output_dir):
            success = False

    if not args.merge_only:
        print("开始生成反向文件...")
        if not reverse_files(args.dict_dir, args.scripts_dir, args.output_dir):
            success = False

    if success:
        print("所有操作完成!")
        return 0
    else:
        print("部分操作失败!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
