#!/usr/bin/env python3
"""
Download and cache the sentence transformer model locally
"""

from sentence_transformers import SentenceTransformer
import os
import shutil

def download_model():
    """Download the model and save it locally."""
    model_name = "all-MiniLM-L6-v2"
    local_path = "/app/all-MiniLM-L6-v2-local"
    
    print(f"Downloading {model_name}...")
    
    # Download the model
    model = SentenceTransformer(model_name)
    
    # Save it locally
    model.save(local_path)
    
    print(f"Model saved to {local_path}")
    
    # Clean up any unnecessary cache files
    cache_dir = os.path.expanduser("~/.cache/huggingface")
    if os.path.exists(cache_dir):
        print("Cleaning up cache...")
        shutil.rmtree(cache_dir, ignore_errors=True)
    
    # Verify the model works
    print("Testing model...")
    test_model = SentenceTransformer(local_path)
    test_embedding = test_model.encode("test sentence")
    print(f"Model test successful. Embedding shape: {test_embedding.shape}")

if __name__ == "__main__":
    download_model()