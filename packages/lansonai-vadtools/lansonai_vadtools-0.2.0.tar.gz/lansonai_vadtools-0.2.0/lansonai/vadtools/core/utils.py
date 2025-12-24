import os
import json
import glob
import shutil
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import re

def get_current_time() -> str:
    """获取当前时间，格式 YYYY/MM/DD HH:mm:ss"""
    return datetime.now().strftime("%Y/%m/%d %H:%M:%S")

def log_message(message: str, level: str = "INFO") -> None:
    """记录日志消息，格式 [时间] 消息"""
    current_time = get_current_time()
    # 只在非INFO级别时显示级别
    if level != "INFO":
        print(f"[{current_time}] {level} - {message}", flush=True)
    else:
        print(f"[{current_time}] {message}", flush=True)

# 延迟导入settings，避免循环导入
def _get_temp_dir():
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent.parent))
    from lansonai.vadtools.config.settings import TEMP_DIR
    return TEMP_DIR

def _get_output_dir():
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent.parent))
    from lansonai.vadtools.config.settings import OUTPUT_DIR
    return OUTPUT_DIR

def save_timestamps(
    segments: List[Dict[str, Any]], 
    timestamps_path: Path,
    request_id: str = "",
    audio_segments: List[Dict[str, Any]] = None,
    overall_speech_ratio: float = 0.0,
    source_file: str = "",
    vad_parameters: Dict[str, Any] = None,
    performance_data: Dict[str, Any] = None,
    total_audio_duration: float = 0.0,
    output_format: str = "wav"
) -> Dict[str, Any]:
    """
    保存完整的VAD分析结果到JSON文件，使用期望的JSON结构格式
    返回保存的完整数据结构，供API直接使用
    """
    current_time = get_current_time()
    output_dir = timestamps_path.parent
    
    # 确保输出目录存在和可写
    os.makedirs(output_dir, exist_ok=True)
    if not os.access(output_dir, os.R_OK | os.W_OK | os.X_OK):
        raise PermissionError(f"时间戳输出目录 {output_dir} 权限不足")
    
    # 如果传入的 request_id 为空，则使用输出目录名称作为 request_id
    if not request_id:
        request_id = output_dir.name if output_dir.parent == _get_output_dir() else "unknown"
    log_message(f"保存时间戳到 {timestamps_path} (request_id: {request_id})")
    
    try:
        # 准备默认值
        if audio_segments is None:
            audio_segments = []
        if vad_parameters is None:
            vad_parameters = {}
        if performance_data is None:
            performance_data = {}
        
        # 计算统计信息
        total_speech_duration = sum(seg.get('duration', 0) for seg in segments)
        num_segments = len(segments)
        
        # 检查分片数量限制
        if num_segments > 1000:
            raise ValueError(f"检测到 {num_segments} 个语音分片，超过1000个限制。音频可能需要预处理。")
        
        # --- 正确构建数据结构 ---
        
        # 1. metadata
        metadata = {
            "source_file": source_file,
            "run_id": request_id,
            "processing_date": current_time,
            "parameters": {
                "threshold": vad_parameters.get("threshold", 0.3),
                "min_speech_duration_ms": int(vad_parameters.get("min_segment_duration", 0.3) * 1000),
                "speech_pad_ms": int(vad_parameters.get("speech_pad_ms", 100)),
                "min_silence_duration_ms": int(vad_parameters.get("max_merge_gap", 0.0) * 1000)
            }
        }
        
        # 2. performance (top-level)
        performance = {
            "total_processing_time": performance_data.get("total_processing_time", 0.0),
            "audio_loading_time": performance_data.get("audio_loading_time", 0.0),
            "stage1_vad_timestamps_time": performance_data.get("stage1_vad_timestamps_time", 0.0),
            "stage2_feature_extraction_time": performance_data.get("stage2_feature_extraction_time", 0.0),
            "speed_ratio": performance_data.get("speed_ratio", 0.0)
        }
        
        # 3. summary (top-level)
        summary = {
            "total_duration": total_audio_duration,
            "total_speech_duration": total_speech_duration,
            "overall_speech_ratio": overall_speech_ratio,
            "num_segments": num_segments
        }
        
        # 4. segments (top-level)
        processed_segments = []
        audio_segments_dict = {seg.get("start_time"): seg for seg in audio_segments}
        
        # 构建segments目录路径
        segments_dir = output_dir / "segments"
        
        for i, seg in enumerate(segments):
            start_time = seg.get('start_time', 0.0)
            audio_seg = audio_segments_dict.get(start_time, {})
            
            # 手动拼接source_url路径：根据输出目录、request_id和segment编号
            # 文件命名格式：segment_{i+1:03d}.{format} (与export_segments保持一致)
            segment_filename = f"segment_{i+1:03d}.{output_format}"
            segment_file_path = segments_dir / segment_filename
            source_url = str(segment_file_path.resolve())
            
            segment_data = {
                "id": i,  # 0-indexed ID
                "source_url": source_url,  # 使用source_url字段，手动拼接的完整绝对路径
                "start_time": start_time,
                "end_time": seg.get('end_time', 0.0),
                "duration": seg.get('duration', 0.0),
                "speech_confidence": seg.get('speech_confidence', audio_seg.get('speech_confidence', 0.8)),
                "rms": seg.get('rms', audio_seg.get('rms', 0.0)),
                "peak_amplitude": seg.get('peak_amplitude', audio_seg.get('peak_amplitude', 0.0)),
            }
            processed_segments.append(segment_data)

        # 5. Assemble the final dictionary
        timestamps_data = {
            "metadata": metadata,
            "performance": performance,
            "request_id": request_id,
            "original_filename": Path(source_file).name,
            "timestamps_path": str(timestamps_path),
            "total_segments": num_segments,
            "total_duration": total_audio_duration,
            "audio_segments": processed_segments,
            "summary": summary,
            "segments": processed_segments
        }
        
        # --- 结构构建结束 ---
        
        # 写入JSON文件
        with open(timestamps_path, 'w', encoding='utf-8') as f:
            json.dump(timestamps_data, f, indent=2, ensure_ascii=False)
        
        # 验证保存
        if not timestamps_path.exists() or timestamps_path.stat().st_size == 0:
            raise ValueError("时间戳文件保存失败或为空")
        
        file_size = timestamps_path.stat().st_size
        log_message(f"完整VAD结果保存成功，大小: {file_size} bytes, 段数: {len(segments)} (request_id: {request_id})")
        
        # 返回保存的完整数据结构
        return timestamps_data
        
    except Exception as e:
        log_message(f"保存时间戳失败 {timestamps_path}: {str(e)} (request_id: {request_id})", "ERROR")
        # 清理失败的文件
        if timestamps_path.exists():
            timestamps_path.unlink(missing_ok=True)
        raise

