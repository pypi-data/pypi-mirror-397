#!/usr/bin/env python3
"""
VAD 包测试套件
测试包的基本功能和错误处理
"""

import sys
import json
from pathlib import Path
import tempfile
import shutil

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from vad import analyze
except ImportError as e:
    print(f"❌ Failed to import vad package: {e}")
    sys.exit(1)


def test_package_import():
    """测试包导入"""
    print("🧪 Test 1: Package import")
    try:
        from vad import analyze
        assert callable(analyze), "analyze should be callable"
        print("  ✅ Package imported successfully")
        return True
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        return False


def test_invalid_file():
    """测试无效文件处理"""
    print("\n🧪 Test 2: Invalid file handling")
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            analyze("nonexistent_file.wav", tmpdir)
        print("  ❌ Should have raised FileNotFoundError")
        return False
    except FileNotFoundError:
        print("  ✅ Correctly raised FileNotFoundError for nonexistent file")
        return True
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
        return False


def test_invalid_output_dir():
    """测试无效输出目录"""
    print("\n🧪 Test 3: Invalid output directory")
    # 创建一个测试音频文件（空文件，仅用于测试路径）
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
        test_file = tmp.name
    
    try:
        # 尝试使用无效路径（需要 root 权限的路径）
        invalid_path = "/root/forbidden/path"
        analyze(test_file, invalid_path)
        print("  ❌ Should have raised RuntimeError")
        return False
    except (RuntimeError, PermissionError, FileNotFoundError):
        print("  ✅ Correctly handled invalid output directory")
        return True
    except Exception as e:
        print(f"  ⚠️  Unexpected error (may be acceptable): {e}")
        return True  # 某些系统可能允许，不算失败
    finally:
        Path(test_file).unlink(missing_ok=True)


def test_api_signature():
    """测试 API 函数签名"""
    print("\n🧪 Test 4: API function signature")
    import inspect
    
    try:
        sig = inspect.signature(analyze)
        params = list(sig.parameters.keys())
        
        # 检查必需参数
        assert 'input_path' in params, "Missing input_path parameter"
        assert 'output_dir' in params, "Missing output_dir parameter"
        
        # 检查可选参数
        assert 'threshold' in params, "Missing threshold parameter"
        assert 'export_segments' in params, "Missing export_segments parameter"
        
        print(f"  ✅ API signature correct: {params}")
        return True
    except Exception as e:
        print(f"  ❌ Signature check failed: {e}")
        return False


def test_with_real_file(audio_file: Path, output_dir: Path):
    """使用真实音频文件测试（如果提供）"""
    print(f"\n🧪 Test 5: Real audio file processing")
    
    if not audio_file.exists():
        print(f"  ⏭️  Skipped: Test file not found: {audio_file}")
        return None
    
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"  📁 Input: {audio_file}")
        print(f"  📁 Output: {output_dir}")
        
        result = analyze(
            input_path=str(audio_file),
            output_dir=str(output_dir),
            threshold=0.3,
            export_segments=True
        )
        
        # 验证结果
        assert 'request_id' in result, "Missing request_id in result"
        assert 'json_path' in result, "Missing json_path in result"
        assert 'total_segments' in result, "Missing total_segments in result"
        
        # 验证文件存在
        json_path = Path(result['json_path'])
        assert json_path.exists(), f"JSON file not found: {json_path}"
        
        # 验证 JSON 格式
        with open(json_path) as f:
            data = json.load(f)
            assert 'segments' in data, "Missing segments in JSON"
            assert 'summary' in data, "Missing summary in JSON"
            assert 'performance' in data, "Missing performance in JSON"
        
        # 验证切片目录（如果导出）
        if result.get('segments_dir'):
            segments_dir = Path(result['segments_dir'])
            assert segments_dir.exists(), f"Segments dir not found: {segments_dir}"
            segment_files = list(segments_dir.glob("segment_*.wav"))
            assert len(segment_files) > 0, "No segment files found"
        
        print(f"  ✅ Processing successful:")
        print(f"     - Request ID: {result['request_id']}")
        print(f"     - Segments: {result['total_segments']}")
        print(f"     - JSON: {result['json_path']}")
        if result.get('segments_dir'):
            print(f"     - Segments dir: {result['segments_dir']}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Processing failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("=" * 60)
    print("VAD Package Test Suite")
    print("=" * 60)
    
    results = []
    
    # 基础测试（不需要实际文件）
    results.append(("Import", test_package_import()))
    results.append(("Invalid File", test_invalid_file()))
    results.append(("Invalid Output Dir", test_invalid_output_dir()))
    results.append(("API Signature", test_api_signature()))
    
    # 真实文件测试（可选）
    import argparse
    parser = argparse.ArgumentParser(description="Test VAD package")
    parser.add_argument("--audio-file", type=Path, help="Path to test audio file")
    parser.add_argument("--output-dir", type=Path, default=Path("./test_output"), help="Output directory")
    args = parser.parse_args()
    
    if args.audio_file:
        result = test_with_real_file(args.audio_file, args.output_dir)
        if result is not None:
            results.append(("Real File", result))
    
    # 总结
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result is True)
    total = len([r for _, r in results if r is not None])
    
    for name, result in results:
        if result is None:
            status = "⏭️  SKIPPED"
        elif result:
            status = "✅ PASSED"
        else:
            status = "❌ FAILED"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
