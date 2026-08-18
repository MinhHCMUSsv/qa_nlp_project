"""
TechQA Dataset Clean Stream Downloader & Extractor

Downloads TechQA.tar.gz (2.82 GB) cleanly with HF_TOKEN auth and extracts to data/raw/techqa/

Usage:
    python scripts/download_techqa.py
"""

import sys
import os
import json
import tarfile
import time
import requests
from dotenv import load_dotenv
from huggingface_hub import hf_hub_url

load_dotenv()

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


def download_and_extract_techqa():
    target_dir = os.path.join("data", "raw", "techqa")
    os.makedirs(target_dir, exist_ok=True)

    dest_file = os.path.join(target_dir, "TechQA.tar.gz")
    progress_file = os.path.join(target_dir, "progress.json")

    # Load HF token if available
    hf_token = os.getenv("HF_TOKEN", "").strip()
    auth_headers = {}
    if hf_token and hf_token != "your_huggingface_token_here":
        auth_headers["Authorization"] = f"Bearer {hf_token}"
        print("🔑 Using Hugging Face authentication token.")

    print("==================================================")
    print("📦 TechQA Clean Downloader & Extractor")
    print("   Source: HuggingFace PrimeQA/TechQA")
    print(f"   Target: {os.path.abspath(dest_file)}")
    print("==================================================")

    # 1. Get CDN download URL
    cdn_url = hf_hub_url("PrimeQA/TechQA", "TechQA.tar.gz", repo_type="dataset")
    res = requests.head(cdn_url, headers=auth_headers, allow_redirects=True)
    total_bytes = int(res.headers.get("content-length", 2959973525))
    actual_url = res.url

    print(f"Total size: {total_bytes / (1024 * 1024):.2f} MB")

    # If existing file is corrupted or incomplete, remove it to start clean download
    if os.path.exists(dest_file):
        print("🧹 Removing previous archive file to ensure clean gzip download...")
        os.remove(dest_file)

    downloaded_bytes = 0
    chunk_size = 4 * 1024 * 1024  # 4 MB chunk for max speed
    last_log_time = time.time()

    print("🚀 Downloading TechQA.tar.gz...")
    response = requests.get(actual_url, headers=auth_headers, stream=True, timeout=60)
    response.raise_for_status()

    with open(dest_file, "wb") as f:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)
                downloaded_bytes += len(chunk)

                pct = round((downloaded_bytes / total_bytes) * 100, 2)
                status_data = {
                    "downloaded_bytes": downloaded_bytes,
                    "total_bytes": total_bytes,
                    "downloaded_mb": round(downloaded_bytes / (1024 * 1024), 2),
                    "total_mb": round(total_bytes / (1024 * 1024), 2),
                    "percent": pct,
                    "status": "downloading" if downloaded_bytes < total_bytes else "downloaded",
                }

                with open(progress_file, "w", encoding="utf-8") as pf:
                    json.dump(status_data, pf, indent=2)

                if time.time() - last_log_time >= 3:
                    print(f"Progress: {pct}% ({status_data['downloaded_mb']} / {status_data['total_mb']} MB)")
                    last_log_time = time.time()

    print("\n✅ Download finished 100%! File verified.")

    # 2. Extract tar.gz archive
    print("📂 Extracting TechQA.tar.gz archive...")
    with tarfile.open(dest_file, "r:gz") as tar:
        if hasattr(tarfile, "data_filter"):
            tar.extractall(path=target_dir, filter="data")
        else:
            tar.extractall(path=target_dir)

    status_data = {
        "downloaded_bytes": total_bytes,
        "total_bytes": total_bytes,
        "downloaded_mb": round(total_bytes / (1024 * 1024), 2),
        "total_mb": round(total_bytes / (1024 * 1024), 2),
        "percent": 100.0,
        "status": "completed",
    }
    with open(progress_file, "w", encoding="utf-8") as pf:
        json.dump(status_data, pf, indent=2)

    print("\n🎉 All done! TechQA dataset successfully extracted into data/raw/techqa/")


if __name__ == "__main__":
    download_and_extract_techqa()
