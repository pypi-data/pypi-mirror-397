# VAD Service README

This document provides instructions and API documentation for the Python-based Voice Activity Detection (VAD) service.

## Overview

The VAD service is a FastAPI application that analyzes audio files to detect speech segments. It uses the Silero VAD model for accurate and efficient voice detection.

## Getting Started

### Prerequisites

- Python 3.9+
- `pip` for package management

### Installation

1.  Navigate to the service directory:
    ```bash
    cd scripts/python/vad
    ```

2.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Running the Service

To run the service locally, use `uvicorn`:

```bash
uvicorn main:app --host 0.0.0.0 --port 3102 --reload
```

The service will be available at `http://localhost:3102`.

## API Documentation

The complete and interactive API documentation is available at `http://localhost:3102/docs` when the service is running.

### Endpoints

#### `POST /api/vad/analyze`

Analyzes an audio file for voice activity.

**Request Body**: `multipart/form-data`

-   `audioFile` (file, **required**): The audio or video file to analyze.
-   `threshold` (number, optional, default: 0.3): VAD sensitivity threshold (0.0 to 1.0).
-   `minSegmentDuration` (number, optional, default: 0.3): Minimum duration for a speech segment in seconds.
-   `maxMergeGap` (number, optional, default: 0.0): Maximum silence duration between segments to be merged, in seconds.
-   `exportAudioSegments` (boolean, optional, default: true): Whether to export detected speech segments as individual audio files.
-   `outputFormat` (string, optional, default: "wav"): Format for exported audio segments (`wav` or `flac`).
-   `requestId` (string, optional): A unique ID for the request. If not provided, one will be generated.

**Example cURL Request**:

```bash
curl -X POST "http://localhost:3102/api/vad/analyze" \
     -F "audioFile=@/path/to/your/audio.wav" \
     -F "minSegmentDuration=0.5"
```

**Success Response (200)**:

Returns a JSON object with detailed analysis results. See the `VADAnalysisResponse` schema in the OpenAPI specification for the full structure.

#### `GET /api/vad/results/{requestId}/{filename}`

Retrieves an artifact generated during analysis, such as the `timestamps.json` file or an exported audio segment.

**Path Parameters**:

-   `requestId` (string, **required**): The ID of the analysis request.
-   `filename` (string, **required**): The name of the file to retrieve.

**Example cURL Request**:

```bash
# Get the timestamps file
curl -X GET "http://localhost:3102/api/vad/results/your-request-id/timestamps.json"

# Get an audio segment
curl -X GET "http://localhost:3102/api/vad/results/your-request-id/segment_0_1.23_4.56.wav"
```

#### `GET /api/health`

Checks the health of the service, including directory permissions and model status.

#### `GET /api/info`

Provides general information about the service, its version, and capabilities.