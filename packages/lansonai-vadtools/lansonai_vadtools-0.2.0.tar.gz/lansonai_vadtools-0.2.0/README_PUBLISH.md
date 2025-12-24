# 快速发布指南

## 发布命令

```bash
cd scripts/python/vad

# 1. 构建包
uv build

# 2. 发布到 PyPI（需要配置 token）
uv publish
```

## 配置 PyPI Token

### 方法 1: 环境变量

```bash
export UV_PUBLISH_TOKEN="pypi-your-api-token"
uv publish
```

### 方法 2: 使用 twine

```bash
pip install twine
twine upload dist/*
```

## 包信息

- **包名**: `lansonai-vadtools`
- **导入**: `from lansonai.vadtools import analyze`
- **版本**: 0.2.0

## 安装使用

```bash
pip install lansonai-vadtools
```

```python
from lansonai.vadtools import analyze

result = analyze("audio.wav", "./output")
```
