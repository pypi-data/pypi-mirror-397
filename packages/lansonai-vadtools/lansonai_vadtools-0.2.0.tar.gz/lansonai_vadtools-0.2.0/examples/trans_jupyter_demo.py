#%%
# %pip install uv
# %uv pip install pydub groq tqdm python-dotenv

#%%
# ==============================================================================
# CELL 1: 核心导入和依赖
# ==============================================================================
import asyncio
import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass

# 需要安装这些库:
# pip install pydub groq tqdm python-dotenv
from pydub import AudioSegment
from groq import AsyncGroq
from tqdm.asyncio import tqdm
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s', datefmt='%Y/%m/%d %H:%M:%S')

# 禁用 groq 库的默认日志记录器，避免重复输出
logging.getLogger("groq").setLevel(logging.WARNING)


#%%
# ==============================================================================
# CELL 2: 配置与数据结构
# ==============================================================================
# --- 配置 ---
# 从环境变量或直接在此处设置你的 GROQ API 密钥
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "YOUR_GROQ_API_KEY_HERE")

MODEL_NAME = 'whisper-large-v3-turbo'

vad_json_path = "/home/isakeem/Code/subtitle-storage-service/scripts/.output/vad/e699e1db-1714-4cb8-adde-5c6944800e78/timestamps.json"
max_segments_to_process = 5

# --- 性能与稳定性配置 ---
MAX_CONCURRENCY = 10       # 最大并发请求数，根据你的API限额调整
RETRY_ATTEMPTS = 3         # 单个分片失败后的最大重试次数
RETRY_DELAY_SECONDS = 5    # 每次重试前的等待时间（秒）

# --- TranscriptionConfig 类定义 ---
@dataclass
class TranscriptionConfig:
    # --- GROQ API 配置 ---
    groq_api_key: str = GROQ_API_KEY
    
    # --- Whisper 模型配置 ---
    model: str = MODEL_NAME
    
    # --- 语言配置 ---
    language: Optional[str] = "zh"
    
    # --- 性能和稳定性配置 ---
    max_concurrent: int = MAX_CONCURRENCY
    max_retries: int = RETRY_ATTEMPTS
    retry_delay: float = RETRY_DELAY_SECONDS
    timeout: int = 120

# --- 全局 logger 变量 ---
logger = logging.getLogger(__name__)


#%%
# ==============================================================================
# CELL 3: 核心转录函数
# ==============================================================================
async def transcribe_segment(
    async_client: AsyncGroq,
    semaphore: asyncio.Semaphore,
    file_path: str,
    segment_id: int,
    model: str,
    language: str,
    retry_attempts: int,
    retry_delay: int
) -> Optional[Dict[str, Any]]:
    """
    异步转写单个音频分片，包含重试和并发控制逻辑。
    """
    async with semaphore:
        for attempt in range(retry_attempts):
            try:
                logger.info(f"段 {segment_id}: 开始转录 (尝试 {attempt + 1}/{retry_attempts})")
                with open(file_path, "rb") as audio_file:
                    file_tuple = (os.path.basename(file_path), audio_file.read(), "audio/wav")

                transcription = await async_client.audio.transcriptions.create(
                    file=file_tuple,
                    model=model,
                    response_format="verbose_json",
                    language=language
                )
                
                logger.info(f"段 {segment_id}: 转录成功")
                return {
                    "segment_id": segment_id,
                    "transcription": transcription
                }
            
            except Exception as e:
                logger.warning(f"段 {segment_id}: 第 {attempt + 1}/{retry_attempts} 次尝试失败: {e}")
                if attempt < retry_attempts - 1:
                    await asyncio.sleep(retry_delay)
                else:
                    logger.error(f"段 {segment_id}: 在 {retry_attempts} 次尝试后彻底失败。")
                    return None
    return None


#%%
# ==============================================================================
# CELL 4: 主流程控制
# ==============================================================================

