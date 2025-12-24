import torch
from torch.hub import load_state_dict_from_url
import numpy as np
import librosa
from typing import List, Dict, Any, Tuple
from pathlib import Path
import soundfile as sf
from datetime import datetime
import time

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from lansonai.vadtools.config.settings import OUTPUT_DIR, SAMPLE_RATE
from lansonai.vadtools.core.audio_processor import convert_audio_format
from lansonai.vadtools.core.utils import log_message, get_current_time

def detect_vad_segments(y: np.ndarray, sr: int, threshold: float, min_segment_duration: float, max_merge_gap: float = 0.0, vad_model = None, get_speech_timestamps = None, request_id: str = "", total_duration: float = None) -> Tuple[List[Dict], Dict[str, float]]:
    """
    使用 Silero VAD 检测音频中的语音活动段
    返回段列表和性能统计数据
    """
    try:
        current_time = get_current_time()
        log_message(f"开始 Silero VAD 检测, 采样率: {sr}, 长度: {len(y)} (request_id: {request_id})")
        
        if y is None or len(y) == 0:
            raise ValueError("音频数据为空，无法进行 VAD 检测")
        
        audio_duration = len(y) / sr
        if total_duration is None:
            total_duration = audio_duration
        
        # 阶段1: VAD时间戳检测
        stage1_start = time.time()
        log_message(f"开始阶段1: VAD时间戳检测 (request_id: {request_id})")
        
        # 转换为 tensor
        tensor = torch.from_numpy(y).float()
        if tensor.dim() == 1:
            tensor = tensor.unsqueeze(0)
        
        # 使用 Silero VAD 获取时间戳
        timestamps = get_speech_timestamps(
            tensor, 
            vad_model, 
            threshold=threshold, 
            sampling_rate=sr, 
            min_speech_duration_ms=int(min_segment_duration * 1000), 
            min_silence_duration_ms=250, 
            return_seconds=True
        )
        
        stage1_time = time.time() - stage1_start
        log_message(f"阶段1完成: 检测到 {len(timestamps)} 个潜在语音片段，耗时: {stage1_time:.2f}s (request_id: {request_id})")
        
        # 阶段2: 特征提取和置信度计算
        stage2_start = time.time()
        log_message(f"开始阶段2: 特征提取和置信度计算 (request_id: {request_id})")
        
        segments = []
        WINDOW_SIZE_SAMPLES = 512
        
        for i, ts in enumerate(timestamps):
            start_sample = int(ts["start"] * sr)
            end_sample = int(ts["end"] * sr)
            audio_data = y[start_sample:end_sample]
            
            # 计算置信度 (参考demo的方法)
            probs_in_segment = []
            tensor_segment = torch.from_numpy(audio_data).float()
            
            for j in range(0, len(audio_data), WINDOW_SIZE_SAMPLES):
                chunk = tensor_segment[j:j + WINDOW_SIZE_SAMPLES]
                if chunk.shape[0] < WINDOW_SIZE_SAMPLES:
                    chunk = torch.nn.functional.pad(chunk, (0, WINDOW_SIZE_SAMPLES - chunk.shape[0]))
                
                try:
                    speech_prob = vad_model(chunk.unsqueeze(0), sr).item()
                    probs_in_segment.append(speech_prob)
                except Exception:
                    probs_in_segment.append(0.8)  # 默认值
            
            confidence = float(np.mean(probs_in_segment)) if probs_in_segment else 0.8
            
            # 计算声学特征
            if audio_data.size > 0:
                rms = float(np.sqrt(np.mean(audio_data**2)))
                peak_amplitude = float(np.max(np.abs(audio_data)))
            else:
                rms = 0.0
                peak_amplitude = 0.0
                
            segment = {
                "start_time": ts["start"],
                "end_time": ts["end"],
                "duration": ts["end"] - ts["start"],
                "rms": rms,
                "peak_amplitude": peak_amplitude,
                "speech_confidence": confidence,
                "audio_data": audio_data
            }
            segments.append(segment)
            
            # 进度日志 (每100个段)
            if (i + 1) % 100 == 0:
                log_message(f"已处理 {i + 1}/{len(timestamps)} 个片段 (request_id: {request_id})")
        
        stage2_time = time.time() - stage2_start
        log_message(f"阶段2完成: 特征和置信度计算完毕，耗时: {stage2_time:.2f}s (request_id: {request_id})")
        
        # 可选：合并相近的段
        if max_merge_gap > 0 and len(segments) > 1:
            merged_segments = [segments[0]]
            for current_seg in segments[1:]:
                last_seg = merged_segments[-1]
                gap = current_seg["start_time"] - last_seg["end_time"]
                
                if gap <= max_merge_gap:
                    # 合并并重新提取 audio_data
                    start_sample = int(last_seg["start_time"] * sr)
                    end_sample = int(current_seg["end_time"] * sr)
                    merged_audio_data = y[start_sample:end_sample]
                    
                    if merged_audio_data.size > 0:
                        merged_rms = float(np.sqrt(np.mean(merged_audio_data**2)))
                        merged_peak = float(np.max(np.abs(merged_audio_data)))
                    else:
                        merged_rms = 0.0
                        merged_peak = 0.0
                        
                    merged_seg = {
                        "start_time": last_seg["start_time"],
                        "end_time": current_seg["end_time"],
                        "duration": current_seg["end_time"] - last_seg["start_time"],
                        "rms": merged_rms,
                        "peak_amplitude": merged_peak,
                        "speech_confidence": (last_seg["speech_confidence"] + current_seg["speech_confidence"]) / 2,
                        "audio_data": merged_audio_data
                    }
                    merged_segments[-1] = merged_seg
                    current_time = get_current_time()
                    log_message(f"合并段: gap={gap:.2f}s, 新时长={merged_seg['duration']:.2f}s (request_id: {request_id})", "DEBUG")
                else:
                    merged_segments.append(current_seg)
            
            segments = merged_segments
        
        # 计算统计信息
        total_voice_duration = sum(seg["duration"] for seg in segments)
        if segments:
            segments[0]["overall_speech_ratio"] = total_voice_duration / total_duration
        
        # 准备性能统计数据
        performance_stats = {
            "stage1_vad_timestamps_time": stage1_time,
            "stage2_feature_extraction_time": stage2_time
        }
        
        current_time = get_current_time()
        log_message(f"Silero VAD 检测完成，检测到 {len(segments)} 个语音段，总语音时长: {total_voice_duration:.2f} 秒，语音比例: {total_voice_duration / total_duration * 100:.1f}% (request_id: {request_id})")
        
        return segments, performance_stats
        
    except Exception as e:
        current_time = get_current_time()
        error_msg = f"Silero VAD 检测失败: {str(e)}"
        log_message(f"{error_msg} (request_id: {request_id})", "ERROR")
        import traceback
        log_message(f"错误堆栈: {traceback.format_exc()} (request_id: {request_id})", "ERROR")
        raise

