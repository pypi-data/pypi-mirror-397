"""
VAD数据处理工具使用示例
演示如何使用vad_data_processor处理timestamps.json文件并写入数据库
"""

import sys
from pathlib import Path
import uuid

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent))

from vad_data_processor import VADDataProcessor, process_single_timestamps_file, process_batch_timestamps_files
from db_connection import get_db_connection, test_database_connection

def example_single_file_processing():
    """示例：处理单个timestamps.json文件"""
    print("=== 单文件处理示例 ===")
    
    # 示例文件路径（需要替换为实际路径）
    timestamps_file = "/home/isakeem/Code/subtitle-storage-service/scripts/.output/vad/bf88cff8-b7f1-4754-af75-ccd1aa2ae6c9/timestamps.json"
    
    # 示例task_id（需要替换为实际的task_id）
    task_id = "bf88cff8-b7f1-4754-af75-ccd1aa2ae6c9"
    
    # 检查文件是否存在
    if not Path(timestamps_file).exists():
        print(f"❌ 文件不存在: {timestamps_file}")
        return False
    
    # 处理文件
    print(f"📁 处理文件: {timestamps_file}")
    print(f"🆔 任务ID: {task_id}")
    
    success = process_single_timestamps_file(timestamps_file, task_id)
    
    if success:
        print("✅ 单文件处理成功")
    else:
        print("❌ 单文件处理失败")
    
    return success

def example_batch_processing():
    """示例：批量处理timestamps.json文件"""
    print("\n=== 批量处理示例 ===")
    
    # 示例目录路径
    timestamps_dir = "/home/isakeem/Code/subtitle-storage-service/scripts/.output/vad"
    
    # 检查目录是否存在
    if not Path(timestamps_dir).exists():
        print(f"❌ 目录不存在: {timestamps_dir}")
        return {}
    
    print(f"📂 处理目录: {timestamps_dir}")
    
    # 批量处理（假设run_id和task_id相同）
    results = process_batch_timestamps_files(timestamps_dir)
    
    print(f"\n📊 处理结果:")
    successful = 0
    for run_id, success in results.items():
        status = "✅ 成功" if success else "❌ 失败"
        print(f"  {run_id}: {status}")
        if success:
            successful += 1
    
    print(f"\n📈 统计: {successful}/{len(results)} 成功")
    return results

def example_with_custom_mapping():
    """示例：使用自定义task_id映射的批量处理"""
    print("\n=== 自定义映射批量处理示例 ===")
    
    timestamps_dir = "/home/isakeem/Code/subtitle-storage-service/scripts/.output/vad"
    
    # 自定义run_id到task_id的映射
    task_mapping = {
        "bf88cff8-b7f1-4754-af75-ccd1aa2ae6c9": "bf88cff8-b7f1-4754-af75-ccd1aa2ae6c9",
        "7aef2ade-013a-435f-8bd8-109de9b7ec32": "7aef2ade-013a-435f-8bd8-109de9b7ec32",
        # 可以添加更多映射...
    }
    
    print(f"📂 处理目录: {timestamps_dir}")
    print(f"🗺️  使用自定义映射: {len(task_mapping)} 个条目")
    
    results = process_batch_timestamps_files(timestamps_dir, task_mapping)
    
    print(f"\n📊 处理结果:")
    for run_id, success in results.items():
        status = "✅ 成功" if success else "❌ 失败"
        mapped_task = task_mapping.get(run_id, run_id)
        print(f"  {run_id} -> {mapped_task}: {status}")
    
    return results

