import aiofiles
import os
from pathlib import Path
from typing import Optional
from datetime import datetime

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from lansonai.vadtools.config.settings import TEMP_DIR
from lansonai.vadtools.core.utils import log_message, get_current_time

async def process_audio_file(file: 'UploadFile', temp_file_path: Path) -> Path:
    """
    处理上传的音频文件：保存到临时目录，支持WAV/MP3等格式
    temp_file_path 应包含 request_id_ 前缀，如 {request_id}_{original_filename}
    """
    current_time = get_current_time()
    
    # 确保临时目录存在 (settings.py已验证，但这里额外检查)
    os.makedirs(TEMP_DIR, exist_ok=True)
    if not os.access(TEMP_DIR, os.R_OK | os.W_OK | os.X_OK):
        raise PermissionError(f"临时目录 {TEMP_DIR} 权限不足，无法保存文件")
    
    # 提取 request_id 和原始文件名用于日志
    request_id = "unknown"
    original_filename = file.filename or "unknown_audio"
    if "_" in temp_file_path.stem:
        request_id = temp_file_path.stem.split("_")[0]
    
    log_message(f"保存上传文件 {original_filename} 到 {temp_file_path} (request_id: {request_id})")
    
    try:
        # 验证文件大小和类型 (可选安全检查)
        if not file.filename:
            raise ValueError("上传文件缺少文件名")
        
        file_ext = original_filename.split('.')[-1].lower() if '.' in original_filename else 'wav'
        if file_ext not in ['wav', 'mp3', 'm4a', 'flac', 'ogg']:
            log_message(f"文件扩展名 {file_ext} 非标准音频格式，但继续处理", "WARNING")
        
        # 异步保存文件内容
        async with aiofiles.open(temp_file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # 验证文件保存成功
        if not temp_file_path.exists():
            raise ValueError(f"文件保存失败: {temp_file_path} 不存在")
        
        if temp_file_path.stat().st_size == 0:
            raise ValueError("文件保存成功但大小为0，可能是空文件")
        
        file_size = temp_file_path.stat().st_size
        log_message(f"音频文件 {original_filename} 保存成功，大小: {file_size} bytes, 路径: {temp_file_path} (request_id: {request_id})")
        
        return temp_file_path
        
    except Exception as e:
        log_message(f"保存音频文件 {original_filename} 失败到 {temp_file_path}: {str(e)} (request_id: {request_id})", "ERROR")
        # 清理失败的文件
        if temp_file_path.exists():
            try:
                temp_file_path.unlink(missing_ok=True)
                log_message(f"清理失败的临时文件: {temp_file_path}")
            except Exception as cleanup_e:
                log_message(f"清理失败文件时出错: {str(cleanup_e)}", "WARNING")
        raise

async def convert_audio_format(input_path: Path, output_path: Path, target_format: str = 'wav') -> Path:
    """
    转换音频格式到目标格式 (占位实现，实际集成ffmpeg或pydub)
    注意：生产环境需替换为实际音频转换库
    """
    log_message(f"开始转换音频格式 {input_path} -> {output_path} (target_format: {target_format})")
    
    if not input_path.exists():
        raise FileNotFoundError(f"输入音频文件不存在: {input_path}")
    
    # 确保输出目录存在
    os.makedirs(output_path.parent, exist_ok=True)
    
    try:
        # 占位实现：复制文件 (实际应使用 ffmpeg-python 或 pydub)
        import shutil
        shutil.copy2(input_path, output_path)
        
        # 实际转换示例 (注释，需安装对应库)
        # import ffmpeg
        # stream = ffmpeg.input(str(input_path))
        # if target_format == 'wav':
        #     stream = ffmpeg.output(stream, str(output_path), acodec='pcm_s16le', ar=16000)
        # ffmpeg.run(stream, overwrite_output=True, quiet=True, capture_stdout=True, capture_stderr=True)
        
        if not output_path.exists():
            raise ValueError(f"音频转换失败: 输出文件 {output_path} 不存在")
        
        output_size = output_path.stat().st_size
        log_message(f"音频格式转换完成: {input_path} -> {output_path}, 大小: {output_size} bytes")
        return output_path
        
    except Exception as e:
        log_message(f"音频格式转换失败 {input_path} -> {output_path}: {str(e)}", "ERROR")
        # 清理失败的输出文件
        if output_path.exists():
            output_path.unlink(missing_ok=True)
        raise

def get_supported_formats() -> list:
    """返回支持的音频输入格式"""
    return ['wav', 'mp3', 'm4a', 'flac', 'ogg']

def get_output_formats() -> list:
    """返回支持的输出格式"""
    return ['wav', 'flac']

def is_video_file(file_path: Path) -> bool:
    """判断文件是否为视频文件"""
    video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm', '.m4v'}
    return file_path.suffix.lower() in video_extensions

def extract_audio_from_video(video_path: Path, output_audio_path: Path) -> Path:
    """
    从视频文件提取音频到指定路径
    
    Args:
        video_path: 视频文件路径
        output_audio_path: 输出音频文件路径（WAV格式）
    
    Returns:
        输出音频文件路径
    
    Raises:
        RuntimeError: 如果 ffmpeg 提取失败
    """
    import subprocess
    
    log_message(f"Extracting audio from video: {video_path} -> {output_audio_path}")
    
    # 确保输出目录存在
    output_audio_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # 使用 ffmpeg 提取音频：16kHz 采样率，单声道，WAV格式
        cmd = [
            'ffmpeg',
            '-i', str(video_path),
            '-ar', '16000',  # 采样率
            '-ac', '1',      # 单声道
            '-y',            # 覆盖输出文件
            str(output_audio_path)
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        if not output_audio_path.exists() or output_audio_path.stat().st_size == 0:
            raise RuntimeError(f"Audio extraction failed: output file is empty")
        
        log_message(f"Audio extracted successfully: {output_audio_path}")
        return output_audio_path
        
    except subprocess.CalledProcessError as e:
        error_msg = f"ffmpeg failed: {e.stderr}"
        log_message(f"{error_msg} (video: {video_path}, output: {output_audio_path})", "ERROR")
        log_message(f"ffmpeg command: {' '.join(cmd)}", "ERROR")
        raise RuntimeError(f"Failed to extract audio from video: {error_msg}")
    except FileNotFoundError:
        error_msg = "ffmpeg not found. Please install ffmpeg to process video files."
        log_message(error_msg, "ERROR")
        raise RuntimeError(error_msg)

def process_audio_file_path(audio_path: Path) -> Path:
    """
    处理本地音频文件路径（用于CLI）
    验证文件存在性和可读性，直接返回路径
    """
    current_time = get_current_time()
    
    if not audio_path.exists():
        raise FileNotFoundError(f"音频文件不存在: {audio_path}")
    
    if not audio_path.is_file():
        raise ValueError(f"不是有效文件: {audio_path}")
    
    if not os.access(audio_path, os.R_OK):
        raise PermissionError(f"音频文件无法读取: {audio_path}")
    
    # 检查文件大小
    file_size = audio_path.stat().st_size
    if file_size == 0:
        raise ValueError(f"音频文件为空: {audio_path}")
    
    # 检查文件扩展名（可选的格式验证）
    supported_extensions = {'.wav', '.mp3', '.m4a', '.flac', '.ogg', '.aac'}
    if audio_path.suffix.lower() not in supported_extensions:
        log_message(f"音频格式可能不被支持: {audio_path.suffix}", "WARNING")

    log_message(f"本地音频文件验证通过: {audio_path}, 大小: {file_size} 字节")
    
    return audio_path
