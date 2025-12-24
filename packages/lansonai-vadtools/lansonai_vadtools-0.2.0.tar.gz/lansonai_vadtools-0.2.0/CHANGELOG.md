# Changelog

## 0.2.0 (2025-12-19)

### Added
- Initial release as `lansonai-vadtools`
- Core VAD analysis functionality
- Support for audio and video files
- Audio segment export
- Comprehensive logging
- Performance metrics

### Features
- Voice Activity Detection using Silero VAD model
- Audio/video file processing
- Configurable VAD parameters (threshold, min duration, merge gap)
- JSON result export
- Audio segment export (WAV/FLAC)
- Detailed performance metrics

### Technical Details
- Python 3.12+ required
- Uses PyTorch and Silero VAD model
- Supports WAV, MP3, M4A, FLAC, OGG audio formats
- Supports MP4, AVI, MOV, MKV, FLV, WMV, WEBM, M4V video formats (requires ffmpeg)
