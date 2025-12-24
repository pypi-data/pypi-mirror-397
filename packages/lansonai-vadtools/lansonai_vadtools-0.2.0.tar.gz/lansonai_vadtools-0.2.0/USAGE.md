# VAD 包使用指南

## 安装

```bash
pip install lansonai-vadtools
```

## 作为 Python 包使用

### 1. 基本使用

```python
from lansonai.vadtools import analyze

# 分析音频文件
result = analyze(
    input_path="audio.wav",
    output_dir="./output",
    export_segments=True
)

print(f"检测到 {result['total_segments']} 个语音片段")
print(f"结果文件: {result['json_path']}")
```

### 2. 完整参数示例

```python
from vad import analyze

result = analyze(
    input_path="audio.wav",           # 输入文件（音频或视频）
    output_dir="./output",             # 输出目录（调用方保证存在）
    threshold=0.3,                     # VAD 阈值 (0.0-1.0)
    min_segment_duration=0.5,          # 最小片段时长（秒）
    max_merge_gap=0.2,                 # 最大合并间隔（秒）
    export_segments=True,              # 是否导出音频切片
    output_format="wav",               # 输出格式: "wav" 或 "flac"
    request_id=None                    # 请求ID（可选，自动生成）
)
```

### 3. 返回结果结构

```python
{
    "request_id": str,                 # 请求ID
    "input_file": str,                 # 输入文件路径
    "output_dir": str,                 # 输出目录路径
    "json_path": str,                  # VAD JSON 文件路径
    "segments_dir": str | None,        # 切片目录路径（如果导出）
    "segments": List[Dict],            # VAD 片段列表
    "summary": Dict,                   # 统计信息
    "performance": Dict,               # 性能指标
    "metadata": Dict,                  # 元数据
    "total_segments": int,             # 总片段数
    "total_duration": float,           # 总时长（秒）
    "overall_speech_ratio": float      # 语音比例 (0.0-1.0)
}
```

### 4. 批量处理示例

```python
from vad import analyze
from pathlib import Path

# 批量处理多个文件
files = ["audio1.wav", "audio2.mp3", "video1.mp4"]
results = []

for file in files:
    try:
        result = analyze(
            input_path=file,
            output_dir="./batch_output",
            export_segments=True
        )
        results.append({
            "file": file,
            "segments": result['total_segments'],
            "speech_ratio": result['overall_speech_ratio']
        })
        print(f"✅ {file}: {result['total_segments']} segments")
    except Exception as e:
        print(f"❌ {file}: {e}")
```

### 5. 处理结果文件

```python
import json
from pathlib import Path

result = analyze("audio.wav", "./output")

# 读取 JSON 结果
with open(result['json_path']) as f:
    data = json.load(f)
    
    # 访问片段信息
    for segment in data['segments']:
        print(f"Segment {segment['id']}: {segment['start_time']:.2f}s - {segment['end_time']:.2f}s")
    
    # 访问统计信息
    print(f"总语音时长: {data['summary']['total_speech_duration']:.2f}s")
    print(f"语音比例: {data['summary']['overall_speech_ratio'] * 100:.1f}%")
    
    # 访问性能指标
    print(f"处理时间: {data['performance']['total_processing_time']:.2f}s")
    print(f"速度比: {data['performance']['speed_ratio']:.1f}x")

# 访问音频切片文件
if result.get('segments_dir'):
    segments_dir = Path(result['segments_dir'])
    segment_files = list(segments_dir.glob("segment_*.wav"))
    print(f"生成了 {len(segment_files)} 个音频切片文件")
```

## 运行示例

### 测试包导入

```bash
cd scripts/python/vad
uv run python -c "from vad import analyze; print('✅ Package works!')"
```

### 运行完整测试

```bash
# 使用真实音频文件测试
uv run python tests/test_as_package.py

# 或使用 CLI
uv run python examples/vad_cli.py audio.wav --output-dir ./output --json
```

## 输出目录结构

```
{output_dir}/
└── {request_id}/
    ├── timestamps.json          # VAD JSON 结果
    └── segments/                # 音频切片（如果导出）
        ├── segment_001.wav
        ├── segment_002.wav
        └── ...
```

## 注意事项

1. **输出目录**: 调用方需要确保输出目录存在或有创建权限
2. **视频文件**: 需要系统安装 `ffmpeg` 才能处理视频文件
3. **内存使用**: 大文件会占用较多内存，建议监控内存使用
4. **错误处理**: 所有异常都会抛出，调用方需要处理

## 常见用法

### 只获取 JSON 结果（不导出切片）

```python
result = analyze(
    input_path="audio.wav",
    output_dir="./output",
    export_segments=False  # 不导出切片，更快
)
```

### 使用自定义请求ID

```python
result = analyze(
    input_path="audio.wav",
    output_dir="./output",
    request_id="my-custom-id-123"
)
```

### 调整检测灵敏度

```python
# 更严格（检测更少的语音）
result = analyze("audio.wav", "./output", threshold=0.5)

# 更宽松（检测更多的语音）
result = analyze("audio.wav", "./output", threshold=0.2)
```
