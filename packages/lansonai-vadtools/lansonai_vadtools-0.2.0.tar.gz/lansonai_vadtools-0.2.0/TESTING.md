# VAD 包测试指南

## 快速测试

### 1. 包导入测试

测试包是否能正确导入：

```bash
cd scripts/python/vad
uv run python -c "from vad import analyze; print('✅ Package imported successfully')"
```

### 2. CLI 测试

测试命令行工具：

```bash
# 使用示例音频文件（需要准备测试文件）
uv run python examples/vad_cli.py /path/to/test.wav --output-dir ./test_output --json

# 测试视频文件（需要 ffmpeg）
uv run python examples/vad_cli.py /path/to/test.mp4 --output-dir ./test_output --export-segments
```

### 3. Python API 测试

```python
from vad import analyze

# 测试音频文件
result = analyze(
    input_path="test.wav",
    output_dir="./test_output",
    threshold=0.3,
    export_segments=True
)

print(f"Segments: {result['total_segments']}")
print(f"JSON: {result['json_path']}")
```

## 完整测试套件

### 运行测试脚本

```bash
cd scripts/python/vad
uv run python tests/test_package.py
```

### 测试内容

1. **包导入测试**
   - 验证包能正确导入
   - 验证 API 函数存在

2. **参数验证测试**
   - 测试无效输入文件
   - 测试无效参数值
   - 测试缺失必需参数

3. **功能测试**（需要测试文件）
   - 音频文件处理
   - 视频文件处理（需要 ffmpeg）
   - 结果文件生成
   - JSON 格式验证

4. **错误处理测试**
   - 文件不存在
   - 无效文件格式
   - 权限错误

## 手动测试步骤

### 准备测试文件

```bash
# 创建测试目录
mkdir -p test_audio test_output

# 准备测试音频文件（WAV格式，16kHz推荐）
# 可以从网上下载或使用 ffmpeg 转换
```

### 测试场景

#### 场景1: 基本音频分析

```bash
uv run python examples/vad_cli.py test_audio/sample.wav \
    --output-dir test_output \
    --threshold 0.3 \
    --export-segments \
    --json
```

**验证点：**
- ✅ 输出目录创建成功
- ✅ timestamps.json 文件存在
- ✅ JSON 格式正确
- ✅ segments 目录存在（如果导出）
- ✅ 日志输出正常

#### 场景2: 视频文件处理

```bash
uv run python examples/vad_cli.py test_audio/sample.mp4 \
    --output-dir test_output \
    --export-segments
```

**验证点：**
- ✅ 视频检测成功
- ✅ 音频提取成功
- ✅ VAD 分析完成
- ✅ 临时音频文件存在（在输出目录中）

#### 场景3: 不同参数测试

```bash
# 高阈值（更严格）
uv run python examples/vad_cli.py test_audio/sample.wav \
    --output-dir test_output \
    --threshold 0.5

# 低阈值（更宽松）
uv run python examples/vad_cli.py test_audio/sample.wav \
    --output-dir test_output \
    --threshold 0.2

# 不同输出格式
uv run python examples/vad_cli.py test_audio/sample.wav \
    --output-dir test_output \
    --format flac \
    --export-segments
```

#### 场景4: 错误处理测试

```bash
# 文件不存在
uv run python examples/vad_cli.py nonexistent.wav --output-dir test_output
# 应该输出错误信息

# 无效输出目录（权限问题）
uv run python examples/vad_cli.py test_audio/sample.wav --output-dir /root/forbidden
# 应该输出权限错误
```

## 自动化测试

### 单元测试示例

创建 `tests/test_package.py`：

```python
import pytest
from pathlib import Path
from vad import analyze

def test_package_import():
    """测试包导入"""
    from vad import analyze
    assert callable(analyze)

def test_invalid_file():
    """测试无效文件"""
    with pytest.raises(FileNotFoundError):
        analyze("nonexistent.wav", "./test_output")

def test_invalid_output_dir():
    """测试无效输出目录"""
    # 需要准备一个测试音频文件
    test_file = Path("test_audio/sample.wav")
    if test_file.exists():
        with pytest.raises(RuntimeError):
            analyze(str(test_file), "/invalid/path/that/does/not/exist")
```

### 运行 pytest

```bash
# 安装测试依赖
uv pip install pytest pytest-cov

# 运行测试
uv run pytest tests/ -v

# 带覆盖率
uv run pytest tests/ --cov=vad --cov-report=html
```

## 性能测试

### 测试不同大小的文件

```bash
# 小文件（< 1MB）
uv run python examples/vad_cli.py small.wav --output-dir test_output

# 中等文件（1-10MB）
uv run python examples/vad_cli.py medium.wav --output-dir test_output

# 大文件（> 10MB）
uv run python examples/vad_cli.py large.wav --output-dir test_output
```

查看性能指标：
- 处理时间
- 速度比（音频时长/处理时间）
- 内存使用

## 集成测试

### 端到端测试流程

```python
from vad import analyze
from pathlib import Path
import json

def test_full_workflow():
    """完整工作流测试"""
    # 1. 分析音频
    result = analyze(
        input_path="test_audio/sample.wav",
        output_dir="./test_output",
        export_segments=True
    )
    
    # 2. 验证结果
    assert result['total_segments'] > 0
    assert Path(result['json_path']).exists()
    assert Path(result['segments_dir']).exists()
    
    # 3. 验证 JSON 格式
    with open(result['json_path']) as f:
        data = json.load(f)
        assert 'segments' in data
        assert 'summary' in data
        assert 'performance' in data
    
    # 4. 验证切片文件
    segments_dir = Path(result['segments_dir'])
    assert segments_dir.exists()
    segment_files = list(segments_dir.glob("segment_*.wav"))
    assert len(segment_files) == result['total_segments']
    
    print("✅ Full workflow test passed")
```

## 测试检查清单

### 功能测试
- [ ] 包能正确导入
- [ ] 音频文件分析成功
- [ ] 视频文件分析成功（需要 ffmpeg）
- [ ] JSON 结果文件生成
- [ ] 音频切片导出（如果启用）
- [ ] 不同参数组合正常工作

### 错误处理
- [ ] 文件不存在错误
- [ ] 无效文件格式错误
- [ ] 输出目录权限错误
- [ ] 日志输出正确

### 边界情况
- [ ] 空音频文件
- [ ] 无语音的音频
- [ ] 超长音频文件
- [ ] 特殊字符文件名

### 性能
- [ ] 小文件处理时间合理
- [ ] 大文件不会内存溢出
- [ ] 性能指标记录正确

## 调试技巧

### 启用详细日志

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from vad import analyze
# ... 运行分析
```

### 检查输出文件

```bash
# 查看 JSON 结果
cat test_output/{request_id}/timestamps.json | jq

# 检查切片文件
ls -lh test_output/{request_id}/segments/

# 验证音频文件
file test_output/{request_id}/segments/segment_001.wav
```

### 常见问题排查

1. **导入错误**: 检查 Python 路径和包安装
2. **ffmpeg 错误**: 确保 ffmpeg 已安装并在 PATH 中
3. **内存不足**: 检查音频文件大小，考虑分块处理
4. **权限错误**: 检查输出目录权限
