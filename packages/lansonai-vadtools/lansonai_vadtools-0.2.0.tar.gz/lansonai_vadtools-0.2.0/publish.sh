#!/bin/bash
# 发布 lansonai-vadtools 到 PyPI

set -e

echo "🚀 Publishing lansonai-vadtools to PyPI"
echo "========================================"

# 检查是否在正确目录
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Please run this script from scripts/python/vad directory"
    exit 1
fi

# 清理旧的构建文件
echo ""
echo "🧹 Cleaning old build files..."
rm -rf dist/ build/ *.egg-info

# 构建包
echo ""
echo "🔨 Building package..."
uv build

# 检查构建产物
echo ""
echo "📦 Build artifacts:"
ls -lh dist/

# 显示包信息
echo ""
echo "📋 Package info:"
grep -E "^name =|^version =|^description =" pyproject.toml | sed 's/^/  /' || {
    echo "  Name: lansonai-vadtools"
    echo "  Version: 0.2.0"
    echo "  Description: Voice Activity Detection (VAD) package"
}

# 询问是否发布
echo ""
read -p "📤 Publish to PyPI? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "⏭️  Publishing cancelled"
    exit 0
fi

# 发布
echo ""
echo "🚀 Publishing to PyPI..."
if command -v uv &> /dev/null; then
    uv publish
else
    echo "⚠️  uv not found, using twine..."
    pip install twine
    twine upload dist/*
fi

echo ""
echo "✅ Published successfully!"
echo ""
echo "📦 Install with: pip install lansonai-vadtools"
echo "📖 Use with: from lansonai.vadtools import analyze"
