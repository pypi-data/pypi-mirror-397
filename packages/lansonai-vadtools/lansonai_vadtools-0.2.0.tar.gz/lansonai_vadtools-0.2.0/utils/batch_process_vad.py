#!/usr/bin/env python3
"""
VAD数据批量处理脚本
用于批量处理VAD输出目录中的timestamps.json文件并写入数据库
"""

import sys
import argparse
from pathlib import Path
import json
from typing import Dict, Optional

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent))

from vad_data_processor import process_batch_timestamps_files, process_single_timestamps_file
from db_connection import test_database_connection

def load_task_mapping(mapping_file: str) -> Dict[str, str]:
    """
    从JSON文件加载run_id到task_id的映射
    
    Args:
        mapping_file: 映射文件路径
        
    Returns:
        映射字典
    """
    try:
        with open(mapping_file, 'r', encoding='utf-8') as f:
            mapping = json.load(f)
        print(f"✅ 成功加载映射文件: {mapping_file}")
        print(f"📊 映射条目数: {len(mapping)}")
        return mapping
    except Exception as e:
        print(f"❌ 加载映射文件失败: {e}")
        return {}

def create_sample_mapping_file(output_file: str, vad_output_dir: str):
    """
    创建示例映射文件
    
    Args:
        output_file: 输出文件路径
        vad_output_dir: VAD输出目录
    """
    try:
        vad_dir = Path(vad_output_dir)
        if not vad_dir.exists():
            print(f"❌ VAD输出目录不存在: {vad_output_dir}")
            return
        
        # 扫描所有timestamps.json文件
        timestamps_files = list(vad_dir.glob("*/timestamps.json"))
        
        # 创建映射（假设run_id和task_id相同）
        mapping = {}
        for file_path in timestamps_files:
            run_id = file_path.parent.name
            mapping[run_id] = run_id  # 默认映射到相同的ID
        
        # 保存映射文件
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(mapping, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 示例映射文件已创建: {output_file}")
        print(f"📊 包含 {len(mapping)} 个映射条目")
        print(f"💡 请根据实际情况编辑映射文件")
        
    except Exception as e:
        print(f"❌ 创建示例映射文件失败: {e}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="VAD数据批量处理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 批量处理（自动映射）
  python batch_process_vad.py /path/to/vad/output

  # 使用自定义映射文件
  python batch_process_vad.py /path/to/vad/output --mapping mapping.json

  # 处理单个文件
  python batch_process_vad.py --single /path/to/timestamps.json task-id

  # 创建示例映射文件
  python batch_process_vad.py --create-mapping mapping.json /path/to/vad/output

  # 测试数据库连接
  python batch_process_vad.py --test-db
        """
    )
    
    parser.add_argument(
        'input_path',
        nargs='?',
        help='VAD输出目录路径或timestamps.json文件路径'
    )
    
    parser.add_argument(
        'task_id',
        nargs='?',
        help='任务ID（仅在单文件模式下需要）'
    )
    
    parser.add_argument(
        '--mapping', '-m',
        help='run_id到task_id的映射文件（JSON格式）'
    )
    
    parser.add_argument(
        '--single', '-s',
        action='store_true',
        help='单文件处理模式'
    )
    
    parser.add_argument(
        '--create-mapping', '-c',
        metavar='OUTPUT_FILE',
        help='创建示例映射文件'
    )
    
    parser.add_argument(
        '--test-db', '-t',
        action='store_true',
        help='测试数据库连接'
    )
    
    parser.add_argument(
        '--dry-run', '-d',
        action='store_true',
        help='试运行模式（不实际写入数据库）'
    )
    
    args = parser.parse_args()
    
    # 测试数据库连接
    if args.test_db:
        print("🔍 测试数据库连接...")
        success = test_database_connection()
        sys.exit(0 if success else 1)
    
    # 创建示例映射文件
    if args.create_mapping:
        if not args.input_path:
            print("❌ 创建映射文件需要指定VAD输出目录")
            sys.exit(1)
        create_sample_mapping_file(args.create_mapping, args.input_path)
        sys.exit(0)
    
    # 检查输入路径
    if not args.input_path:
        print("❌ 请指定输入路径")
        parser.print_help()
        sys.exit(1)
    
    # 检查输入路径是否存在
    input_path = Path(args.input_path)
    if not input_path.exists():
        print(f"❌ 输入路径不存在: {args.input_path}")
        sys.exit(1)
    
    # 试运行模式提示
    if args.dry_run:
        print("🔍 试运行模式：将验证文件但不写入数据库")
    
    # 测试数据库连接
    print("🔍 测试数据库连接...")
    if not test_database_connection():
        print("❌ 数据库连接失败，无法继续")
        sys.exit(1)
    
    try:
        if args.single:
            # 单文件处理模式
            if not args.task_id:
                print("❌ 单文件模式需要指定task_id")
                sys.exit(1)
            
            print(f"📄 单文件处理模式")
            print(f"📁 文件: {args.input_path}")
            print(f"🆔 任务ID: {args.task_id}")
            
            if args.dry_run:
                print("🔍 试运行：跳过实际处理")
                success = True
            else:
                success = process_single_timestamps_file(str(input_path), args.task_id)
            
            if success:
                print("✅ 单文件处理成功")
            else:
                print("❌ 单文件处理失败")
                sys.exit(1)
        
        else:
            # 批量处理模式
            print(f"📂 批量处理模式")
            print(f"📁 目录: {args.input_path}")
            
            # 加载映射文件（如果提供）
            task_mapping = None
            if args.mapping:
                task_mapping = load_task_mapping(args.mapping)
                if not task_mapping:
                    print("❌ 映射文件加载失败")
                    sys.exit(1)
            
            if args.dry_run:
                print("🔍 试运行：跳过实际处理")
                # 在试运行模式下，只扫描文件
                vad_dir = Path(args.input_path)
                timestamps_files = list(vad_dir.glob("*/timestamps.json"))
                print(f"📊 发现 {len(timestamps_files)} 个timestamps文件")
                
                for file_path in timestamps_files[:5]:  # 只显示前5个
                    run_id = file_path.parent.name
                    task_id = task_mapping.get(run_id, run_id) if task_mapping else run_id
                    print(f"  📄 {run_id} -> {task_id}")
                
                if len(timestamps_files) > 5:
                    print(f"  ... 还有 {len(timestamps_files) - 5} 个文件")
                
                results = {f.parent.name: True for f in timestamps_files}
            else:
                results = process_batch_timestamps_files(str(input_path), task_mapping)
            
            # 输出结果统计
            successful = sum(1 for success in results.values() if success)
            total = len(results)
            
            print(f"\n📊 处理结果统计:")
            print(f"  📝 总文件数: {total}")
            print(f"  ✅ 成功: {successful}")
            print(f"  ❌ 失败: {total - successful}")
            print(f"  📈 成功率: {successful/total*100:.1f}%" if total > 0 else "  📈 成功率: 0%")
            
            # 显示详细结果
            if total <= 10:  # 如果文件数不多，显示所有结果
                print(f"\n📋 详细结果:")
                for run_id, success in results.items():
                    status = "✅ 成功" if success else "❌ 失败"
                    print(f"  {run_id}: {status}")
            else:  # 否则只显示失败的
                failed_items = [run_id for run_id, success in results.items() if not success]
                if failed_items:
                    print(f"\n❌ 失败的文件:")
                    for run_id in failed_items:
                        print(f"  {run_id}")
            
            if successful < total:
                sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 处理过程中发生异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("\n🎉 处理完成")

if __name__ == "__main__":
    main()
