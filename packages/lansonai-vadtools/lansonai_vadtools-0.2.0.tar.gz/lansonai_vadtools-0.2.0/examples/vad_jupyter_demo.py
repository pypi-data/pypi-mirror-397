# %%
import sys
# !uv pip install --python {sys.executable} torch torchaudio numpy



# %%
# ==================================
# CELL 1: 导入所有必要的库
# ==================================
import torch
import torchaudio
import numpy as np
import json
import os
from pprint import pprint
import uuid
from datetime import datetime
import time

print("✓ 所有库已成功导入。")



# %%
# ==================================
# CELL 2: 定义辅助函数
# ==================================
def calculate_acoustic_features(audio_chunk_np: np.ndarray):
    """
    计算音频块的 RMS (音量) 和 Peak Amplitude (峰值)。
    """
    if audio_chunk_np.size == 0:
        return {"rms": 0.0, "peak_amplitude": 0.0}
    
    rms_val = np.sqrt(np.mean(audio_chunk_np**2))
    peak_val = np.max(np.abs(audio_chunk_np))
    
    return {
        "rms": float(rms_val),
        "peak_amplitude": float(peak_val)
    }

def log_message(message: str):
    """
    打印带时间戳的日志信息。
    """
    timestamp = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

print("✓ 辅助函数 calculate_acoustic_features, log_message 已定义。")



# %%
# ==================================
# CELL 3: 配置参数 (这是您最常修改的部分)
# ==================================
# --- 请将这里修改为您的音频文件路径 ---
AUDIO_FILE = "/home/isakeem/Code/subtitle-storage-service/data/audio/chinese_how_fear_happend.m4a"  

# VAD 参数
THRESHOLD = 0.5               # 语音概率阈值
MIN_SPEECH_DURATION = 250     # (毫秒) 最短语音片段
SPEECH_PAD = 100              # (毫秒) 在语音前后添加的静音

# 检查文件是否存在
if not os.path.exists(AUDIO_FILE):
    print(f"❌ 错误: 找不到音频文件 '{AUDIO_FILE}'")
    print(f"请确保文件路径正确，当前工作目录是: {os.getcwd()}")
else:
    print(f"✓ 配置文件加载成功，将处理: {AUDIO_FILE}")
    log_message(f"使用VAD参数 -> 阈值: {THRESHOLD}, 最短语音: {MIN_SPEECH_DURATION}ms, 语音填充: {SPEECH_PAD}ms")


# %%
# ==================================
# CELL 4: 加载模型 (只需运行一次)
# ==================================
print("正在加载 Silero VAD 模型...")
try:
    model, utils = torch.hub.load(
        repo_or_dir='snakers4/silero-vad',
        model='silero_vad',
        force_reload=False,
        onnx=False  # 如果您安装了 onnxruntime 并希望加速，可以设为 True
    )
    (get_speech_timestamps,
     save_audio,
     read_audio,
     VADIterator,
     collect_chunks) = utils
    print("✓ 模型和工具已成功加载到内存。")
except Exception as e:
    print(f"❌ 加载模型失败: {e}")


# %%
# ==================================
# CELL 5: 核心处理流程 (修复版本)
# ==================================
SAMPLING_RATE = 16000
analysis_result = None
overall_start_time = time.time()

