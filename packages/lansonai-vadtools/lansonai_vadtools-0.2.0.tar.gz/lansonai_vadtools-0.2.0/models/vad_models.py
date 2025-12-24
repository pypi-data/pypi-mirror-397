from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class VADConfig(BaseModel):
    """VAD配置参数"""
    threshold: float = 0.3
    min_segment_duration: float = 0.1
    max_merge_gap: float = 0.5
    sampling_rate: int = 16000
    export_audio_segments: bool = True
    output_format: str = "wav"


class VADMetadata(BaseModel):
    """VAD元数据"""
    source_file: str
    run_id: str
    processing_date: str
    parameters: Dict[str, Any]


class VADPerformance(BaseModel):
    """VAD性能数据"""
    total_processing_time: float
    audio_loading_time: float
    stage1_vad_timestamps_time: float
    stage2_feature_extraction_time: float
    speed_ratio: float


class VADSummary(BaseModel):
    """VAD统计摘要"""
    total_duration: float
    total_speech_duration: float
    overall_speech_ratio: float
    num_segments: int


class VADSegment(BaseModel):
    """语音段详细信息"""
    id: int
    file_path: str
    start_time: float
    end_time: float
    duration: float
    speech_confidence: float
    rms: float
    peak_amplitude: float


class VADCompleteResult(BaseModel):
    """完整的VAD分析结果 - 匹配期望的JSON结构"""
    metadata: VADMetadata
    performance: VADPerformance
    summary: VADSummary
    segments: List[VADSegment]


# 兼容性保持 - 用于现有的API接口
class AudioSegment(BaseModel):
    """音频段信息 - 向后兼容"""
    id: int
    start_time: float
    end_time: float
    duration: float
    source_url: Optional[str] = None
    rms: float = 0.0
    peak_amplitude: float = 0.0
    speech_confidence: float = 0.8
    overall_speech_ratio: Optional[float] = None


class VADResult(BaseModel):
    """VAD处理结果 - 向后兼容"""
    success: bool
    request_id: str
    processing_time: float
    audio_info: Dict[str, Any]
    segments: List[AudioSegment]
    statistics: Dict[str, Any]
    output_dir: Optional[str] = None
    error: Optional[str] = None