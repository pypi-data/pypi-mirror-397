#!/usr/bin/env python3
"""
Modal Deployment Script for VAD API - Elegant & Production-Ready

This script deploys a Voice Activity Detection (VAD) API to Modal cloud platform.
Features:
- CPU-optimized for VAD processing (no GPU required)
- Persistent storage for processed audio segments
- Comprehensive error handling and logging
- Clean configuration management
- UV package manager for fast dependency installation
"""

import modal
import os
from pathlib import Path
from typing import List, Optional


# ===================================================================
# Configuration Class - Single Source of Truth
# ===================================================================
class DeploymentConfig:
    """Centralized configuration for VAD API deployment."""
    
    # Application Settings
    APP_NAME = "vad"
    PYTHON_VERSION = "3.10"
    
    # Path Configuration
    LOCAL_VAD_DIR = Path(__file__).parent
    REMOTE_APP_PATH = "/root/app"
    REQUIREMENTS_FILE = "pyproject.toml"
    
    # Storage Configuration
    VOLUME_NAME = "vad-audio"
    VAD_STORAGE_PATH = "/vad_audio"
    TEMP_DIR = "/tmp/vad_api"
    
    # Optional external base URL for absolute redirects (e.g. https://deth--vad-api.modal.run)
    # Set this value before deployment or override with environment variable BASE_URL at runtime.
    EXTERNAL_URL: str = ""
    
    # Resource Allocation
    CPU_CORES = 2.0
    MEMORY_MB = 4096
    TIMEOUT_SECONDS = 180
    
    # API Endpoints
    ANALYZE_ENDPOINT = "/api/vad/analyze"
    HEALTH_ENDPOINT = "/api/health"
    INFO_ENDPOINT = "/api/info"
    
    @classmethod
    def get_deployment_instructions(cls) -> List[str]:
        """Generate deployment instructions with current configuration."""
        script_name = Path(__file__).name
        return [
            f"=== {cls.APP_NAME.upper()} DEPLOYMENT GUIDE ===",
            "",
            "🚀 Deployment Commands:",
            f"   modal deploy {script_name}           # Deploy to production",
            f"   modal serve {script_name}            # Local development server",
            "",
            "🧪 Testing Commands:",
            f"   modal run {script_name}::test_vad --audio-file-path '/path/to/audio.mp3'",
            f"   modal run {script_name}::list_segments",
            f"   modal run {script_name}::health_check",
            "",
            "📚 API Documentation (after deployment):",
            "   • Swagger UI: https://<app-url>/docs",
            "   • ReDoc: https://<app-url>/redoc",
            f"   • Health Check: https://<app-url>{cls.HEALTH_ENDPOINT}",
            f"   • API Info: https://<app-url>{cls.INFO_ENDPOINT}",
            "",
            "=" * 50
        ]


# ===================================================================
# Modal Application Setup
# ===================================================================

# Create the Modal app
app = modal.App(DeploymentConfig.APP_NAME)

# Configure persistent storage volume
vad_volume = modal.Volume.from_name(
    DeploymentConfig.VOLUME_NAME, 
    create_if_missing=True
)

# Build the container image with optimized dependency installation
def create_optimized_image() -> modal.Image:
    """Create a container image with UV package manager and all dependencies."""
    
    print(f"🔨 Building container image with Python {DeploymentConfig.PYTHON_VERSION}")
    print(f"📦 Installing dependencies from {DeploymentConfig.REQUIREMENTS_FILE}")
    
    return (
        modal.Image.debian_slim(python_version=DeploymentConfig.PYTHON_VERSION)
        .env({"TORCH_HOME": "/tmp/torch"})  # Set a writable cache dir for model downloads
        # Install system dependencies
        .apt_install("ffmpeg", "curl")
        
        .add_local_file(
            DeploymentConfig.LOCAL_VAD_DIR / DeploymentConfig.REQUIREMENTS_FILE,
            f"{DeploymentConfig.REMOTE_APP_PATH}/{DeploymentConfig.REQUIREMENTS_FILE}",
            copy=True
        )
        # Install UV package manager for faster dependency resolution
        .run_commands(
            "curl -LsSf https://astral.sh/uv/install.sh | sh",
            "echo 'export PATH=$HOME/.cargo/bin:$PATH' >> ~/.bashrc"
        )
        
        # Install Python dependencies using UV (use absolute path to requirements)
        .run_commands(
            "export PATH=$HOME/.cargo/bin:$PATH",
            f"uv pip install --system -r {DeploymentConfig.REMOTE_APP_PATH}/{DeploymentConfig.REQUIREMENTS_FILE}"
        )
        
        .add_local_dir(
            DeploymentConfig.LOCAL_VAD_DIR, 
            DeploymentConfig.REMOTE_APP_PATH
        )
    )

