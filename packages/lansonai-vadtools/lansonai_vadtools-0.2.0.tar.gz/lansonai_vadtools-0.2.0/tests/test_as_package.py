#!/usr/bin/env python3
"""
模拟作为 Python 包使用的测试脚本
演示如何像使用标准包一样导入和使用 vad
"""

import sys
from pathlib import Path

# 添加项目路径以便导入包
sys.path.insert(0, str(Path(__file__).parent.parent))

# 像使用标准包一样导入
from vad import analyze

def test_as_package():
    """测试作为包使用"""
    print("=" * 60)
    print("Testing VAD as a Python Package")
    print("=" * 60)
    
    # 测试文件路径
    audio_file = Path("/Users/clay/Code/subtitle-storage-service/data/temp/uploads/09f6644a73524f53a709f7509a5793af.mp3")
    output_dir = Path("./test_package_output")
    
    if not audio_file.exists():
        print(f"❌ Test file not found: {audio_file}")
        print("Please provide a valid audio file path")
        return False
    
    print(f"\n📁 Input file: {audio_file}")
    print(f"📁 Output directory: {output_dir}")
    print(f"📊 File size: {audio_file.stat().st_size / 1024 / 1024:.2f} MB")
    
    try:
        # 使用包 API - 就像使用任何标准 Python 包一样
        print("\n🚀 Starting VAD analysis...")
        result = analyze(
            input_path=str(audio_file),
            output_dir=str(output_dir),
            threshold=0.3,
            min_segment_duration=0.5,
            max_merge_gap=0.2,
            export_segments=True,
            output_format="wav",
            request_id=None  # 自动生成
        )
        
        # 处理结果
        print("\n✅ Analysis completed!")
        print("\n📊 Results:")
        print(f"  Request ID: {result['request_id']}")
        print(f"  Total segments: {result['total_segments']}")
        print(f"  Total duration: {result['total_duration']:.2f}s")
        print(f"  Speech duration: {result['summary']['total_speech_duration']:.2f}s")
        print(f"  Speech ratio: {result['overall_speech_ratio'] * 100:.1f}%")
        print(f"  Processing time: {result['performance']['total_processing_time']:.2f}s")
        print(f"  Speed ratio: {result['performance']['speed_ratio']:.1f}x")
        
        print(f"\n📁 Output files:")
        print(f"  JSON result: {result['json_path']}")
        if result.get('segments_dir'):
            print(f"  Segments dir: {result['segments_dir']}")
            segments_dir = Path(result['segments_dir'])
            if segments_dir.exists():
                segment_count = len(list(segments_dir.glob("segment_*.wav")))
                print(f"  Segments created: {segment_count}")
        
        # 验证输出文件
        json_path = Path(result['json_path'])
        if json_path.exists():
            json_size = json_path.stat().st_size
            print(f"  JSON file size: {json_size / 1024:.1f} KB")
        
        print("\n🎉 Package usage test passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_different_scenarios():
    """测试不同的使用场景"""
    print("\n" + "=" * 60)
    print("Testing Different Usage Scenarios")
    print("=" * 60)
    
    audio_file = Path("/Users/clay/Code/subtitle-storage-service/data/temp/uploads/09f6644a73524f53a709f7509a5793af.mp3")
    
    if not audio_file.exists():
        print("⏭️  Skipping scenarios test (test file not found)")
        return
    
    scenarios = [
        {
            "name": "Minimal parameters",
            "params": {
                "input_path": str(audio_file),
                "output_dir": "./test_scenario1"
            }
        },
        {
            "name": "High threshold (strict)",
            "params": {
                "input_path": str(audio_file),
                "output_dir": "./test_scenario2",
                "threshold": 0.5,
                "export_segments": False
            }
        },
        {
            "name": "Low threshold (loose)",
            "params": {
                "input_path": str(audio_file),
                "output_dir": "./test_scenario3",
                "threshold": 0.2,
                "export_segments": True,
                "output_format": "flac"
            }
        },
        {
            "name": "Custom request ID",
            "params": {
                "input_path": str(audio_file),
                "output_dir": "./test_scenario4",
                "request_id": "custom-test-id-123"
            }
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📝 Scenario {i}: {scenario['name']}")
        try:
            result = analyze(**scenario['params'])
            print(f"  ✅ Success: {result['total_segments']} segments detected")
        except Exception as e:
            print(f"  ❌ Failed: {e}")


def test_batch_processing():
    """演示批量处理（调用方自己控制）"""
    print("\n" + "=" * 60)
    print("Testing Batch Processing Pattern")
    print("=" * 60)
    
    # 模拟多个文件
    test_files = [
        "/Users/clay/Code/subtitle-storage-service/data/temp/uploads/09f6644a73524f53a709f7509a5793af.mp3"
    ]
    
    # 可以扩展为多个文件
    # test_files = [
    #     "file1.wav",
    #     "file2.mp3",
    #     "file3.mp4"
    # ]
    
    print(f"📦 Processing {len(test_files)} file(s)...")
    
    results = []
    for i, file_path in enumerate(test_files, 1):
        file = Path(file_path)
        if not file.exists():
            print(f"  ⏭️  File {i}: {file.name} - not found, skipping")
            continue
        
        try:
            print(f"  🔄 Processing {i}/{len(test_files)}: {file.name}")
            result = analyze(
                input_path=str(file),
                output_dir=f"./test_batch_output",
                export_segments=True
            )
            results.append({
                "file": file.name,
                "segments": result['total_segments'],
                "speech_ratio": result['overall_speech_ratio'],
                "status": "success"
            })
            print(f"     ✅ {result['total_segments']} segments, {result['overall_speech_ratio']*100:.1f}% speech")
        except Exception as e:
            results.append({
                "file": file.name,
                "status": "failed",
                "error": str(e)
            })
            print(f"     ❌ Failed: {e}")
    
    print(f"\n📊 Batch processing summary:")
    print(f"  Total files: {len(test_files)}")
    print(f"  Successful: {sum(1 for r in results if r['status'] == 'success')}")
    print(f"  Failed: {sum(1 for r in results if r['status'] == 'failed')}")


if __name__ == "__main__":
    print("\n🧪 VAD Package Usage Simulation")
    print("This script demonstrates how to use the VAD package")
    print("as a standard Python package.\n")
    
    # 基础使用测试
    success = test_as_package()
    
    if success:
        # 不同场景测试
        test_different_scenarios()
        
        # 批量处理演示
        test_batch_processing()
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)
