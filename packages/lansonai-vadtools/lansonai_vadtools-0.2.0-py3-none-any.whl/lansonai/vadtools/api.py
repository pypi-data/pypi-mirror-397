"""
VAD 分析 API
提供 analyze() 函数作为包的主要入口
"""

import sys
import time
import warnings
from pathlib import Path
from typing import Optional, Dict, Any, Literal
import torch
import librosa
import numpy as np

# 抑制常见的警告信息
warnings.filterwarnings('ignore', category=UserWarning, message='.*PySoundFile.*')
warnings.filterwarnings('ignore', category=FutureWarning, message='.*__audioread_load.*')
warnings.filterwarnings('ignore', category=FutureWarning, message='.*librosa.*')

# 添加项目路径以导入核心模块
# lansonai/vadtools/api.py 位于 lansonai/vadtools/ 目录下
_project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_project_root))

from lansonai.vadtools.config.settings import SAMPLE_RATE
from lansonai.vadtools.core.vad_detector import detect_vad_segments, export_segments as export_audio_segments
from lansonai.vadtools.core.utils import log_message, save_timestamps, generate_request_id
from lansonai.vadtools.core.audio_processor import process_audio_file_path, extract_audio_from_video, is_video_file


def load_vad_model():
    """加载Silero VAD模型"""
    try:
        log_message("Loading Silero VAD model from torch.hub...")
        model, utils = torch.hub.load(
            repo_or_dir='snakers4/silero-vad', 
            model='silero_vad', 
            force_reload=False, 
            onnx=False, 
            verbose=False
        )
        get_speech_timestamps = utils[0]
        log_message("Silero VAD model loaded successfully")
        return model, get_speech_timestamps
    except Exception as e:
        error_msg = f"Failed to load VAD model: {str(e)}"
        log_message(error_msg, "ERROR")
        import traceback
        log_message(f"Error traceback: {traceback.format_exc()}", "ERROR")
        raise RuntimeError(error_msg)