# Create the image
app_image = create_optimized_image()


# ===================================================================
# Main API Function
# ===================================================================

# Define a secret to securely pass the DATABASE_URL
db_secret = modal.Secret.from_name("my-db-secret")

@app.function(
    image=app_image,
    cpu=DeploymentConfig.CPU_CORES,
    memory=DeploymentConfig.MEMORY_MB,
    timeout=DeploymentConfig.TIMEOUT_SECONDS,
    volumes={DeploymentConfig.VAD_STORAGE_PATH: vad_volume},
    secrets=[db_secret]  # Attach the secret to the function
)
@modal.asgi_app()
def api():
    """
    Main VAD API service function.
    
    Sets up the environment and returns the FastAPI application instance.
    """
    import sys
    import os
    from pathlib import Path
    
    # Configure Python path
    sys.path.insert(0, DeploymentConfig.REMOTE_APP_PATH)
    
    # Ensure required directories exist
    Path(DeploymentConfig.TEMP_DIR).mkdir(parents=True, exist_ok=True)
    Path(DeploymentConfig.VAD_STORAGE_PATH).mkdir(parents=True, exist_ok=True)
    
    # Set environment variables for the application
    # Include BASE_URL so the FastAPI app can generate absolute redirects to /docs when desired.
    env_updates = {
        "VAD_STORAGE_PATH": DeploymentConfig.VAD_STORAGE_PATH,
        "PYTHONPATH": DeploymentConfig.REMOTE_APP_PATH,
        "TORCH_HOME": "/tmp/torch",  # Ensure runtime uses the same cache dir
    }
    # Prefer runtime environment variable; fall back to configured EXTERNAL_URL in DeploymentConfig
    if os.getenv("BASE_URL"):
        env_updates["BASE_URL"] = os.getenv("BASE_URL")
    elif DeploymentConfig.EXTERNAL_URL:
        env_updates["BASE_URL"] = DeploymentConfig.EXTERNAL_URL
    else:
        # leave BASE_URL unset (app will use relative /docs)
        env_updates["BASE_URL"] = ""
    os.environ.update(env_updates)
    
    # Import and configure the FastAPI application
    try:
        from main import app as fastapi_app
        
        print("✅ VAD API successfully initialized")
        # 詳細打印存儲與臨時目錄信息（顯示絕對路徑、存在性、可寫性、以及是否可能是 tmpfs 類臨時路徑）
        def _describe_and_ensure(path_str: str, attempt_create: bool = True):
            from pathlib import Path
            import tempfile
            import os
            import uuid

            p = Path(path_str).resolve()
            status_parts = []

            # 存在性檢查與（可選）創建
            if p.exists():
                status_parts.append("exists")
                exists = True
            else:
                exists = False
                if attempt_create:
                    try:
                        p.mkdir(parents=True, exist_ok=True)
                        status_parts.append("created")
                        exists = True
                    except Exception as e:
                        status_parts.append(f"missing, failed to create: {e}")
                else:
                    status_parts.append("missing")

            # 可寫性檢查（以實際寫入為準）
            if exists:
                try:
                    # 使用 NamedTemporaryFile 在目錄內寫入測試文件
                    tf = tempfile.NamedTemporaryFile(prefix=".write_test_", dir=str(p), delete=True)
                    tf.write(b"v")
                    tf.flush()
                    tf.close()
                    status_parts.append("writable")
                except Exception:
                    status_parts.append("not writable")

            # 臨時文件系統啟發式判斷
            ephemeral_roots = ("/tmp", "/var/tmp", "/run", "/dev/shm")
            is_ephemeral = any(str(p).startswith(root + os.sep) or str(p) == root for root in ephemeral_roots)
            if is_ephemeral:
                status_parts.append("likely ephemeral — will be lost on reboot")

            return p, ", ".join(status_parts)

        p_path, p_info = _describe_and_ensure(DeploymentConfig.VAD_STORAGE_PATH, attempt_create=True)
        t_path, t_info = _describe_and_ensure(DeploymentConfig.TEMP_DIR, attempt_create=True)

        print(f"📁 Persistent storage: {p_path} ({p_info})")
        print(f"💾 Temporary storage: {t_path} ({t_info})")
        print(f"🔧 CPU cores: {DeploymentConfig.CPU_CORES}")
        print(f"💾 Memory: {DeploymentConfig.MEMORY_MB}MB")
        
        return fastapi_app
        
    except ImportError as e:
        print(f"❌ Failed to import FastAPI application: {e}")
        raise
    except Exception as e:
        print(f"❌ Unexpected error during initialization: {e}")
        raise