def cleanup_temp_files(temp_dir: Path, request_id: str, max_age_hours: int = 24) -> int:
    """
    清理临时目录中的文件，支持按request_id清理 .temp/vad/{request_id}* 模式
    包括所有以 request_id 开头的文件和相关子目录
    """
    current_time = get_current_time()
    cleaned_count = 0
    
    if not temp_dir.exists():
        log_message(f"临时目录不存在: {temp_dir}")
        return cleaned_count
    
    if not request_id:
        log_message(f"cleanup_temp_files 缺少 request_id，跳过特定清理", "WARNING")
        return 0
    
    # 增强清理：查找所有以 request_id 开头的文件和目录
    # 模式1: 直接文件 request_id.*
    pattern_files = temp_dir / f"{request_id}.*"
    files_to_delete = glob.glob(str(pattern_files))
    
    # 模式2: 包含 request_id 的文件名 (如 request_id_audio.wav)
    all_files = list(temp_dir.rglob("*"))
    request_id_files = [f for f in all_files if f.is_file() and re.match(rf".*{re.escape(request_id)}.*", f.name)]
    
    # 模式3: request_id 子目录及其内容
    request_id_dirs = [d for d in temp_dir.iterdir() if d.is_dir() and d.name == request_id]
    dir_files = []
    for req_dir in request_id_dirs:
        dir_files.extend(list(req_dir.rglob("*")))
    
    all_to_delete = files_to_delete + request_id_files + dir_files
    
    # 去重并清理
    unique_paths = list(set(str(p) for p in all_to_delete))
    
    for file_path_str in unique_paths:
        try:
            path_obj = Path(file_path_str)
            if path_obj.exists():
                if path_obj.is_file():
                    path_obj.unlink(missing_ok=True)
                elif path_obj.is_dir():
                    shutil.rmtree(path_obj, ignore_errors=True)
                cleaned_count += 1
                log_message(f"清理临时文件/目录: {path_obj.name} (request_id: {request_id})")
        except Exception as e:
            log_message(f"清理 {file_path_str} 失败: {str(e)} (request_id: {request_id})", "WARNING")
            continue
    
    # 如果没有特定request_id，清理过期文件
    if not request_id or cleaned_count == 0:
        now = datetime.now()
        cutoff_time = now.timestamp() - (max_age_hours * 3600)
        
        for file_path in temp_dir.iterdir():
            if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                try:
                    file_path.unlink(missing_ok=True)
                    cleaned_count += 1
                    age_hours = (now - datetime.fromtimestamp(file_path.stat().st_mtime)).total_seconds() / 3600
                    log_message(f"清理过期临时文件: {file_path.name} (年龄: {age_hours:.1f}h)")
                except Exception as e:
                    log_message(f"清理过期文件失败 {file_path}: {str(e)}", "WARNING")
                    continue
    
    log_message(f"临时文件清理完成，共清理 {cleaned_count} 个文件/目录 (request_id: {request_id or 'all'})")
    return cleaned_count

