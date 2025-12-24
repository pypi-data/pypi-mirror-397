"""
VAD数据处理和数据库写入工具
基于timestamps.json文件将VAD分析结果写入数据库
"""

import json
import uuid
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
import logging
import statistics

import sys
from pathlib import Path
# 将项目根目录加入 sys.path，以便能够直接导入 db_connection
sys.path.append(str(Path(__file__).parent.parent))
try:
    from db_connection import DatabaseConnection, get_db_connection
except ImportError:
    # 作为后备，仍尝试相对导入（在本地开发环境中可能需要）
    from .db_connection import DatabaseConnection, get_db_connection

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VADDataProcessor:
    """VAD数据处理器"""
    
    def __init__(self, db_connection: Optional[DatabaseConnection] = None):
        """
        初始化VAD数据处理器
        
        Args:
            db_connection: 数据库连接实例，如果为None则自动创建
        """
        self.db = db_connection or get_db_connection()
        self._should_close_db = db_connection is None
    
    def process_timestamps_file(self, timestamps_file_path: str, task_id: str) -> bool:
        """
        处理timestamps.json文件并写入数据库
        
        Args:
            timestamps_file_path: timestamps.json文件路径
            task_id: 对应的任务ID
            
        Returns:
            是否处理成功
        """
        try:
            # 读取timestamps.json文件
            timestamps_data = self._load_timestamps_file(timestamps_file_path)
            
            # 验证数据格式
            if not self._validate_timestamps_data(timestamps_data):
                logger.error(f"timestamps.json数据格式无效: {timestamps_file_path}")
                return False
            
            # 检查任务是否存在
            task_exists = self._check_task_exists(task_id)
            if not task_exists:
                logger.warning(f"任务 {task_id} 不存在，将尝试创建新任务。")
            
            # 处理并写入数据
            success = self._process_and_save_data(timestamps_data, task_id)
            
            if success:
                logger.info(f"VAD数据处理成功: {task_id}")
            else:
                logger.error(f"VAD数据处理失败: {task_id}")
                
            return success
            
        except Exception as e:
            logger.error(f"处理timestamps文件时发生异常: {e}")
            return False
    
    def _load_timestamps_file(self, file_path: str) -> Dict[str, Any]:
        """加载timestamps.json文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"成功加载timestamps文件: {file_path}")
            return data
        except Exception as e:
            logger.error(f"加载timestamps文件失败: {e}")
            raise
    
    def _validate_timestamps_data(self, data: Dict[str, Any]) -> bool:
        """验证timestamps数据格式"""
        required_keys = ['request_id', 'total_segments', 'total_duration', 'timestamps_path', 'audio_segments', 'original_filename']
        
        # 检查顶级键
        for key in required_keys:
            if key not in data:
                logger.error(f"缺少必需的键: {key}")
                return False
        
        # 检查必需字段是否为空或无效
        validation_errors = self._validate_required_fields(data)
        if validation_errors:
            for error in validation_errors:
                logger.error(f"字段验证失败: {error}")
            return False
        
        # 检查audio_segments
        audio_segments = data['audio_segments']
        if not isinstance(audio_segments, list) or len(audio_segments) == 0:
            logger.error("audio_segments必须是非空列表")
            return False

        # 检查第一个audio_segment的格式 (AudioSegment)
        audio_segment = audio_segments[0]
        audio_segment_required = ['start_time', 'end_time', 'duration', 'file_path', 'rms', 'peak_amplitude', 'speech_confidence']
        for key in audio_segment_required:
            if key not in audio_segment:
                logger.error(f"AudioSegment缺少必需的键: {key}")
                return False
        
        logger.info("timestamps数据格式验证通过")
        return True
    
    def _validate_required_fields(self, data: Dict[str, Any]) -> List[str]:
        """验证必需字段是否为空或无效"""
        errors = []
        
        # 验证 original_filename
        original_filename = data.get('original_filename')
        if not original_filename or not isinstance(original_filename, str) or original_filename.strip() == '':
            errors.append("original_filename 不能为空且必须是有效的字符串")
        
        # 验证 request_id
        request_id = data.get('request_id')
        if not request_id or not isinstance(request_id, str) or request_id.strip() == '':
            errors.append("request_id 不能为空且必须是有效的字符串")
        
        # 验证 total_segments
        total_segments = data.get('total_segments')
        if not isinstance(total_segments, int) or total_segments < 0:
            errors.append("total_segments 必须是非负整数")
        
        # 验证 total_duration
        total_duration = data.get('total_duration')
        if not isinstance(total_duration, (int, float)) or total_duration < 0:
            errors.append("total_duration 必须是非负数")
        
        # 验证 metadata 结构
        metadata = data.get('metadata', {})
        if not isinstance(metadata, dict):
            errors.append("metadata 必须是字典类型")
        else:
            # 验证 metadata 中的必需字段
            required_metadata_fields = ["source_file", "run_id", "processing_date"]
            for field in required_metadata_fields:
                if field not in metadata:
                    errors.append(f"metadata 中缺少必需字段: {field}")
        
        return errors
    
    def _check_task_exists(self, task_id: str) -> bool:
        """检查任务是否存在"""
        try:
            if not self.db.connection:
                self.db.connect()
                
            result = self.db.execute_query(
                "SELECT task_id FROM audio_tasks WHERE task_id = %s",
                (task_id,)
            )
            exists = len(result) > 0
            logger.info(f"任务存在检查: {task_id} -> {exists}")
            return exists
        except Exception as e:
            logger.error(f"检查任务存在性失败: {e}")
            return False
    
    def _process_and_save_data(self, data: Dict[str, Any], task_id: str) -> bool:
        """处理并保存VAD数据到数据库"""
        try:
            if not self.db.connection:
                self.db.connect()
            
            # 预处理数据，确保所有必需字段都有有效值
            processed_data = self._preprocess_data(data)
            
            operations = []
            
            # 检查任务是否存在，决定是插入还是更新
            task_exists = self._check_task_exists(task_id)
            
            if task_exists:
                # 任务存在，准备更新操作
                audio_tasks_op = self._prepare_audio_tasks_update(processed_data, task_id)
            else:
                # 任务不存在，准备插入操作
                audio_tasks_op = self._prepare_audio_tasks_insert(processed_data, task_id)
            
            operations.append(audio_tasks_op)
            
            success = self.db.execute_transaction(operations)
            
            if success:
                logger.info(f"VAD数据保存成功: task_id={task_id}, operations={len(operations)}")
            
            return success
            
        except Exception as e:
            logger.error(f"保存VAD数据失败: {e}")
            return False
    
    def _prepare_audio_tasks_insert(self, data: Dict[str, Any], task_id: str) -> Tuple[str, Tuple]:
        """准备audio_tasks表的插入SQL"""
        metadata = data['metadata']
        performance = data['performance']
        summary = data['summary']
        audio_segments = data['audio_segments']

        avg_speech_confidence = statistics.mean([s['speech_confidence'] for s in audio_segments]) if audio_segments else 0.0
        avg_rms = statistics.mean([s['rms'] for s in audio_segments]) if audio_segments else 0.0
        avg_peak_amplitude = statistics.mean([s['peak_amplitude'] for s in audio_segments]) if audio_segments else 0.0
        processing_date = self._parse_processing_date(metadata['processing_date'])
        
        # 获取段数，从顶层字段获取
        num_segments = data.get('total_segments', len(audio_segments))
        # 计算平均段时长
        avg_segment_duration = summary['total_speech_duration'] / num_segments if num_segments > 0 else 0
        # 获取语音比例，从顶层字段获取
        overall_speech_ratio = data.get('summary', {}).get('overall_speech_ratio', 0.0)
        # 获取原始文件名，从顶层字段获取
        original_filename = data.get('original_filename', '')
        # 获取存储路径，从第一个音频片段的 file_path 或 source_url 获取
        # 如果都为空，则使用 metadata.source_file 作为备选
        storage_path = ''
        if audio_segments:
            first_segment = audio_segments[0]
            storage_path = first_segment.get('file_path', '') or first_segment.get('source_url', '')
        if not storage_path:
            storage_path = metadata.get('source_file', '')

        compact_segments = [
            {
                'id': s['id'],
                'start_time': s['start_time'],
                'end_time': s['end_time'],
                'duration': s['duration'],
                'speech_confidence': s['speech_confidence'],
                'rms': s['rms'],
                'peak_amplitude': s['peak_amplitude'],
                'file_path': s.get('file_path')
            }
            for s in audio_segments
        ]

        # 使用字典来管理数据，确保字段和值的对应关系
        data_to_insert = {
            "task_id": task_id,
            "original_filename": original_filename,
            "storage_path": storage_path,
            "vad_total_processing_time": performance['total_processing_time'],
            "vad_audio_loading_time": performance['audio_loading_time'],
            "vad_stage1_time": performance['stage1_vad_timestamps_time'],
            "vad_stage2_time": performance['stage2_feature_extraction_time'],
            "vad_speed_ratio": performance['speed_ratio'],
            "vad_run_id": metadata['run_id'],
            "vad_source_file_path": metadata['source_file'],
            "vad_total_speech_duration": summary['total_speech_duration'],
            "vad_avg_speech_confidence": avg_speech_confidence,
            "vad_avg_rms": avg_rms,
            "vad_avg_peak_amplitude": avg_peak_amplitude,
            "vad_segment_count": num_segments,
            "vad_speech_ratio": overall_speech_ratio,
            "vad_avg_segment_duration": avg_segment_duration,
            "vad_completed_at": processing_date,
            "vad_current_params": json.dumps(metadata['parameters']),
            "vad_segments_content": json.dumps(compact_segments),
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "duration_seconds": data.get("total_duration", 0.0),
            "started_at": datetime.now(),
            "file_size": self._get_file_size(metadata.get("source_file", ""))
        }
        
        # 动态生成SQL语句
        columns = list(data_to_insert.keys())
        placeholders = ["%s"] * len(columns)
        
        sql = f"""
        INSERT INTO audio_tasks ({', '.join(columns)})
        VALUES ({', '.join(placeholders)})
        """
        
        # 从字典的值生成参数元组
        params = tuple(data_to_insert.values())
        
        return (sql, params)


    def _prepare_audio_tasks_update(self, data: Dict[str, Any], task_id: str) -> Tuple[str, Tuple]:
        """准备audio_tasks表的更新SQL"""
        metadata = data['metadata']
        performance = data['performance']
        summary = data['summary']
        audio_segments = data['audio_segments']
        
        # 计算audio_segments的平均值
        avg_speech_confidence = statistics.mean([s['speech_confidence'] for s in audio_segments]) if audio_segments else 0.0
        avg_rms = statistics.mean([s['rms'] for s in audio_segments]) if audio_segments else 0.0
        avg_peak_amplitude = statistics.mean([s['peak_amplitude'] for s in audio_segments]) if audio_segments else 0.0
        
        # 解析处理日期
        processing_date = self._parse_processing_date(metadata['processing_date'])
        
        # 获取段数，从顶层字段获取
        num_segments = data.get('total_segments', len(audio_segments))
        # 计算平均段时长
        avg_segment_duration = summary['total_speech_duration'] / num_segments if num_segments > 0 else 0
        # 获取语音比例，从顶层字段获取
        overall_speech_ratio = data.get('overall_speech_ratio') or summary.get('overall_speech_ratio', 0.0)
        
        # 精简存储的audio_segments，避免冗余键
        compact_segments = [
            {
                'id': s['id'],
                'start_time': s['start_time'],
                'end_time': s['end_time'],
                'duration': s['duration'],
                'speech_confidence': s['speech_confidence'],
                'rms': s['rms'],
                'peak_amplitude': s['peak_amplitude'],
                'file_path': s.get('file_path')
            }
            for s in audio_segments
        ]
        
        # 使用字典来管理数据，确保字段和值的对应关系
        data_to_update = {
            "vad_total_processing_time": performance['total_processing_time'],
            "vad_audio_loading_time": performance['audio_loading_time'],
            "vad_stage1_time": performance['stage1_vad_timestamps_time'],
            "vad_stage2_time": performance['stage2_feature_extraction_time'],
            "vad_speed_ratio": performance['speed_ratio'],
            "vad_run_id": metadata['run_id'],
            "vad_source_file_path": metadata['source_file'],
            "vad_total_speech_duration": summary['total_speech_duration'],
            "vad_avg_speech_confidence": avg_speech_confidence,
            "vad_avg_rms": avg_rms,
            "vad_avg_peak_amplitude": avg_peak_amplitude,
            "vad_segment_count": num_segments,
            "vad_speech_ratio": overall_speech_ratio,
            "vad_avg_segment_duration": avg_segment_duration,
            "vad_completed_at": processing_date,
            "vad_current_params": json.dumps(metadata['parameters']),
            "vad_segments_content": json.dumps(compact_segments)
        }
        
        # 动态生成UPDATE语句
        set_clauses = [f"{col} = %s" for col in data_to_update.keys()]
        set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        
        sql = f"""
        UPDATE audio_tasks SET
            {', '.join(set_clauses)}
        WHERE task_id = %s
        """
        
        # 从字典的值生成参数元组，加上WHERE条件的task_id
        params = tuple(list(data_to_update.values()) + [task_id])
        
        return (sql, params)

    
    def _get_subtitle_id_for_task(self, task_id: str) -> Optional[str]:
        """获取任务对应的subtitle_id"""
        try:
            result = self.db.execute_query(
                "SELECT subtitle_id FROM audio_tasks WHERE task_id = %s",
                (task_id,)
            )
            if result and result[0]['subtitle_id']:
                subtitle_id = result[0]['subtitle_id']
                logger.info(f"找到subtitle_id: {subtitle_id} for task: {task_id}")
                return subtitle_id
            else:
                logger.info(f"任务 {task_id} 暂无关联的subtitle_id")
                return None
        except Exception as e:
            logger.error(f"获取subtitle_id失败: {e}")
            return None
    
    def _prepare_segments_updates(self, data: Dict[str, Any], subtitle_id: str) -> List[Tuple[str, Tuple]]:
        """准备segments表的更新SQL列表"""
        audio_segments = data['audio_segments']
        operations = []
        
        for audio_segment in audio_segments:
            sql = """
            UPDATE segments SET
                speech_confidence = %s,
                rms = %s,
                peak_amplitude = %s,
                vad_segment_file_path = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE subtitle_id = %s
            AND seq_index = %s
            """
            
            params = (
                audio_segment['speech_confidence'],
                audio_segment['rms'],
                audio_segment['peak_amplitude'],
                audio_segment['file_path'],
                subtitle_id,
                audio_segment['id']
            )
            
            operations.append((sql, params))
        
        logger.info(f"准备更新 {len(operations)} 个segments记录")
        return operations
    
    def _get_file_size(self, file_path: str) -> Optional[int]:
        """获取文件大小（字节）"""
        try:
            if file_path and Path(file_path).exists():
                return Path(file_path).stat().st_size
            return None
        except Exception as e:
            logger.warning(f"获取文件大小失败 {file_path}: {e}")
            return None
    
    def _parse_processing_date(self, date_str: str) -> datetime:
        """解析处理日期字符串"""
        try:
            # 格式: "2025/09/13 03:01:07"
            return datetime.strptime(date_str, "%Y/%m/%d %H:%M:%S")
        except Exception as e:
            logger.warning(f"解析日期失败，使用当前时间: {e}")
            return datetime.now()
    
    def process_batch_timestamps(self, timestamps_dir: str, task_mapping: Optional[Dict[str, str]] = None) -> Dict[str, bool]:
        """
        批量处理timestamps文件
        
        Args:
            timestamps_dir: timestamps文件目录
            task_mapping: run_id到task_id的映射，如果为None则尝试从文件名推断
            
        Returns:
            处理结果字典 {run_id: success}
        """
        results = {}
        timestamps_dir_path = Path(timestamps_dir)
        
        if not timestamps_dir_path.exists():
            logger.error(f"目录不存在: {timestamps_dir}")
            return results
        
        # 查找所有timestamps.json文件
        timestamps_files = list(timestamps_dir_path.glob("*/timestamps.json"))
        logger.info(f"发现 {len(timestamps_files)} 个timestamps文件")
        
        for file_path in timestamps_files:
            try:
                # 从目录名获取run_id
                run_id = file_path.parent.name
                
                # 获取对应的task_id
                if task_mapping and run_id in task_mapping:
                    task_id = task_mapping[run_id]
                else:
                    # 尝试从run_id推断task_id（假设它们相同）
                    task_id = run_id
                
                logger.info(f"处理文件: {file_path}, run_id: {run_id}, task_id: {task_id}")
                
                # 处理文件
                success = self.process_timestamps_file(str(file_path), task_id)
                results[run_id] = success
                
            except Exception as e:
                logger.error(f"处理文件失败 {file_path}: {e}")
                results[run_id] = False
        
        # 输出统计结果
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        logger.info(f"批量处理完成: {successful}/{total} 成功")
        
        return results
    
    def __enter__(self):
        """上下文管理器入口"""
        if not self.db.connection:
            self.db.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        if self._should_close_db and self.db.connection:
            self.db.disconnect()
    
    def _preprocess_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """预处理数据，确保所有必需字段都有有效值"""
        processed_data = data.copy()
        
        # 确保 original_filename 有有效值
        if not processed_data.get('original_filename'):
            # 尝试从 metadata.source_file 推导
            source_file = processed_data.get('metadata', {}).get('source_file')
            if source_file:
                from pathlib import Path
                processed_data['original_filename'] = Path(source_file).name
                logger.info(f"从 source_file 推导出 original_filename: {processed_data['original_filename']}")
            else:
                # 如果无法推导，使用 request_id 作为后备
                request_id = processed_data.get('request_id', 'unknown')
                processed_data['original_filename'] = f"{request_id}.audio"
                logger.warning(f"无法推导 original_filename，使用后备值: {processed_data['original_filename']}")
        
        
        # 确保 total_segments 有有效值
        if 'total_segments' not in processed_data or processed_data['total_segments'] is None:
            audio_segments = processed_data.get('audio_segments', [])
            processed_data['total_segments'] = len(audio_segments)
            logger.info(f"从 audio_segments 推导出 total_segments: {processed_data['total_segments']}")
        
        return processed_data


def process_single_timestamps_file(timestamps_file_path: str, task_id: str) -> bool:
    """
    处理单个timestamps文件的便捷函数
    
    Args:
        timestamps_file_path: timestamps.json文件路径
        task_id: 对应的任务ID
        
    Returns:
        是否处理成功
    """
    with VADDataProcessor() as processor:
        return processor.process_timestamps_file(timestamps_file_path, task_id)


def process_batch_timestamps_files(timestamps_dir: str, task_mapping: Optional[Dict[str, str]] = None) -> Dict[str, bool]:
    """
    批量处理timestamps文件的便捷函数
    
    Args:
        timestamps_dir: timestamps文件目录
        task_mapping: run_id到task_id的映射
        
    Returns:
        处理结果字典
    """
    with VADDataProcessor() as processor:
        return processor.process_batch_timestamps(timestamps_dir, task_mapping)


if __name__ == "__main__":
    # 示例用法
    import sys
    
    if len(sys.argv) < 3:
        print("用法: python vad_data_processor.py <timestamps_file_path> <task_id>")
        print("或者: python vad_data_processor.py --batch <timestamps_dir>")
        sys.exit(1)
    
    if sys.argv[1] == "--batch":
        # 批量处理
        timestamps_dir = sys.argv[2]
        results = process_batch_timestamps_files(timestamps_dir)
        
        print("\n处理结果:")
        for run_id, success in results.items():
            status = "✅ 成功" if success else "❌ 失败"
            print(f"  {run_id}: {status}")
    else:
        # 单文件处理
        timestamps_file = sys.argv[1]
        task_id = sys.argv[2]
        
        success = process_single_timestamps_file(timestamps_file, task_id)
        if success:
            print("✅ VAD数据处理成功")
        else:
            print("❌ VAD数据处理失败")