# ===================================================================
# Utility Functions
# ===================================================================
@app.function(
    image=app_image,
    volumes={DeploymentConfig.VAD_STORAGE_PATH: vad_volume}
)
def list_segments() -> List[str]:
    """
    List all processed audio segments in persistent storage.
    
    Returns:
        List of directory paths containing segments
    """
    from pathlib import Path
    
    storage_path = Path(DeploymentConfig.VAD_STORAGE_PATH)
    print(f"📂 Listing contents of: {storage_path}")
    
    if not storage_path.exists():
        print("   📭 Storage volume not yet created or mounted")
        return []
    
    try:
        directories = [d for d in storage_path.iterdir() if d.is_dir()]
        
        if not directories:
            print("   📭 No processed segments found")
            return []
        
        print(f"   📊 Found {len(directories)} processed audio sessions:")
        
        for i, dir_path in enumerate(sorted(directories), 1):
            try:
                segment_files = list(dir_path.glob("segment_*.wav"))
                metadata_files = list(dir_path.glob("*.json"))
                
                print(f"   {i:2d}. {dir_path.name}")
                print(f"       🎵 Audio segments: {len(segment_files)}")
                print(f"       📄 Metadata files: {len(metadata_files)}")
                
            except Exception as e:
                print(f"   {i:2d}. {dir_path.name} (⚠️  Error reading: {e})")
        
        return [str(d) for d in directories]
        
    except Exception as e:
        print(f"   ❌ Error accessing storage: {e}")
        return []


@app.function(
    image=app_image,
    secrets=[db_secret]  # Attach the secret for DB access
)
def test_db():
    """
    Run a database connection test within the Modal container.
    This is a quick way to verify that the database connection string and
    permissions are working correctly in the deployed environment.
    """
    import sys
    sys.path.insert(0, DeploymentConfig.REMOTE_APP_PATH)
    print("⚙️  Running database connection test...")
    from utils.db_connection import test_database_connection
    test_database_connection()

@app.function(image=app_image)
def health_check() -> dict:
    """
    Perform a health check on the deployed API.
    
    Returns:
        Health check results
    """
    import requests
    
    api_url = app.web_url
    if not api_url:
        return {"status": "error", "message": "API not deployed"}
    
    try:
        response = requests.get(
            f"{api_url}{DeploymentConfig.HEALTH_ENDPOINT}",
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Health check passed!")
            print(f"   Status: {result.get('status', 'unknown')}")
            print(f"   Timestamp: {result.get('timestamp', 'N/A')}")
            return result
        else:
            print(f"❌ Health check failed (HTTP {response.status_code})")
            return {"status": "error", "code": response.status_code}
            
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return {"status": "error", "message": str(e)}


# ===================================================================
# Entry Point
# ===================================================================

if __name__ == "__main__":
    print(f"📦 VAD API Deployment Tool")
    print(f"🏷️  App Name: {DeploymentConfig.APP_NAME}")
    print(f"📁 Local Directory: {DeploymentConfig.LOCAL_VAD_DIR}")
    print("")
    
    for instruction in DeploymentConfig.get_deployment_instructions():
        print(instruction)