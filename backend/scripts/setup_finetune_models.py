import os
import sys
import subprocess

# Auto-check and install pre-built binary wheels for Python 3.13
try:
    from sentence_transformers import SentenceTransformer
    from huggingface_hub import snapshot_download
except ImportError:
    print("Installing pre-built PyTorch & SentenceTransformers binary wheels for Python 3.13...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "sentence-transformers", "huggingface_hub", "torch", "numpy>=2.0.0"])
    from sentence_transformers import SentenceTransformer
    from huggingface_hub import snapshot_download

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

HF_TOKEN = os.getenv("HF_TOKEN", "")

def setup():
    print("=== AutoMind AI Model & Fine-Tuning Setup ===")
    
    # 1. Download & cache embedding models
    print("\n1. Downloading Embedding Models...")
    print("-> Downloading all-MiniLM-L6-v2...")
    model1 = SentenceTransformer("all-MiniLM-L6-v2")
    print("✔ all-MiniLM-L6-v2 successfully cached!")

    print("-> Downloading BAAI/bge-small-en-v1.5...")
    model2 = SentenceTransformer("BAAI/bge-small-en-v1.5")
    print("✔ BAAI/bge-small-en-v1.5 successfully cached!")

    # 2. Pre-download Qwen 2.5 1.5B Instruct model
    print("\n2. Pre-caching Qwen 2.5 1.5B / 3B LLM model...")
    qwen_model_id = "Qwen/Qwen2.5-1.5B-Instruct"
    print(f"-> Downloading {qwen_model_id} repository snapshot...")
    try:
        path = snapshot_download(repo_id=qwen_model_id, token=HF_TOKEN)
        print(f"✔ {qwen_model_id} model weights successfully cached at: {path}")
    except Exception as e:
        print(f"Notice during Qwen download: {e}")

    print("\n=== Model Setup Complete! ===")

if __name__ == "__main__":
    setup()
