"""
Script to download AQUABOT/Llama-3.2-3B-TechQA from Hugging Face Hub to local directory.
Supports resume and multi-threaded downloading.
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from huggingface_hub import snapshot_download

REPO_ID = os.getenv("LLM_MODEL_NAME", "AQUABOT/Llama-3.2-3B-TechQA")
LOCAL_DIR = os.getenv("LLM_MODEL_PATH", "models/Llama_TechQA")

print(f"===========================================================")
print(f"🚀 DOWNLOADING MODEL FROM HUGGING FACE HUB")
print(f"Repository: {REPO_ID}")
print(f"Destination: {LOCAL_DIR}")
print(f"===========================================================\n")

os.makedirs(LOCAL_DIR, exist_ok=True)

try:
    path = snapshot_download(
        repo_id=REPO_ID,
        local_dir=LOCAL_DIR,
        local_dir_use_symlinks=False,
        resume_download=True,
    )
    print(f"\n🎉 Model downloaded successfully to: {path}")
except Exception as e:
    print(f"\n❌ Error downloading model: {e}")
    sys.exit(1)