def analyze(
    input_path: str | Path,
    output_dir: str | Path,
    threshold: float = 0.3,
    min_segment_duration: float = 0.5,
    max_merge_gap: float = 0.2,
    export_segments: bool = True,
    output_format: Literal["wav", "flac"] = "wav",
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    分析音频/视频文件的语音活动
    
    Args:
        input_path: 输入音频或视频文件路径
        output_dir: 输出目录（调用方保证存在）
        threshold: VAD检测阈值 (0.0-1.0)
        min_segment_duration: 最小音频段长度(秒)
        max_merge_gap: 最大合并间隔(秒)
        export_segments: 是否导出音频片段
        output_format: 输出格式 ("wav" 或 "flac")
        request_id: 请求ID，如果为None会自动生成
    
    Returns:
        Dict包含分析结果，包括：
        - request_id: 请求ID
        - input_file: 输入文件路径
        - output_dir: 输出目录路径
        - json_path: VAD JSON 文件路径
        - segments_dir: 切片文件目录路径（如果导出）
        - segments: VAD片段列表
        - summary: 统计信息
        - performance: 性能指标
        - metadata: 元数据
    
    Raises:
        FileNotFoundError: 输入文件不存在
        RuntimeError: VAD处理失败
    """
    # 转换路径类型
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    
    # 验证输入文件
    if not input_path.exists():
        error_msg = f"Input file not found: {input_path}"
        log_message(error_msg, "ERROR")
        raise FileNotFoundError(error_msg)
    
    if not input_path.is_file():
        error_msg = f"Input path is not a file: {input_path}"
        log_message(error_msg, "ERROR")
        raise ValueError(error_msg)
    
    # 生成请求ID
    if not request_id:
        request_id = generate_request_id(str(input_path))
        log_message(f"Generated request ID: {request_id}")
    else:
        log_message(f"Using provided request ID: {request_id}")
    
    # 创建输出目录结构
    try:
        request_output_dir = output_dir / request_id
        request_output_dir.mkdir(parents=True, exist_ok=True)
        log_message(f"Output directory created: {request_output_dir}")
    except Exception as e:
        error_msg = f"Failed to create output directory {output_dir}: {str(e)}"
        log_message(error_msg, "ERROR")
        raise RuntimeError(error_msg)
    
    log_message("Starting VAD analysis")
    log_message(f"Input file: {input_path}")
    log_message(f"Request ID: {request_id}")
    log_message(f"Output directory: {request_output_dir}")
    log_message(f"Parameters: threshold={threshold}, min_segment_duration={min_segment_duration}, max_merge_gap={max_merge_gap}, export_segments={export_segments}, output_format={output_format}")
    
    overall_start_time = time.time()
    
    # 处理视频文件：提取音频
    audio_path = input_path
    temp_audio_path = None
    if is_video_file(input_path):
        log_message(f"Detected video file: {input_path.suffix}, extracting audio...")
        try:
            temp_audio_path = request_output_dir / f"{request_id}_extracted_audio.wav"
            audio_path = extract_audio_from_video(input_path, temp_audio_path)
            log_message(f"Audio extracted successfully: {audio_path} (size: {audio_path.stat().st_size} bytes)")
        except Exception as e:
            error_msg = f"Failed to extract audio from video {input_path}: {str(e)}"
            log_message(error_msg, "ERROR")
            raise RuntimeError(error_msg)
    
    # 验证音频文件
    try:
        audio_path = process_audio_file_path(audio_path)
    except Exception as e:
        error_msg = f"Audio file validation failed: {str(e)}"
        log_message(error_msg, "ERROR")
        raise
    
    # 加载VAD模型
    vad_model, get_speech_timestamps = load_vad_model()
    
    # 加载音频数据
    try:
        log_message(f"Loading audio data from: {audio_path}")
        audio_loading_start = time.time()
        y, sr = librosa.load(str(audio_path), sr=SAMPLE_RATE)
        audio_duration = len(y) / sr
        audio_loading_time = time.time() - audio_loading_start
        log_message(f"Audio loaded successfully: duration={audio_duration:.2f}s, sample_rate={sr}, samples={len(y)}, loading_time={audio_loading_time:.2f}s")
    except Exception as e:
        error_msg = f"Failed to load audio from {audio_path}: {str(e)}"
        log_message(error_msg, "ERROR")
        import traceback
        log_message(f"Error traceback: {traceback.format_exc()}", "ERROR")
        raise RuntimeError(error_msg)
    
    # VAD检测
    try:
        log_message(f"Starting VAD detection (threshold={threshold}, min_duration={min_segment_duration}s, max_merge_gap={max_merge_gap}s)...")
        segments, performance_stats = detect_vad_segments(
            y=y,
            sr=sr,
            threshold=threshold,
            min_segment_duration=min_segment_duration,
            max_merge_gap=max_merge_gap,
            vad_model=vad_model,
            get_speech_timestamps=get_speech_timestamps,
            request_id=request_id,
            total_duration=audio_duration
        )
        log_message(f"VAD detection completed: found {len(segments)} segments")
    except Exception as e:
        error_msg = f"VAD detection failed: {str(e)}"
        log_message(error_msg, "ERROR")
        import traceback
        log_message(f"Error traceback: {traceback.format_exc()}", "ERROR")
        raise RuntimeError(error_msg)
    
    # 可选：导出音频段
    audio_segments = []
    segments_dir = request_output_dir / "segments"
    if export_segments:
        if not segments:
            log_message("No segments to export (empty segments list)", "WARNING")
        else:
            try:
                log_message(f"Exporting {len(segments)} audio segments to {segments_dir} (format: {output_format})...")
                audio_segments = export_audio_segments(
                    segments=segments,
                    y=y,
                    sr=sr,
                    output_dir=request_output_dir,
                    format=output_format,
                    request_id=request_id
                )
                log_message(f"Successfully exported {len(audio_segments)} audio segments")
            except Exception as e:
                error_msg = f"Failed to export audio segments: {str(e)}"
                log_message(error_msg, "WARNING")
                import traceback
                log_message(f"Warning traceback: {traceback.format_exc()}", "WARNING")
                # 继续执行，不中断流程
    
    # 计算总体语音比例
    if segments:
        overall_speech_ratio = segments[0].get("overall_speech_ratio", 0.0)
        log_message(f"Calculated speech ratio: {overall_speech_ratio * 100:.1f}%")
    else:
        overall_speech_ratio = 0.0
        log_message("No speech segments detected, speech ratio: 0%", "WARNING")
    
    # 计算性能统计
    total_processing_time = time.time() - overall_start_time
    speed_ratio = audio_duration / total_processing_time if total_processing_time > 0 else 0
    
    complete_performance_data = {
        "total_processing_time": total_processing_time,
        "audio_loading_time": audio_loading_time,
        "stage1_vad_timestamps_time": performance_stats.get("stage1_vad_timestamps_time", 0.0),
        "stage2_feature_extraction_time": performance_stats.get("stage2_feature_extraction_time", 0.0),
        "speed_ratio": speed_ratio
    }
    
    # VAD参数
    vad_parameters = {
        "threshold": threshold,
        "min_segment_duration": min_segment_duration,
        "max_merge_gap": max_merge_gap
    }
    
    # 保存结果
    timestamps_path = request_output_dir / "timestamps.json"
    try:
        log_message(f"Saving results to: {timestamps_path}")
        result_data = save_timestamps(
            segments=segments,
            timestamps_path=timestamps_path,
            request_id=request_id,
            audio_segments=audio_segments,
            overall_speech_ratio=overall_speech_ratio,
            source_file=str(input_path),  # 使用原始输入文件路径
            vad_parameters=vad_parameters,
            performance_data=complete_performance_data,
            total_audio_duration=audio_duration,
            output_format=output_format
        )
        log_message(f"Results saved successfully: {timestamps_path} (size: {timestamps_path.stat().st_size} bytes)")
    except Exception as e:
        error_msg = f"Failed to save results to {timestamps_path}: {str(e)}"
        log_message(error_msg, "ERROR")
        import traceback
        log_message(f"Error traceback: {traceback.format_exc()}", "ERROR")
        raise RuntimeError(error_msg)
    
    # 构建返回结果
    result = {
        "request_id": request_id,
        "input_file": str(input_path),
        "output_dir": str(request_output_dir),
        "json_path": str(timestamps_path),
        "segments_dir": str(segments_dir) if export_segments else None,
        "segments": result_data.get("segments", []),
        "summary": result_data.get("summary", {}),
        "performance": result_data.get("performance", {}),
        "metadata": result_data.get("metadata", {}),
        "total_segments": result_data.get("total_segments", 0),
        "total_duration": result_data.get("total_duration", 0.0),
        "overall_speech_ratio": overall_speech_ratio,
    }
    
    log_message("VAD analysis completed successfully!")
    log_message(f"Summary - Request ID: {request_id}")
    log_message(f"  - Total segments: {result['total_segments']}")
    log_message(f"  - Total duration: {result['total_duration']:.2f}s")
    log_message(f"  - Speech duration: {result['summary'].get('total_speech_duration', 0):.2f}s")
    log_message(f"  - Overall speech ratio: {result['overall_speech_ratio'] * 100:.1f}%")
    log_message(f"  - Processing time: {result['performance']['total_processing_time']:.2f}s")
    log_message(f"  - Speed ratio: {result['performance'].get('speed_ratio', 0):.2f}x")
    log_message(f"  - JSON result: {result['json_path']}")
    if result.get('segments_dir'):
        log_message(f"  - Segments directory: {result['segments_dir']}")
    
    return result