def example_advanced_usage():
    """示例：高级用法 - 使用VADDataProcessor类"""
    print("\n=== 高级用法示例 ===")
    
    try:
        # 使用上下文管理器
        with VADDataProcessor() as processor:
            print("🔗 数据库连接已建立")
            
            # 处理单个文件
            timestamps_file = "/home/isakeem/Code/subtitle-storage-service/scripts/.output/vad/bf88cff8-b7f1-4754-af75-ccd1aa2ae6c9/timestamps.json"
            task_id = "bf88cff8-b7f1-4754-af75-ccd1aa2ae6c9"
            
            if Path(timestamps_file).exists():
                success = processor.process_timestamps_file(timestamps_file, task_id)
                print(f"📄 文件处理结果: {'✅ 成功' if success else '❌ 失败'}")
            
            # 批量处理
            timestamps_dir = "/home/isakeem/Code/subtitle-storage-service/scripts/.output/vad"
            if Path(timestamps_dir).exists():
                results = processor.process_batch_timestamps(timestamps_dir)
                print(f"📁 批量处理结果: {len(results)} 个文件")
        
        print("🔒 数据库连接已关闭")
        
    except Exception as e:
        print(f"❌ 高级用法示例失败: {e}")

def check_database_status():
    """检查数据库状态和VAD字段"""
    print("\n=== 数据库状态检查 ===")
    
    try:
        with get_db_connection() as db:
            # 检查audio_tasks表的VAD字段
            vad_fields_query = """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'audio_tasks' 
            AND column_name LIKE 'vad_%'
            ORDER BY column_name
            """
            
            vad_fields = db.execute_query(vad_fields_query)
            print(f"🔍 audio_tasks表VAD字段数: {len(vad_fields)}")
            
            for field in vad_fields:
                nullable = "NULL" if field['is_nullable'] == 'YES' else "NOT NULL"
                print(f"  📋 {field['column_name']}: {field['data_type']} ({nullable})")
            
            # 检查segments表的VAD字段
            segments_vad_query = """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'segments' 
            AND column_name IN ('speech_confidence', 'rms', 'peak_amplitude', 'vad_segment_file_path')
            ORDER BY column_name
            """
            
            segments_fields = db.execute_query(segments_vad_query)
            print(f"\n🔍 segments表VAD字段数: {len(segments_fields)}")
            
            for field in segments_fields:
                nullable = "NULL" if field['is_nullable'] == 'YES' else "NOT NULL"
                print(f"  📋 {field['column_name']}: {field['data_type']} ({nullable})")
            
            # 检查有多少任务已有VAD数据
            vad_data_count = db.execute_query("""
                SELECT 
                    COUNT(*) as total_tasks,
                    COUNT(vad_run_id) as tasks_with_vad_data,
                    COUNT(vad_completed_at) as tasks_with_vad_completed
                FROM audio_tasks
            """)
            
            if vad_data_count:
                stats = vad_data_count[0]
                print(f"\n📊 VAD数据统计:")
                print(f"  📝 总任务数: {stats['total_tasks']}")
                print(f"  🎯 有VAD数据的任务: {stats['tasks_with_vad_data']}")
                print(f"  ✅ VAD已完成的任务: {stats['tasks_with_vad_completed']}")
            
    except Exception as e:
        print(f"❌ 数据库状态检查失败: {e}")

def main():
    """主函数 - 运行所有示例"""
    print("🚀 VAD数据处理工具使用示例")
    print("=" * 50)
    
    # 1. 测试数据库连接
    print("1️⃣ 测试数据库连接...")
    if not test_database_connection():
        print("❌ 数据库连接失败，无法继续")
        return
    
    # 2. 检查数据库状态
    check_database_status()
    
    # 3. 单文件处理示例
    try:
        example_single_file_processing()
    except Exception as e:
        print(f"❌ 单文件处理示例失败: {e}")
    
    # 4. 批量处理示例
    try:
        example_batch_processing()
    except Exception as e:
        print(f"❌ 批量处理示例失败: {e}")
    
    # 5. 自定义映射示例
    try:
        example_with_custom_mapping()
    except Exception as e:
        print(f"❌ 自定义映射示例失败: {e}")
    
    # 6. 高级用法示例
    try:
        example_advanced_usage()
    except Exception as e:
        print(f"❌ 高级用法示例失败: {e}")
    
    print("\n🎉 示例运行完成")

if __name__ == "__main__":
    main()
