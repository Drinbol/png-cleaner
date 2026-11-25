#!/usr/bin/env python3
"""
批量删除PNG文件的Python脚本

功能：
1. 接受一个文件夹路径作为参数
2. 找到所有PNG文件
3. 对于大于50KB的文件，保留它们
4. 同时保留这些文件的多一个下划线的版本（例如：a.png > 50KB，则保留a.png和a_.png）
5. 删除其他小于50KB且没有对应大于50KB版本的PNG文件

使用方法：
python main.py 文件夹路径
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Set, Tuple


def get_png_files(folder_path: str) -> List[Path]:
    """获取指定文件夹中的所有PNG文件"""
    folder = Path(folder_path)
    if not folder.exists():
        raise FileNotFoundError(f"文件夹不存在: {folder_path}")
    if not folder.is_dir():
        raise NotADirectoryError(f"路径不是文件夹: {folder_path}")
    
    # 递归查找所有PNG文件
    png_files = list(folder.rglob("*.png"))
    # 同时查找.PNG（大写扩展名）
    png_files.extend(folder.rglob("*.PNG"))
    
    return png_files


def get_file_size_kb(file_path: Path) -> float:
    """获取文件大小（KB）"""
    return file_path.stat().st_size / 1024


def find_files_to_keep(png_files: List[Path]) -> Tuple[Set[Path], Set[Path]]:
    """
    找出需要保留的文件和需要删除的文件
    
    返回：
    - files_to_keep: 需要保留的文件集合
    - files_to_delete: 需要删除的文件集合
    """
    # 存储大于50KB的文件（不含下划线版本）
    large_files = set()
    
    # 第一步：找出所有大于50KB的文件
    for file_path in png_files:
        if get_file_size_kb(file_path) > 50:
            large_files.add(file_path)
    
    # 第二步：构建需要保留的文件集合
    files_to_keep = set(large_files)  # 首先保留所有大于50KB的文件
    
    # 第三步：为每个大于50KB的文件，查找其带下划线的版本
    for large_file in large_files:
        # 获取文件名和目录
        dir_path = large_file.parent
        file_name = large_file.name
        
        # 构建带下划线的版本
        # 例如：a.png -> a_.png
        name_without_ext = file_name.rsplit('.', 1)[0]
        ext = file_name.rsplit('.', 1)[1] if '.' in file_name else ''
        
        # 创建带下划线的文件名
        underscored_name = f"{name_without_ext}_.{ext}"
        underscored_path = dir_path / underscored_name
        
        # 如果带下划线的文件存在，则保留它
        if underscored_path.exists() and underscored_path in png_files:
            files_to_keep.add(underscored_path)
    
    # 第四步：确定需要删除的文件（所有PNG文件中不在保留集合里的）
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
        description="批量删除PNG文件脚本 - 保留大于50KB的文件及其带下划线的版本"
    )
    parser.add_argument(
        "folder",
        help="要处理的文件夹路径"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="模拟运行，显示将要删除的文件但不实际删除"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="显示详细信息"
    )
    
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
        files_to_keep, files_to_delete = find_files_to_keep(png_files)
        
        # 显示统计信息
        print(f"\n统计信息:")
        print(f"总PNG文件数: {len(png_files)}")
        print(f"需要保留的文件数: {len(files_to_keep)}")
        print(f"需要删除的文件数: {len(files_to_delete)}")
        
        # 显示大于50KB的文件
        large_files = [f for f in png_files if get_file_size_kb(f) > 50]
        if large_files and args.verbose:
            print(f"\n大于50KB的文件 ({len(large_files)}个):")
            for file_path in sorted(large_files):
                size_kb = get_file_size_kb(file_path)
                print(f"  {file_path.name}: {size_kb:.2f} KB")
        
        # 显示需要保留的文件（详细模式）
        if args.verbose and files_to_keep:
            print(f"\n需要保留的文件:")
            for file_path in sorted(files_to_keep):
                size_kb = get_file_size_kb(file_path)
                status = "(大于50KB)" if size_kb > 50 else "(带下划线版本)"
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
