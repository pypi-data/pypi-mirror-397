# 发布 lansonai-vadtools 包

## 包信息

- **包名**: `lansonai-vadtools`
- **导入名**: `lansonai.vadtools`
- **当前版本**: 0.2.0

## 发布前检查清单

### 1. 验证包结构

```bash
cd scripts/python/vad

# 检查包结构
ls -la lansonai/vadtools/

# 验证导入
uv pip install -e .
python3 -c "from lansonai.vadtools import analyze; print('OK')"
```

### 2. 构建包

```bash
# 清理旧的构建文件
rm -rf dist/ build/ *.egg-info

# 构建包
uv build

# 检查构建产物
ls -lh dist/
```

### 3. 测试安装

```bash
# 从本地 wheel 文件安装测试
uv pip install dist/lansonai_vadtools-0.2.0-py3-none-any.whl

# 测试导入
python3 -c "from lansonai.vadtools import analyze; print('✅ Installed successfully')"
```

## 发布到 PyPI

### 使用 uv 发布

```bash
# 1. 确保已登录 PyPI（需要 API token）
# 创建 ~/.pypirc 或使用环境变量
export UV_PUBLISH_TOKEN="pypi-your-token-here"

# 2. 发布到 PyPI
uv publish

# 或指定文件
uv publish dist/lansonai_vadtools-0.2.0-py3-none-any.whl
```

### 使用 twine 发布（备选）

```bash
# 安装 twine
pip install twine

# 上传到 PyPI
twine upload dist/*

# 或先上传到 TestPyPI 测试
twine upload --repository testpypi dist/*
```

## 发布后验证

```bash
# 从 PyPI 安装
pip install lansonai-vadtools

# 测试导入和使用
python3 -c "
from lansonai.vadtools import analyze
print('✅ Package installed from PyPI')
print('Version:', __import__('lansonai.vadtools').__version__)
"
```

## 使用示例

安装后使用：

```python
from lansonai.vadtools import analyze

result = analyze(
    input_path="audio.wav",
    output_dir="./output",
    export_segments=True
)

print(f"检测到 {result['total_segments']} 个语音片段")
```

## 版本管理

更新版本号：

1. 编辑 `pyproject.toml` 中的 `version` 字段
2. 编辑 `lansonai/__init__.py` 中的 `__version__`
3. 编辑 `lansonai/vadtools/__init__.py` 中的 `__version__`
4. 重新构建和发布

## 注意事项

1. **命名空间包**: 包使用 `lansonai.vadtools` 命名空间，确保 `lansonai` 命名空间可用
2. **依赖**: 确保所有依赖在 PyPI 上可用
3. **README**: 确保 `README.md` 文件存在且格式正确
4. **许可证**: 当前设置为 MIT 许可证
5. **Python 版本**: 要求 Python >= 3.12

## 发布命令总结

```bash
# 完整发布流程
cd scripts/python/vad
rm -rf dist/ build/ *.egg-info
uv build
uv publish
```
