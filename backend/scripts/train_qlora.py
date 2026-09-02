import os
import sys
import subprocess

# Auto-check and install requirements if needed
try:
    import peft
except ImportError:
    print("Installing backend requirements for QLoRA training...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "requirements.txt")])

import torch

# Add parent directory to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

BASE_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
DATASET_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "finetune_dataset.jsonl")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "qwen_automind_lora")

def train():
    print("=== AutoMind QLoRA Fine-Tuning Pipeline ===")
    
    if not os.path.exists(DATASET_PATH):
        print(f"Dataset not found at {DATASET_PATH}. Running JSONL converter first...")
        from scripts.convert_to_jsonl import convert_cars_to_jsonl
        convert_cars_to_jsonl()

    print(f"Loading dataset from: {DATASET_PATH}")
    ds = load_dataset("json", data_files=DATASET_PATH)

    print(f"Loading base model '{BASE_MODEL}' with 4-bit QLoRA quantization...")
    
    # 4-Bit BitsAndBytes Configuration
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True
    )

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True
    )
    model = prepare_model_for_kbit_training(model)

    # QLoRA Adapter Config
    peft_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )

    model = get_peft_model(model, peft_config)
    model.print_trainable_parameters()

    print("\nQLoRA training configuration ready!")
    print(f"Fine-tuned adapter model will be saved to: {OUTPUT_DIR}")

if __name__ == "__main__":
    train()
