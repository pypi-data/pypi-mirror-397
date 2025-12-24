#!/usr/bin/env python3
"""
VAD 包使用示例
演示如何使用 vad 包进行音频/视频分析
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from vad import analyze

def main():
    """示例：分析音频文件"""
    
    # 示例1: 分析音频文件
    print("示例1: 分析音频文件")
    result = analyze(
        input_path="path/to/audio.wav",
        output_dir="./output",
        threshold=0.3,
        min_segment_duration=0.5,
        export_segments=True
    )
    
    print(f"检测到 {result['total_segments']} 个语音片段")
    print(f"JSON 结果: {result['json_path']}")
    print(f"切片目录: {result['segments_dir']}")
    
    # 示例2: 分析视频文件
    print("\n示例2: 分析视频文件")
    result = analyze(
        input_path="path/to/video.mp4",
        output_dir="./output",
        export_segments=True,
        output_format="flac"
    )
    
    print(f"检测到 {result['total_segments']} 个语音片段")
    print(f"语音比例: {result['overall_speech_ratio'] * 100:.1f}%")
    
    # 示例3: 批量处理（调用方自己控制）
    print("\n示例3: 批量处理")
    files = ["audio1.wav", "audio2.wav", "video1.mp4"]
    for file in files:
        try:
            result = analyze(file, output_dir="./output")
            print(f"✓ {file}: {result['total_segments']} segments")
        except Exception as e:
            print(f"✗ {file}: {e}")

if __name__ == "__main__":
    main()
