# VAD Python 包改造方案

## 目标

将当前的 VAD CLI 工具改造为一个标准的 Python 包，提供清晰的 API 接口：
- **输入**：本地音频/视频文件 + 输出目录等参数
- **输出**：VAD JSON 结果 + 导出的音频切片

## 包结构设计

```
vad/
├── __init__.py              # 包入口，导出主要 API
├── core/
│   ├── __init__.py
│   ├── vad_detector.py      # VAD 检测核心逻辑（保持不变）
│   ├── audio_processor.py   # 音频处理（增强视频支持）
│   └── utils.py             # 工具函数（保持不变）
├── config/
│   ├── __init__.py
│   └── settings.py          # 配置管理（简化）
├── api/
│   ├── __init__.py
│   └── analyzer.py          # 主要 API：analyze() 函数
└── cli/
    └── __init__.py          # CLI 入口（可选，保持向后兼容）

examples/
└── vad_cli.py              # CLI 脚本（使用新包）
```

## API 设计

### 主要接口：`vad.analyze()`

```python
from vad import analyze

result = analyze(
    input_path="path/to/audio.wav",  # 或视频文件
    output_dir="path/to/output",     # 输出目录
    threshold=0.3,                  # VAD 阈值
    min_segment_duration=0.5,        # 最小片段时长
    max_merge_gap=0.2,               # 最大合并间隔
    export_segments=True,            # 是否导出切片
    output_format="wav",             # 输出格式：wav/flac
    request_id=None                  # 可选请求ID
)

# result 包含：
# - segments: List[Dict] - VAD 片段列表
# - json_path: Path - VAD JSON 文件路径
# - segments_dir: Path - 切片文件目录
# - metadata: Dict - 元数据
# - performance: Dict - 性能指标
```

### 返回数据结构

```python
{
    "request_id": str,
    "input_file": str,
    "output_dir": Path,
    "json_path": Path,
    "segments_dir": Path,
    "segments": List[Dict],  # VAD 片段
    "summary": Dict,         # 统计信息
    "performance": Dict,      # 性能指标
    "metadata": Dict          # 元数据
}
```

## 实现要点

### 1. 视频文件支持

在 `audio_processor.py` 中添加视频提取功能：

```python
def extract_audio_from_video(video_path: Path, output_audio_path: Path) -> Path:
    """从视频文件提取音频"""
    # 使用 ffmpeg-python 或 subprocess 调用 ffmpeg
    # 输出为 WAV 格式，16kHz 采样率
    pass
```

### 2. 包入口 (`__init__.py`)

```python
from pathlib import Path
from typing import Optional, Dict, Any, Literal

from .api.analyzer import analyze as _analyze

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
        output_dir: 输出目录
        threshold: VAD 检测阈值 (0.0-1.0)
        min_segment_duration: 最小片段时长（秒）
        max_merge_gap: 最大合并间隔（秒）
        export_segments: 是否导出音频切片
        output_format: 输出格式 ("wav" 或 "flac")
        request_id: 请求ID（可选，自动生成）
    
    Returns:
        包含分析结果的字典
    """
    return _analyze(
        input_path=Path(input_path),
        output_dir=Path(output_dir),
        threshold=threshold,
        min_segment_duration=min_segment_duration,
        max_merge_gap=max_merge_gap,
        export_segments=export_segments,
        output_format=output_format,
        request_id=request_id
    )

__all__ = ["analyze"]
```

### 3. 配置简化

`config/settings.py` 简化为仅包含必要的配置，移除项目特定的路径逻辑：

```python
# 默认配置，可通过环境变量覆盖
SAMPLE_RATE = int(os.getenv("VAD_SAMPLE_RATE", "16000"))
MIN_SEGMENT_DURATION = float(os.getenv("VAD_MIN_SEGMENT_DURATION", "0.1"))
DEFAULT_THRESHOLD = float(os.getenv("VAD_THRESHOLD", "0.3"))
```

### 4. pyproject.toml 更新

```toml
[project]
name = "vad"
version = "0.2.0"
description = "Voice Activity Detection (VAD) package for audio/video processing"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "torch>=2.0.0",
    "torchaudio>=2.0.0",
    "librosa>=0.10.0",
    "soundfile>=0.12.0",
    "numpy>=1.24.0",
    "ffmpeg-python>=0.2.0",  # 新增：视频支持
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["vad"]
```

## 使用示例

### 作为 Python 包使用

```python
from vad import analyze

# 分析音频文件
result = analyze(
    input_path="audio.wav",
    output_dir="./output",
    threshold=0.4,
    export_segments=True
)

print(f"检测到 {result['summary']['num_segments']} 个语音片段")
print(f"JSON 结果: {result['json_path']}")
print(f"切片目录: {result['segments_dir']}")
```

### 作为 CLI 工具使用（向后兼容）

```bash
# 使用新的包结构
python -m vad.cli audio.wav --output-dir ./output --export-segments

# 或使用旧脚本（内部调用新包）
python examples/vad_cli.py audio.wav --output-dir ./output
```

## 迁移步骤

1. **创建新包结构**：按照上述结构创建目录和文件
2. **重构核心逻辑**：将 `analyze_audio_file()` 移到 `api/analyzer.py`
3. **添加视频支持**：在 `audio_processor.py` 中添加视频提取
4. **更新 CLI**：`examples/vad_cli.py` 调用新包 API
5. **更新依赖**：添加 `ffmpeg-python` 到 `pyproject.toml`
6. **测试**：确保所有功能正常工作
7. **文档**：更新 README 和使用示例

## 优势

1. **标准化**：符合 Python 包标准结构
2. **可复用**：可作为库被其他项目导入
3. **清晰**：API 接口明确，易于使用
4. **扩展性**：易于添加新功能（如批量处理）
5. **向后兼容**：保持 CLI 工具可用
