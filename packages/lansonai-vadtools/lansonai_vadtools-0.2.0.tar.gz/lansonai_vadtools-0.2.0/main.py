import os
import uuid
import re
import time
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, UploadFile, File, HTTPException, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from pathlib import Path
import asyncio
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field
import torch
import librosa
from config.settings import (
    TEMP_DIR,
    OUTPUT_DIR,
    SAMPLE_RATE
)
from core.vad_detector import detect_vad_segments, export_segments
from core.utils import log_message, get_current_time, save_timestamps
from utils.vad_data_processor import process_single_timestamps_file


class VADSegment(BaseModel):
    """语音段数据模型"""
    start_time: float
    end_time: float
    duration: float


class AudioSegment(BaseModel):
    """音频段文件信息模型"""
    start_time: float
    end_time: float
    duration: float
    source_url: str
    rms: float = Field(0.0, description="RMS amplitude")
    peak_amplitude: float = Field(0.0, description="Peak amplitude")
    speech_confidence: float = Field(0.8, description="Speech confidence score")


class Metadata(BaseModel):
    source_file: str
    run_id: str
    processing_date: str
    parameters: Dict[str, Any]


class Performance(BaseModel):
    total_processing_time: float
    audio_loading_time: float
    stage1_vad_timestamps_time: float
    stage2_feature_extraction_time: float
    speed_ratio: float


class Summary(BaseModel):
    total_speech_duration: float


class VADResponse(BaseModel):
    """VAD分析响应模型，与保存的JSON结构一致"""
    request_id: str
    total_segments: int
    total_duration: float
    overall_speech_ratio: Optional[float] = Field(None, description="Overall speech ratio")
    timestamps_path: str
    metadata: Metadata
    performance: Performance
    summary: Summary
    segments: List[VADSegment]
    audio_segments: List[AudioSegment]


@asynccontextmanager
async def lifespan(app: FastAPI):
    log_message("VAD service starting...")

    try:
        from config.settings import validate_and_create_dirs
        validate_and_create_dirs()
        log_message(f"Directory validation complete, temp_dir: {TEMP_DIR}, output_dir: {OUTPUT_DIR}")
    except Exception as e:
        log_message(f"Directory validation failed: {str(e)}", "ERROR")
        raise RuntimeError(f"Directory validation failed: {str(e)}")

    try:
        log_message("Loading Silero VAD model...")
        # 优化建议: 启用 ONNX 以获得更快的推理速度。需要 `pip install onnxruntime`。
        (model, utils) = torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad', force_reload=False, onnx=True, verbose=False)
        get_speech_timestamps = utils[0]
        app.state.vad_model = model
        app.state.get_speech_timestamps = get_speech_timestamps
        log_message("Silero VAD model loaded successfully (ONNX enabled)")
    except Exception as e:
        log_message(f"Silero VAD model load failed: {str(e)}", "ERROR")
        raise RuntimeError(f"Model load failed: {str(e)}")

    log_message("VAD service started successfully")
    yield
    log_message("VAD service shutting down")


app = FastAPI(title="VAD Subtitle Storage Service", version="1.0.0", lifespan=lifespan)


