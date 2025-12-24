import os
from pathlib import Path
from typing import Optional
from datetime import datetime

# 项目根目录：相对于当前文件的三级父目录 (vad -> scripts/python/vad -> scripts/python -> scripts -> 项目根)
project_root = Path(__file__).parent.parent.parent.parent

# 默认临时目录：项目根/.temp/vad，用于上传、转换和中间文件
TEMP_DIR = project_root / ".temp" / "vad"

# 默认输出目录：项目根/data/.output/vad，用于持久化输出 (segments WAV/FLAC, timestamps.json)
# 说明：放到 data/ 下更符合运行时产物（并且更容易被部署/卷挂载策略识别）
OUTPUT_DIR = project_root / "data" / ".output" / "vad"

# 支持环境变量覆盖
TEMP_DIR = Path(os.getenv("TEMP_DIR", str(TEMP_DIR)))
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", str(OUTPUT_DIR)))

# VAD处理配置 (默认值，可通过API参数覆盖)
SAMPLE_RATE = 16000
MIN_SEGMENT_DURATION = 0.1  # 秒
SILENCE_THRESHOLD = 0.3  # 比例阈值 (对应dB计算)
SILENCE_DURATION = 0.5  # 秒 (max_merge_gap相关)

# 日志配置
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Modal部署特定配置
MODAL_VOLUME_PATH = os.getenv("MODAL_VOLUME_PATH", "/volumes/vad_storage")

def get_current_time() -> str:
    """获取当前时间，格式 YYYY/MM/DD HH:mm:ss"""
    return datetime.now().strftime("%Y/%m/%d %H:%M:%S")

def log_message(message: str, level: str = "INFO") -> None:
    """记录日志消息，格式 [时间] LEVEL - 消息 (延迟导入utils)"""
    from lansonai.vadtools.core.utils import log_message as utils_log
    current_time = get_current_time()
    utils_log(f"[{current_time}] {level} - {message}")

def validate_and_create_dirs() -> None:
    """
    验证并创建目录，确保读写执行权限
    使用utils.log_message报告详细事件，如创建成功、权限状态、失败错误
    """
    current_time_str = get_current_time()
    
    global TEMP_DIR, OUTPUT_DIR
    
    # 验证临时目录
    temp_success = False
    try:
        log_message(f"验证临时目录 {TEMP_DIR}: 开始检查和创建", "INFO")
        
        # 创建目录
        os.makedirs(TEMP_DIR, exist_ok=True)
        
        # 检查存在性
        if not TEMP_DIR.exists():
            raise OSError(f"临时目录 {TEMP_DIR} 创建后仍不存在")
        
        # 检查权限
        readable = os.access(TEMP_DIR, os.R_OK)
        writable = os.access(TEMP_DIR, os.W_OK)
        executable = os.access(TEMP_DIR, os.X_OK)
        
        if not (readable and writable and executable):
            raise PermissionError(f"临时目录 {TEMP_DIR} 权限不足 (r={readable}, w={writable}, x={executable})")
        
        temp_success = True
        log_message(f"验证临时目录 {TEMP_DIR}: 创建成功, 权限 rwx (exists=True, readable={readable}, writable={writable}, executable={executable})", "INFO")
        
    except (OSError, PermissionError) as e:
        error_msg = f"临时目录 {TEMP_DIR} 验证失败: {str(e)}"
        log_message(error_msg, "ERROR")
        
        # 回退到项目根目录下的 .temp/vad_fallback
        fallback_dir = project_root / ".temp" / "vad_fallback"
        try:
            os.makedirs(fallback_dir, exist_ok=True)
            
            TEMP_DIR = fallback_dir
            fallback_readable = os.access(TEMP_DIR, os.R_OK)
            fallback_writable = os.access(TEMP_DIR, os.W_OK)
            fallback_executable = os.access(TEMP_DIR, os.X_OK)
            log_message(f"回退到临时目录 {TEMP_DIR}: 创建成功, 权限 rwx (readable={fallback_readable}, writable={fallback_writable}, executable={fallback_executable})", "INFO")
            temp_success = True
        except Exception as fallback_e:
            log_message(f"回退目录 {fallback_dir} 也失败: {str(fallback_e)}", "ERROR")
            raise RuntimeError(f"无法设置任何临时目录: {error_msg}, fallback: {str(fallback_e)}")
    
    if not temp_success:
        raise RuntimeError(f"临时目录验证最终失败: {TEMP_DIR}")
    
    # 验证输出目录 (不回退，失败时抛出异常)
    output_success = False
    try:
        log_message(f"验证输出目录 {OUTPUT_DIR}: 开始检查和创建", "INFO")
        
        # 创建目录
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # 检查存在性
        if not OUTPUT_DIR.exists():
            raise OSError(f"输出目录 {OUTPUT_DIR} 创建后仍不存在")
        
        # 检查权限
        readable = os.access(OUTPUT_DIR, os.R_OK)
        writable = os.access(OUTPUT_DIR, os.W_OK)
        executable = os.access(OUTPUT_DIR, os.X_OK)
        
        if not (readable and writable and executable):
            raise PermissionError(f"输出目录 {OUTPUT_DIR} 权限不足 (r={readable}, w={writable}, x={executable})")
        
        output_success = True
        log_message(f"验证输出目录 {OUTPUT_DIR}: 创建成功, 权限 rwx (exists=True, readable={readable}, writable={writable}, executable={executable})", "INFO")
        
    except (OSError, PermissionError) as e:
        error_msg = f"输出目录 {OUTPUT_DIR} 验证失败: {str(e)}"
        log_message(error_msg, "ERROR")
        raise RuntimeError(error_msg)
    
    if not output_success:
        raise RuntimeError(f"输出目录验证失败: {OUTPUT_DIR}")
    
    # 最终确认
    log_message(f"所有目录验证完成: TEMP_DIR={TEMP_DIR} (成功), OUTPUT_DIR={OUTPUT_DIR} (成功)", "INFO")

# 初始化时调用验证 (在 main.py startup 中显式调用)
# validate_and_create_dirs()  # 注释掉，避免模块导入时自动执行