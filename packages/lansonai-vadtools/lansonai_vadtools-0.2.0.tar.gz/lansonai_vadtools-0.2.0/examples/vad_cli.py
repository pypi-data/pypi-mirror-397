#!/usr/bin/env python3
"""
VAD Command Line Interface
可以直接调用的VAD分析脚本，接受本地文件路径和参数
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Optional

# 添加项目路径以导入包
sys.path.insert(0, str(Path(__file__).parent.parent))

from lansonai.vadtools import analyze
from lansonai.vadtools.config.settings import OUTPUT_DIR, validate_and_create_dirs
from lansonai.vadtools.core.utils import log_message

def analyze_audio_file(
    audio_path: str,
    threshold: float = 0.3,
    min_segment_duration: float = 0.5,
    max_merge_gap: float = 0.2,
    export_audio_segments: bool = False,
    output_format: str = "wav",
    request_id: Optional[str] = None,
    output_dir: Optional[str] = None
):
    """
    分析单个音频/视频文件的VAD（向后兼容的包装函数）
    
    使用新的包 API 实现
    """
    # 设置输出目录（向后兼容：如果没有提供，使用默认目录）
    if not output_dir:
        output_dir = OUTPUT_DIR
    
    # 调用新的包 API
    result = analyze(
        input_path=audio_path,
        output_dir=output_dir,
        threshold=threshold,
        min_segment_duration=min_segment_duration,
        max_merge_gap=max_merge_gap,
        export_segments=export_audio_segments,
        output_format=output_format,
        request_id=request_id
    )
    
    # 适配返回格式以保持向后兼容
    result['timestamps_path'] = result['json_path']
    result['output_directory'] = result['output_dir']
    result['audio_duration'] = result.get('total_duration', 0.0)
    result['processing_time'] = result['performance'].get('total_processing_time', 0.0)
    
    return result

def main():
    """命令行主函数"""
    parser = argparse.ArgumentParser(
        description="Voice Activity Detection (VAD) CLI tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/audio.wav
  %(prog)s /path/to/audio.mp3 --threshold 0.4 --min-duration 1.0
  %(prog)s /path/to/audio.m4a --export-segments --format flac
  %(prog)s /path/to/audio.wav --output-dir /custom/output --request-id my-task-123
        """
    )
    
    parser.add_argument('audio_path', help='Path to the audio file to analyze')
    
    parser.add_argument('--threshold', type=float, default=0.3,
                        help='VAD detection threshold (0.0-1.0, default: 0.3)')
    
    parser.add_argument('--min-duration', type=float, default=0.5,
                        help='Minimum segment duration in seconds (default: 0.5)')
    
    parser.add_argument('--max-merge-gap', type=float, default=0.2,
                        help='Maximum gap to merge segments in seconds (default: 0.2)')
    
    parser.add_argument('--export-segments', action='store_true',
                        help='Export individual audio segments')
    
    parser.add_argument('--format', choices=['wav', 'flac'], default='wav',
                        help='Output format for audio segments (default: wav)')
    
    parser.add_argument('--request-id', type=str,
                        help='Custom request ID (auto-generated if not provided)')
    
    parser.add_argument('--output-dir', type=str,
                        help='Custom output directory (uses default if not provided)')
    
    parser.add_argument('--json', action='store_true',
                        help='Output results as JSON (instead of human-readable format)')
    
    parser.add_argument('--quiet', '-q', action='store_true',
                        help='Suppress progress messages (only show errors)')
    
    args = parser.parse_args()
    
    # 设置静默模式
    if args.quiet:
        import logging
        logging.getLogger().setLevel(logging.ERROR)
    
    try:
        # 验证并创建目录
        validate_and_create_dirs()
        
        # 执行VAD分析
        result = analyze_audio_file(
            audio_path=args.audio_path,
            threshold=args.threshold,
            min_segment_duration=args.min_duration,
            max_merge_gap=args.max_merge_gap,
            export_audio_segments=args.export_segments,
            output_format=args.format,
            request_id=args.request_id,
            output_dir=args.output_dir
        )
        
        if args.json:
            # JSON输出
            print(json.dumps(result, indent=2, default=str))
        else:
            # 人类可读输出
            print("\n" + "="*60)
            print("VAD ANALYSIS RESULTS")
            print("="*60)
            print(f"Request ID: {result['request_id']}")
            print(f"Total segments: {result['total_segments']}")
            print(f"Audio duration: {result.get('total_duration', 'N/A')}s")
            print(f"Total voice duration: {result['summary'].get('total_speech_duration', 0)}s")
            print(f"Speech ratio: {result.get('overall_speech_ratio', 0) * 100:.1f}%")
            print(f"Processing time: {result['performance'].get('total_processing_time', 'N/A')}s")
            print(f"Results saved to: {result['json_path']}")
            
            if result.get('segments_dir'):
                print(f"Audio segments exported to: {result['segments_dir']}")
        
        return 0
        
    except KeyboardInterrupt:
        log_message("Operation cancelled by user")
        return 1
    except Exception as e:
        log_message(f"{str(e)}", "ERROR")
        if not args.quiet:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
