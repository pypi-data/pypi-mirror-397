# LansonAI VAD Tools - Python 包使用说明

## 安装

### 从 PyPI 安装（推荐）

```bash
pip install lansonai-vadtools
```

### 从源码安装（开发模式）

```bash
cd scripts/python/vad
uv pip install -e .
```

## 使用方式

### 作为 Python 包使用

```python
from lansonai.vadtools import analyze

# 分析音频文件
result = analyze(
    input_path="audio.wav",
    output_dir="./output",
    threshold=0.3,
    min_segment_duration=0.5,
    max_merge_gap=0.2,
    export_segments=True,
    output_format="wav"
)

print(f"检测到 {result['total_segments']} 个语音片段")
print(f"JSON 结果: {result['json_path']}")
print(f"切片目录: {result['segments_dir']}")
```

### 作为 CLI 工具使用

```bash
# 使用 CLI（向后兼容）
python examples/vad_cli.py audio.wav --output-dir ./output --export-segments

# 或使用 uv 运行
uv run python examples/vad_cli.py video.mp4 --output-dir ./output
```

## API 说明

### `analyze()` 函数

**参数：**
- `input_path` (str | Path): 输入音频或视频文件路径
- `output_dir` (str | Path): 输出目录（调用方保证存在）
- `threshold` (float, 默认 0.3): VAD 检测阈值 (0.0-1.0)
- `min_segment_duration` (float, 默认 0.5): 最小片段时长（秒）
- `max_merge_gap` (float, 默认 0.2): 最大合并间隔（秒）
- `export_segments` (bool, 默认 True): 是否导出音频切片
- `output_format` (str, 默认 "wav"): 输出格式 ("wav" 或 "flac")
- `request_id` (str, 可选): 请求ID，如果不提供会自动生成

**返回：**
```python
{
    "request_id": str,
    "input_file": str,
    "output_dir": str,           # {output_dir}/{request_id}
    "json_path": str,             # timestamps.json 路径
    "segments_dir": str | None,   # 切片目录路径（如果导出）
    "segments": List[Dict],       # VAD 片段列表
    "summary": Dict,              # 统计信息
    "performance": Dict,          # 性能指标
    "metadata": Dict,             # 元数据
    "total_segments": int,
    "total_duration": float,
    "overall_speech_ratio": float
}
```

**输出目录结构：**
```
{output_dir}/
└── {request_id}/
    ├── timestamps.json          # VAD JSON 结果
    └── segments/                # 音频切片（如果导出）
        ├── segment_001.wav
        ├── segment_002.wav
        └── ...
```

## 支持的格式

**输入：**
- 音频：WAV, MP3, M4A, FLAC, OGG
- 视频：MP4, AVI, MOV, MKV, FLV, WMV, WEBM, M4V（需要安装 ffmpeg）

**输出：**
- WAV
- FLAC

## 依赖

- Python >= 3.12
- torch >= 2.0.0
- torchaudio >= 2.0.0
- librosa >= 0.10.0
- soundfile >= 0.12.0
- numpy >= 1.24.0
- ffmpeg（用于视频处理，系统级依赖）

## 发行

使用 uv 构建和发行：

```bash
# 构建
uv build

# 发布到 PyPI（需要配置）
uv publish
```
