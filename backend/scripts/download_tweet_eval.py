import os
import sys
import json
try:
    from huggingface_hub import HfApi, hf_hub_download, login
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "huggingface_hub", "datasets"])
    from huggingface_hub import HfApi, hf_hub_download, login

HF_TOKEN = os.getenv("HF_TOKEN", "")
DATASET_ID = "cardiffnlp/tweet_eval"
SAVE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "tweet_eval")

def main():
    if HF_TOKEN:
        print(f"Logging in to Hugging Face with provided token...")
        try:
            login(token=HF_TOKEN)
            print("Successfully authenticated with Hugging Face!")
        except Exception as e:
            print(f"Auth notice: {e}")
    else:
        print("No HF_TOKEN provided in environment; proceeding with public datasets.")

    os.makedirs(SAVE_DIR, exist_ok=True)
    print(f"Downloading dataset '{DATASET_ID}' into {os.path.abspath(SAVE_DIR)}...")

    try:
        from datasets import load_dataset
        tasks = ['emoji', 'emotion', 'hate', 'irony', 'offensive', 'sentiment', 'stance_abortion', 'stance_atheism', 'stance_climate', 'stance_feminist', 'stance_hillary']
        
        for task in tasks:
            print(f"Downloading subset: {task}...")
            task_dir = os.path.join(SAVE_DIR, task)
            os.makedirs(task_dir, exist_ok=True)
            
            try:
                ds = load_dataset(DATASET_ID, task, token=HF_TOKEN)
                for split in ds.keys():
                    split_path = os.path.join(task_dir, f"{split}.json")
                    ds[split].to_json(split_path)
                    print(f"Saved {task}/{split}.json ({len(ds[split])} records)")
            except Exception as sub_e:
                print(f"Error downloading subset '{task}': {sub_e}")
                
    except ImportError:
        print("datasets library not installed, downloading directly via HuggingFace Hub API...")
        api = HfApi(token=HF_TOKEN)
        files = api.list_repo_files(repo_id=DATASET_ID, repo_type="dataset")
        print(f"Found {len(files)} dataset files: {files}")
        for file in files:
            print(f"Downloading file: {file}...")
            local_path = hf_hub_download(repo_id=DATASET_ID, filename=file, repo_type="dataset", token=HF_TOKEN, local_dir=SAVE_DIR)
            print(f"Saved to {local_path}")

    print("\nDataset download process completed!")

if __name__ == "__main__":
    main()