@app.get("/")
async def root():
    """Root endpoint that redirects to the API documentation."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")

def _run_vad_analysis(
    audio_file_contents: bytes,
    original_filename: str,
    request_id: str,
    threshold: float,
    min_segment_duration: float,
    max_merge_gap: float,
    export_audio_segments: bool,
    output_format: str,
    vad_model: Any,
    get_speech_timestamps_func: Any,
) -> tuple[dict, str]:
    """
    在一个独立的同步函数中执行所有阻塞的CPU密集型和I/O操作。
    """
    overall_start_time = time.time()
    
    # 构建路径
    safe_filename = "".join(c for c in original_filename if c.isalnum() or c in ('.', '-', '_')).rstrip()
    temp_file_path = TEMP_DIR / f"{request_id}_{safe_filename}"
    request_output_dir = OUTPUT_DIR / request_id
    
    try:
        # 1. 创建目录并保存临时文件
        os.makedirs(request_output_dir, exist_ok=True)
        with open(temp_file_path, 'wb') as f:
            f.write(audio_file_contents)
        
        # 2. 加载音频
        audio_loading_start = time.time()
        y, sr = librosa.load(str(temp_file_path), sr=SAMPLE_RATE)
        audio_duration = len(y) / sr
        audio_loading_time = time.time() - audio_loading_start
        log_message(f"Audio loaded, duration: {audio_duration:.2f}s (request_id: {request_id})")

        # 3. VAD 检测
        segments, performance_stats = detect_vad_segments(
            y=y, sr=sr, threshold=threshold, min_segment_duration=min_segment_duration,
            max_merge_gap=max_merge_gap, vad_model=vad_model,
            get_speech_timestamps=get_speech_timestamps_func, request_id=request_id,
            total_duration=audio_duration
        )

        # 4. 导出音频段
        audio_segments = []
        if export_audio_segments and segments:
            audio_segments = export_segments(
                segments=segments, y=y, sr=sr, output_dir=request_output_dir,
                format=output_format, request_id=request_id
            )

        # 5. 准备性能和元数据
        overall_speech_ratio = segments[0].get("overall_speech_ratio", 0.0) if segments else 0.0
        total_processing_time = time.time() - overall_start_time
        speed_ratio = audio_duration / total_processing_time if total_processing_time > 0 else 0
        
        complete_performance_data = {
            "total_processing_time": total_processing_time, "audio_loading_time": audio_loading_time,
            "stage1_vad_timestamps_time": performance_stats.get("stage1_vad_timestamps_time", 0.0),
            "stage2_feature_extraction_time": performance_stats.get("stage2_feature_extraction_time", 0.0),
            "speed_ratio": speed_ratio
        }
        vad_parameters = {
            "threshold": threshold, "min_segment_duration": min_segment_duration, "max_merge_gap": max_merge_gap
        }

        # 6. 保存结果
        timestamps_path = request_output_dir / "timestamps.json"
        response = save_timestamps(
            segments=segments, timestamps_path=timestamps_path, request_id=request_id,
            audio_segments=audio_segments, overall_speech_ratio=overall_speech_ratio,
            source_file=str(temp_file_path.resolve()), vad_parameters=vad_parameters,
            performance_data=complete_performance_data, total_audio_duration=audio_duration
        )
        
        log_message(f"VAD analysis complete, returning {len(segments)} speech segments (request_id: {request_id})")
        
        return response, str(timestamps_path)

    finally:
        # 7. 清理临时文件
        if temp_file_path.exists():
            temp_file_path.unlink(missing_ok=True)


@app.post("/api/vad", response_model=VADResponse)
async def analyze_vad(
    background_tasks: BackgroundTasks,
    audio_file: UploadFile=File(...),
    threshold: float=Form(0.3, ge=0.0, le=1.0),
    min_segment_duration: float=Form(0.3, ge=0.1),
    max_merge_gap: float=Form(0.0, ge=0.0),
    export_audio_segments: bool=Form(True),
    output_format: str=Form("wav"),
    request_id: Optional[str]=Form(None)
):
    """
    分析音频文件，检测语音活动段 (VAD)。此端点为异步接口，将CPU密集型任务卸载到线程池。
    """
    current_time = get_current_time()

    # 优化: 使用UUID生成request_id，避免读取文件内容
    if not request_id or not re.match(r'^[a-f0-9]{32}$', request_id.lower()):
        if request_id:
            log_message(f"[{current_time}] WARNING - Provided request_id '{request_id}' is invalid, regenerating", "WARNING")
        request_id = uuid.uuid4().hex
    
    if output_format not in ["wav", "flac"]:
        raise HTTPException(status_code=400, detail=f"Unsupported output format: {output_format}")

    if not hasattr(app.state, 'vad_model') or app.state.vad_model is None:
        raise HTTPException(status_code=500, detail="VAD model not loaded")

    try:
        # 读取文件内容到内存，准备传递给后台线程
        audio_contents = await audio_file.read()
        
        # 优化: 使用asyncio.to_thread将阻塞操作卸载到线程池
        response, timestamps_path = await asyncio.to_thread(
            _run_vad_analysis,
            audio_file_contents=audio_contents,
            original_filename=audio_file.filename or "unknown.audio",
            request_id=request_id,
            threshold=threshold,
            min_segment_duration=min_segment_duration,
            max_merge_gap=max_merge_gap,
            export_audio_segments=export_audio_segments,
            output_format=output_format,
            vad_model=app.state.vad_model,
            get_speech_timestamps_func=app.state.get_speech_timestamps,
        )
        
        # 在后台更新数据库
        background_tasks.add_task(update_db_in_background, timestamps_path, request_id)
        
        return JSONResponse(content=response)

    except Exception as e:
        error_msg = f"Unexpected error during VAD analysis: {str(e)}"
        log_message(f"{error_msg} (request_id: {request_id})", "ERROR")
        import traceback
        log_message(f"Error stacktrace: {traceback.format_exc()} (request_id: {request_id})", "ERROR")
        raise HTTPException(status_code=500, detail=error_msg)


@app.get("/api/health")
async def health_check():
    """综合健康检查和信息服务端点"""
    current_time = get_current_time()
    from core.utils import validate_directories
    report = validate_directories()
    temp_ok = report['temp_dir']['exists'] and all(report['temp_dir'][p] for p in ['readable', 'writable', 'executable'])
    output_ok = report['output_dir']['exists'] and all(report['output_dir'][p] for p in ['readable', 'writable', 'executable'])
    model_loaded = hasattr(app.state, 'vad_model') and app.state.vad_model is not None
    status = "healthy" if temp_ok and output_ok and model_loaded else "unhealthy"
    log_message(f"Health check: status={status}, temp_ok={temp_ok}, output_ok={output_ok}, model_loaded={model_loaded}")
    
    # 返回综合信息
    return {
        "status": status,
        "timestamp": current_time,
        "model_loaded": model_loaded,
        "service": "VAD Service",
        "version": "1.0.0",
        "model": "Silero VAD (ONNX)" if model_loaded else "Not loaded",
        "supported_formats": ["wav", "mp3", "m4a", "flac", "ogg"]
    }


def update_db_in_background(timestamps_path: str, task_id: str):
    """在后台线程中运行同步的数据库更新操作"""
    try:
        log_message(f"Starting background DB update for task: {task_id}")
        success = process_single_timestamps_file(timestamps_path, task_id)
        if success:
            log_message(f"Background DB update successful for task: {task_id}")
        else:
            log_message(f"Background DB update failed for task: {task_id}", "WARNING")
    except Exception as e:
        log_message(f"Exception in background DB update for task {task_id}: {e}", "ERROR")


if __name__ == "__main__":
    import uvicorn
    # 建议: 在生产环境中使用 Gunicorn 运行:
    # gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8083
    uvicorn.run(app, host="0.0.0.0", port=8083)
