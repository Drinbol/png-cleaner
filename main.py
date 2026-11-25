#!/usr/bin/env python3
"""
png-cleaner — 按大小规则批量清理 PNG 文件

规则：
1. 保留所有大于阈值（默认 50KB）的 PNG 文件
2. 同时保留这些文件的"下划线版本"（例如 a.png > 50KB，则保留 a.png 和 a_.png）
3. 删除其余小于阈值且没有对应大文件的 PNG

用法：
    python main.py 文件夹路径 [--threshold 50] [--dry-run] [--verbose]
"""

import sys
import argparse
from pathlib import Path
from typing import List, Set, Tuple

DEFAULT_THRESHOLD_KB = 50.0


def get_png_files(folder_path: str) -> List[Path]:
    """递归获取指定文件夹中的所有 PNG 文件（含大写扩展名）"""
    folder = Path(folder_path)
    if not folder.exists():
        raise FileNotFoundError(f"文件夹不存在: {folder_path}")
    if not folder.is_dir():
        raise NotADirectoryError(f"路径不是文件夹: {folder_path}")

    # rglob 在大小写不敏感的文件系统上可能重复匹配，用 set 去重
    png_files = set(folder.rglob("*.png")) | set(folder.rglob("*.PNG"))
    return sorted(png_files)


def get_file_size_kb(file_path: Path) -> float:
    """获取文件大小（KB）"""
    return file_path.stat().st_size / 1024


def find_files_to_keep(png_files: List[Path], threshold_kb: float = DEFAULT_THRESHOLD_KB) -> Tuple[Set[Path], Set[Path]]:
    """
    找出需要保留的文件和需要删除的文件

    返回：
    - files_to_keep: 需要保留的文件集合
    - files_to_delete: 需要删除的文件集合
    """
    # 第一步：找出所有大于阈值的文件
    large_files = {f for f in png_files if get_file_size_kb(f) > threshold_kb}

    # 第二步：保留所有大于阈值的文件
    files_to_keep = set(large_files)

    # 第三步：为每个大文件保留其带下划线的版本（a.png -> a_.png）
    png_set = set(png_files)
    for large_file in large_files:
        underscored_path = large_file.with_name(f"{large_file.stem}_.{large_file.suffix.lstrip('.')}")
        if underscored_path in png_set:
            files_to_keep.add(underscored_path)

    # 第四步：其余全部删除
    files_to_delete = set(png_files) - files_to_keep

    return files_to_keep, files_to_delete


def delete_files(files_to_delete: Set[Path], dry_run: bool = False) -> int:
    """删除文件，如果dry_run为True则只显示不实际删除"""
    deleted_count = 0
    
    for file_path in sorted(files_to_delete):
        try:
            if dry_run:
                print(f"[DRY RUN] 将删除: {file_path}")
            else:
                file_path.unlink()
                print(f"已删除: {file_path}")
                deleted_count += 1
        except Exception as e:
            print(f"删除文件失败 {file_path}: {e}")
    
    return deleted_count


def main():
    parser = argparse.ArgumentParser(
        description="按大小规则批量清理 PNG：保留大于阈值的大图及其下划线版本，删除其余小图"
    )
    parser.add_argument("folder", help="要处理的文件夹路径")
    parser.add_argument(
        "-t", "--threshold",
        type=float,
        default=DEFAULT_THRESHOLD_KB,
        help=f"大小阈值（KB），默认 {DEFAULT_THRESHOLD_KB:.0f}",
    )
    parser.add_argument("--dry-run", action="store_true", help="模拟运行，只显示不删除")
    parser.add_argument("--verbose", action="store_true", help="显示详细信息")

    args = parser.parse_args()

    try:
        # 获取所有PNG文件
        png_files = get_png_files(args.folder)

        if args.verbose:
            print(f"在文件夹 '{args.folder}' 中找到 {len(png_files)} 个PNG文件")

        if not png_files:
            print("没有找到PNG文件")
            return

        # 找出需要保留和删除的文件
        files_to_keep, files_to_delete = find_files_to_keep(png_files, args.threshold)

        # 显示统计信息
        print(f"\n统计信息（阈值 {args.threshold:.0f} KB）:")
        print(f"总PNG文件数: {len(png_files)}")
        print(f"需要保留的文件数: {len(files_to_keep)}")
        print(f"需要删除的文件数: {len(files_to_delete)}")

        # 显示大于阈值的文件
        large_files = [f for f in png_files if get_file_size_kb(f) > args.threshold]
        if large_files and args.verbose:
            print(f"\n大于{args.threshold:.0f}KB的文件 ({len(large_files)}个):")
            for file_path in sorted(large_files):
                size_kb = get_file_size_kb(file_path)
                print(f"  {file_path.name}: {size_kb:.2f} KB")

        # 显示需要保留的文件（详细模式）
        if args.verbose and files_to_keep:
            print(f"\n需要保留的文件:")
            for file_path in sorted(files_to_keep):
                size_kb = get_file_size_kb(file_path)
                status = f"(大于{args.threshold:.0f}KB)" if size_kb > args.threshold else "(带下划线版本)"
                print(f"  {file_path.name}: {size_kb:.2f} KB {status}")
        
        # 显示将要删除的文件
        if files_to_delete:
            print(f"\n将要删除的文件 ({len(files_to_delete)}个):")
            for file_path in sorted(files_to_delete):
                size_kb = get_file_size_kb(file_path)
                print(f"  {file_path.name}: {size_kb:.2f} KB")
            
            # 确认删除
            if not args.dry_run:
                response = input(f"\n确认删除以上 {len(files_to_delete)} 个文件？(y/N): ")
                if response.lower() != 'y':
                    print("操作已取消")
                    return
            
            # 执行删除
            deleted_count = delete_files(files_to_delete, args.dry_run)
            
            if args.dry_run:
                print(f"\n[DRY RUN] 模拟删除完成，将删除 {len(files_to_delete)} 个文件")
            else:
                print(f"\n删除完成，实际删除了 {deleted_count} 个文件")
        else:
            print("\n没有需要删除的文件")
            
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