log_message(f"开始处理音频文件: {AUDIO_FILE}")
try:
    # --- 1. 加载和预处理音频 ---
    load_start_time = time.time()
    
    # 获取音频元数据
    audio_info = torchaudio.info(AUDIO_FILE)
    log_message(f"原始音频信息 -> 采样率: {audio_info.sample_rate}Hz, 声道数: {audio_info.num_channels}, 时长: {audio_info.num_frames / audio_info.sample_rate:.2f}s")

    wav_tensor, sr = torchaudio.load(AUDIO_FILE)
    if sr != SAMPLING_RATE:
        log_message(f"音频采样率 ({sr}Hz) 与目标 ({SAMPLING_RATE}Hz) 不符，正在重采样...")
        resampler = torchaudio.transforms.Resample(sr, SAMPLING_RATE)
        wav_tensor = resampler(wav_tensor)
    if wav_tensor.shape[0] > 1:
        log_message("音频为多声道，正在混合为单声道...")
        wav_tensor = torch.mean(wav_tensor, dim=0, keepdim=True)
    wav_tensor = wav_tensor.squeeze()
    wav_np = wav_tensor.numpy()
    total_samples = len(wav_np)
    load_time = time.time() - load_start_time
    total_duration_in_seconds = total_samples / SAMPLING_RATE
    log_message(f"✓ 音频预处理完成，耗时 {load_time:.2f} 秒。总时长: {total_duration_in_seconds:.2f} 秒。")

    # --- 2. VAD 处理和特征计算 (混合方案) ---
    log_message("开始语音活动检测 (阶段1: 获取稳定时间戳)...")
    stage1_start_time = time.time()
    
    speech_timestamps = get_speech_timestamps(
        wav_tensor,
        model,
        sampling_rate=SAMPLING_RATE,
        threshold=THRESHOLD,
        min_speech_duration_ms=MIN_SPEECH_DURATION,
        speech_pad_ms=SPEECH_PAD
    )
    stage1_time = time.time() - stage1_start_time
    log_message(f"阶段1完成: 使用 get_speech_timestamps 检测到 {len(speech_timestamps)} 个潜在语音片段。耗时: {stage1_time:.2f} 秒。")
    
    log_message("开始计算特征和置信度 (阶段2: 遍历各片段，分块提取 speech_prob)...")
    stage2_start_time = time.time()
    
    WINDOW_SIZE_SAMPLES = 512
    raw_segments = []

    for i, seg in enumerate(speech_timestamps):
        start_sample, end_sample = seg['start'], seg['end']
        
        probs_in_segment = []
        for j in range(start_sample, end_sample, WINDOW_SIZE_SAMPLES):
            chunk = wav_tensor[j: j + WINDOW_SIZE_SAMPLES]
            if chunk.shape[0] < WINDOW_SIZE_SAMPLES:
                chunk = torch.nn.functional.pad(chunk, (0, WINDOW_SIZE_SAMPLES - chunk.shape[0]))
            
            speech_prob = model(chunk, SAMPLING_RATE).item()
            probs_in_segment.append(speech_prob)
        
        confidence = np.mean(probs_in_segment) if probs_in_segment else 0.0
        
        audio_chunk_np = wav_np[start_sample:end_sample]
        acoustic_features = calculate_acoustic_features(audio_chunk_np)
        
        segment_data = {
            'start': start_sample,
            'end': end_sample,
            'speech_confidence': float(confidence)
        }
        segment_data.update(acoustic_features)
        raw_segments.append(segment_data)
        if (i + 1) % 100 == 0:
            log_message(f"    ...已处理 {i + 1}/{len(speech_timestamps)} 个片段")

    stage2_time = time.time() - stage2_start_time
    log_message(f"阶段2完成: 特征和置信度计算完毕。耗时: {stage2_time:.2f} 秒。")

    # --- 3. 格式化并保存最终输出 ---
    log_message("处理完成，正在格式化并保存输出...")
    output_start_time = time.time()

    run_id = str(uuid.uuid4())
    output_dir = os.path.join("scripts", ".output", "vad", run_id)
    segments_dir = os.path.join(output_dir, "segments")
    os.makedirs(segments_dir, exist_ok=True)
    log_message(f"结果将保存到: {os.path.abspath(output_dir)}")
    
    final_segments = []
    total_speech_samples = sum(seg['end'] - seg['start'] for seg in raw_segments)
    
    source_file_abs_path = os.path.abspath(AUDIO_FILE)

    for i, seg in enumerate(raw_segments):
        start_time = seg['start'] / SAMPLING_RATE
        end_time = seg['end'] / SAMPLING_RATE
        
        # 保存单个音频片段
        segment_audio_tensor = wav_tensor[seg['start']:seg['end']]
        if segment_audio_tensor.ndim == 1:
            segment_audio_tensor = segment_audio_tensor.unsqueeze(0)
        
        segment_filename = f"segment_{i:04d}.wav"
        segment_path = os.path.join(segments_dir, segment_filename)
        torchaudio.save(segment_path, segment_audio_tensor, SAMPLING_RATE)

        # 格式化用于JSON输出
        final_segments.append({
            "id": i,
            "file_path": os.path.abspath(segment_path),
            "start_time": round(start_time, 3),
            "end_time": round(end_time, 3),
            "duration": round(end_time - start_time, 3),
            "speech_confidence": round(seg.get('speech_confidence', 0.0), 4),
            "rms": round(seg.get('rms', 0.0), 6),
            "peak_amplitude": round(seg.get('peak_amplitude', 0.0), 6),
        })

    overall_time = time.time() - overall_start_time
    total_duration_in_seconds = total_samples / SAMPLING_RATE

    analysis_result = {
        "metadata": {
            "source_file": source_file_abs_path,
            "run_id": run_id,
            "processing_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "parameters": {
                "threshold": THRESHOLD,
                "min_speech_duration_ms": MIN_SPEECH_DURATION,
                "speech_pad_ms": SPEECH_PAD
            }
        },
        "performance": {
            "total_processing_time": round(overall_time, 2),
            "audio_loading_time": round(load_time, 2),
            "stage1_vad_timestamps_time": round(stage1_time, 2),
            "stage2_feature_extraction_time": round(stage2_time, 2),
            "speed_ratio": round(total_duration_in_seconds / overall_time, 2) if overall_time > 0 else 0
        },
        "summary": {
            "total_duration": round(total_duration_in_seconds, 3),
            "total_speech_duration": round(total_speech_samples / SAMPLING_RATE, 3),
            "overall_speech_ratio": round((total_speech_samples / total_samples) if total_samples > 0 else 0, 4),
            "num_segments": len(final_segments),
        },
        "segments": final_segments,
    }
    
    json_output_path = os.path.join(output_dir, "timestamps.json")
    with open(json_output_path, 'w', encoding='utf-8') as f:
        json.dump(analysis_result, f, ensure_ascii=False, indent=4)
        
    output_time = time.time() - output_start_time
    log_message(f"✓ 输出已保存。耗时 {output_time:.2f} 秒。")
    log_message(f"✓✓✓ 全部处理完成！总耗时: {overall_time:.2f} 秒。")
    log_message(f"处理速度比: {analysis_result['performance']['speed_ratio']:.2f}x (音频时长 / 处理时间)")

except Exception as e:
    log_message(f"❌ 在处理过程中发生错误: {e}")
    import traceback
    traceback.print_exc()

# %%