def export_segments(segments: List[Dict], y: np.ndarray, sr: int, output_dir: Path, format: str = "wav", request_id: str = "") -> List[Dict]:
    """
    导出语音段为单独的音频文件到输出目录
    返回包含质量指标的详细信息
    """
    current_time = get_current_time()
    segments_dir = output_dir / "segments"
    segments_dir.mkdir(parents=True, exist_ok=True)
    exported_files = []
    
    if not segments:
        log_message(f"无语音段需要导出 (request_id: {request_id})")
        return exported_files
    
    # 检查分片数量限制（不超过1000个分片）
    if len(segments) > 1000:
        error_msg = f"检测到 {len(segments)} 个语音分片，超过1000个限制。音频可能需要预处理。"
        log_message(f"{error_msg} (request_id: {request_id})", "ERROR")
        raise ValueError(error_msg)
    
    log_message(f"开始导出 {len(segments)} 个语音段到 {segments_dir} (format: {format}) (request_id: {request_id})")
    
    for i, segment in enumerate(segments):
        try:
            segment_file = segments_dir / f"segment_{i+1:03d}.{format}"
            
            # 获取 audio_data
            if "audio_data" in segment and segment["audio_data"] is not None:
                audio_data = segment["audio_data"]
            else:
                # 重新提取
                start_sample = int(segment["start_time"] * sr)
                end_sample = int(segment["end_time"] * sr)
                audio_data = y[start_sample:end_sample]
            
            # 保存音频
            sf.write(str(segment_file), audio_data, sr, format='FLAC' if format == 'flac' else 'WAV')
            
            # 验证文件
            if not segment_file.exists() or segment_file.stat().st_size == 0:
                raise ValueError(f"段文件导出失败: {segment_file}")
            
            # 构建详细导出信息，使用完整的绝对路径
            export_info = {
                "source_url": str(segment_file.resolve()),
                "start_time": segment["start_time"],
                "end_time": segment["end_time"],
                "duration": segment["duration"],
                "size_bytes": int(segment_file.stat().st_size),
                "rms": segment.get("rms", 0.0),
                "peak_amplitude": segment.get("peak_amplitude", 0.0),
                "speech_confidence": segment.get("speech_confidence", 0.8)
            }
            if "overall_speech_ratio" in segment:
                export_info["overall_speech_ratio"] = segment["overall_speech_ratio"]
            exported_files.append(export_info)
            
            current_time = get_current_time()
            log_message(f"导出段 {i+1}/{len(segments)}: {segment_file.name}, 时长: {segment['duration']:.2f}s, RMS: {export_info['rms']:.4f}, 峰值: {export_info['peak_amplitude']:.4f}, 大小: {export_info['size_bytes']} 字节 (request_id: {request_id})")
            
        except Exception as e:
            current_time = get_current_time()
            log_message(f"导出段 {i+1} 失败: {str(e)} (request_id: {request_id})", "ERROR")
            continue
    
    current_time = get_current_time()
    log_message(f"语音段导出完成，成功: {len(exported_files)}/{len(segments)} (request_id: {request_id})")
    return exported_files