def cleanup_output_directory(output_dir: Path, max_age_days: int = 7) -> int:
    """
    清理输出目录中的过期结果 (按request_id目录)，用于定期维护
    """
    current_time = get_current_time()
    cleaned_dirs = 0
    
    if not output_dir.exists():
        log_message(f"输出目录不存在: {output_dir}")
        return cleaned_dirs
    
    now = datetime.now()
    cutoff_time = now.timestamp() - (max_age_days * 24 * 3600)
    
    for dir_path in output_dir.iterdir():
        if dir_path.is_dir():
            # 检查目录内最新文件修改时间
            try:
                all_files = list(dir_path.rglob("*"))
                if not all_files:
                    dir_mtime = dir_path.stat().st_mtime
                else:
                    dir_mtime = max(f.stat().st_mtime for f in all_files if f.is_file())
                
                if dir_mtime < cutoff_time:
                    shutil.rmtree(dir_path, ignore_errors=True)
                    cleaned_dirs += 1
                    age_days = (now - datetime.fromtimestamp(dir_mtime)).total_seconds() / (24 * 3600)
                    log_message(f"清理过期输出目录: {dir_path.name} (年龄: {age_days:.1f}天)")
            except Exception as e:
                log_message(f"检查/清理输出目录 {dir_path} 失败: {str(e)}", "WARNING")
                continue
    
    log_message(f"[{current_time}] INFO - 输出目录清理完成，共清理 {cleaned_dirs} 个目录", "INFO")
    return cleaned_dirs

def validate_directories() -> Dict[str, bool]:
    """
    验证目录状态，返回详细可用性报告
    """
    current_time = get_current_time()
    temp_dir = _get_temp_dir()
    output_dir = _get_output_dir()
    report = {
        "temp_dir": {"path": str(temp_dir), "exists": False, "readable": False, "writable": False, "executable": False},
        "output_dir": {"path": str(output_dir), "exists": False, "readable": False, "writable": False, "executable": False}
    }
    
    # 检查临时目录
    if temp_dir.exists():
        report["temp_dir"]["exists"] = True
        report["temp_dir"]["readable"] = os.access(temp_dir, os.R_OK)
        report["temp_dir"]["writable"] = os.access(temp_dir, os.W_OK)
        report["temp_dir"]["executable"] = os.access(temp_dir, os.X_OK)
    
    # 检查输出目录
    if output_dir.exists():
        report["output_dir"]["exists"] = True
        report["output_dir"]["readable"] = os.access(output_dir, os.R_OK)
        report["output_dir"]["writable"] = os.access(output_dir, os.W_OK)
        report["output_dir"]["executable"] = os.access(output_dir, os.X_OK)
    
    # 记录报告
    temp_ok = report['temp_dir']['exists'] and all(report['temp_dir'][p] for p in ['readable', 'writable', 'executable'])
    output_ok = report['output_dir']['exists'] and all(report['output_dir'][p] for p in ['readable', 'writable', 'executable'])
    log_message(f"目录验证报告: temp_dir_ok={temp_ok}, output_dir_ok={output_ok}")
    
    return report

def generate_request_id(audio_file_path: str = "") -> str:
    """
    生成基于音频文件MD5哈希的请求ID
    如果没有提供音频文件路径，则使用UUID4作为后备方案
    """
    if audio_file_path:
        try:
            import hashlib
            with open(audio_file_path, 'rb') as f:
                file_hash = hashlib.md5()
                # 读取文件的前8KB来计算哈希，避免大文件处理过慢
                while chunk := f.read(8192):
                    file_hash.update(chunk)
                return file_hash.hexdigest()
        except Exception:
            # 如果文件读取失败，回退到UUID4
            pass
    
    # 如果没有提供音频文件路径或文件读取失败，使用UUID4
    import uuid
    return str(uuid.uuid4())