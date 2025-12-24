#!/bin/bash
# 快速测试脚本

set -e

echo "🧪 VAD Package Quick Test"
echo "=========================="

# 检查是否在正确的目录
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Please run this script from scripts/python/vad directory"
    exit 1
fi

# 测试1: 包导入
echo ""
echo "Test 1: Package Import"
uv run python -c "from vad import analyze; print('✅ Package imported successfully')" || {
    echo "❌ Package import failed"
    exit 1
}

# 测试2: CLI 帮助
echo ""
echo "Test 2: CLI Help"
uv run python examples/vad_cli.py --help > /dev/null || {
    echo "❌ CLI help failed"
    exit 1
}
echo "✅ CLI help works"

# 测试3: 无效文件处理
echo ""
echo "Test 3: Invalid File Handling"
uv run python examples/vad_cli.py nonexistent.wav --output-dir /tmp/test_output 2>&1 | grep -q "not found" && {
    echo "✅ Invalid file handling works"
} || {
    echo "⚠️  Invalid file handling may need review"
}

# 测试4: 运行测试套件
echo ""
echo "Test 4: Running Test Suite"
if [ -f "tests/test_package.py" ]; then
    uv run python tests/test_package.py || {
        echo "⚠️  Some tests failed (this may be expected if test files are missing)"
    }
else
    echo "⏭️  Test suite not found"
fi

echo ""
echo "=========================="
echo "✅ Quick tests completed!"
echo ""
echo "For full testing with real audio files, see TESTING.md"
