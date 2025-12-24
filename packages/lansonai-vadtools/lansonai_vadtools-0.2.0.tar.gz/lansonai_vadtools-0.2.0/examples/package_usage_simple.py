#!/usr/bin/env python3
"""
最简单的包使用示例
演示如何像使用标准 Python 包一样使用 vad
"""

import sys
from pathlib import Path

# 添加项目路径（实际安装后不需要这行）
sys.path.insert(0, str(Path(__file__).parent.parent))

# 像使用标准包一样导入
from vad import analyze

# 使用包 API
result = analyze(
    input_path="/path/to/your/audio.wav",  # 替换为实际文件路径
    output_dir="./output",
    threshold=0.3,
    export_segments=True
)

# 处理结果
print(f"检测到 {result['total_segments']} 个语音片段")
print(f"语音比例: {result['overall_speech_ratio'] * 100:.1f}%")
print(f"结果文件: {result['json_path']}")