async def run_transcription_pipeline(vad_json_path: str, config: TranscriptionConfig, max_segments: int = 0):
    """
    执行完整的音频转录流程，包括断点续传和统一结果输出。
    """
    # 1. 确定唯一的输出文件路径，与输入文件同级
    transcription_path = os.path.join(os.path.dirname(vad_json_path), "transcription.json")

    logger.info(f"""
    开始转录管道:
      - 输入文件: {vad_json_path}
      - 状态与输出文件: {transcription_path}
      - 最大分段: {max_segments if max_segments > 0 else '全部'}
      - 模型: {config.model}
      - 并发数: {config.max_concurrent}
    """)

    # 2. 加载或创建转录状态文件
    if os.path.exists(transcription_path):
        logger.info("发现转录文件，将从上次中断处继续处理")
        with open(transcription_path, 'r', encoding='utf-8') as f:
            transcription_data = json.load(f)
    else:
        logger.info("未发现转录文件，将根据 timestamps.json 创建新文件")
        with open(vad_json_path, 'r') as f:
            vad_data = json.load(f)
        
        all_segments = vad_data.get('segments', [])
        transcription_data = {
            "full_text": "",
            "detected_language": None,
            "tasks": [
                {
                    "segment_id": seg['id'],
                    "file_path": seg['file_path'],
                    "start_time": seg['start_time'],
                    "end_time": seg['end_time'],
                    "duration": seg['end_time'] - seg['start_time'],
                    "status": "pending",
                    "text": "",
                    "detected_language": None,
                    "confidence": 0.0,
                    "error_message": "",
                    "retry_count": 0
                }
                for seg in all_segments
            ]
        }
        with open(transcription_path, 'w', encoding='utf-8') as f:
            json.dump(transcription_data, f, ensure_ascii=False, indent=4)
        logger.info(f"已创建新的转录文件，包含 {len(transcription_data['tasks'])} 个任务")

    # 3. 筛选需要处理的任务
    all_tasks = transcription_data.get('tasks', [])
    pending_or_failed_tasks = [task for task in all_tasks if task['status'] in ['pending', 'failed']]
    logger.info(f"找到 {len(pending_or_failed_tasks)} 个待处理的段")

    tasks_for_this_run = pending_or_failed_tasks
    if max_segments > 0:
        tasks_for_this_run = pending_or_failed_tasks[:max_segments]
        logger.info(f"根据 max_segments={max_segments} 的限制，本次将处理 {len(tasks_for_this_run)} 个段")

    valid_tasks_for_this_run = [task for task in tasks_for_this_run if os.path.exists(task['file_path'])]
    
    # 4. 执行转录
    if valid_tasks_for_this_run:
        logger.info(f"找到 {len(valid_tasks_for_this_run)} 个有效的音频段待处理")
        
        async_client = AsyncGroq(api_key=config.groq_api_key)
        semaphore = asyncio.Semaphore(config.max_concurrent)
        
        async_tasks = [
            transcribe_segment(
                async_client=async_client,
                semaphore=semaphore,
                file_path=task['file_path'],
                segment_id=task['segment_id'],
                model=config.model,
                language=config.language,
                retry_attempts=config.max_retries,
                retry_delay=config.retry_delay
            )
            for task in valid_tasks_for_this_run
        ]
        
        results = await tqdm.gather(*async_tasks, desc="转录进度")
        
        # 5. 更新任务状态
        successful_count = 0
        failed_count = 0
        for i, result in enumerate(results):
            processed_task_info = valid_tasks_for_this_run[i]
            segment_id = processed_task_info['segment_id']
            
            task_to_update = next((t for t in transcription_data["tasks"] if t["segment_id"] == segment_id), None)
            if not task_to_update:
                continue

            if result is None:
                task_to_update["status"] = "failed"
                task_to_update["error_message"] = "Max retries reached or unknown error"
                task_to_update["retry_count"] += 1
                failed_count += 1
            else:
                transcription = result["transcription"]
                task_to_update["status"] = "completed"
                task_to_update["text"] = transcription.text
                task_to_update["detected_language"] = getattr(transcription, 'language', None)
                task_to_update["confidence"] = getattr(transcription, 'confidence', 0.0)
                successful_count += 1
        
        logger.info(f"本轮转录完成: 成功 {successful_count} 个，失败 {failed_count} 个")

    else:
        logger.info("没有新的音频段需要处理。")

    # 6. 更新 full_text 并保存最终结果
    completed_tasks = sorted(
        [task for task in transcription_data["tasks"] if task["status"] == "completed"],
        key=lambda x: x["segment_id"]
    )
    transcription_data["full_text"] = " ".join(task["text"] for task in completed_tasks)
    
    with open(transcription_path, 'w', encoding='utf-8') as f:
        json.dump(transcription_data, f, ensure_ascii=False, indent=4)
    
    logger.info(f"转录流程结束，结果已统一保存至: {transcription_path}")
    return transcription_path


#%%
# ==============================================================================
# CELL 5: 脚本执行入口
# ==============================================================================
# 检查是否在 Jupyter 环境中运行
try:
    get_ipython()
    # 在 Jupyter 中运行
    print("在 Jupyter 环境中运行, 请手动执行以下代码:")
    print(f"# await run_transcription_pipeline(vad_json_path, TranscriptionConfig(), {max_segments_to_process})")
except NameError:
    # 直接运行脚本
    if __name__ == "__main__":
        asyncio.run(run_transcription_pipeline(vad_json_path, TranscriptionConfig(), max_segments_to_process))