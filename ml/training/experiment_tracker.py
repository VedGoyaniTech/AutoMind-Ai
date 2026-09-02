"""
AutoMind AI — Experiment Tracker & Versioning Manager (Points 1, 4, 12 of Roadmap)
Tracks:
  - Training Loss & Validation Loss
  - Versioned Checkpoint Folders (models/qwen_lora_v1, v2, v3)
  - Hyperparameters (Learning Rate, Epochs, LoRA Rank r, Alpha)
  - Experiment Summary Log Table
"""

import os
import json
import time
from typing import Dict, Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG_PATH = os.path.join(BASE_DIR, "ml", "training", "experiment_log.json")
MODELS_DIR = os.path.join(BASE_DIR, "ml", "training", "models")

class ExperimentTracker:
    def __init__(self, experiment_name: str = "qwen_lora"):
        self.experiment_name = experiment_name
        self.models_dir = MODELS_DIR
        os.makedirs(self.models_dir, exist_ok=True)
        self.version = self._get_next_version()

    def _get_next_version(self) -> int:
        existing_versions = []
        if os.path.exists(self.models_dir):
            for folder in os.listdir(self.models_dir):
                if folder.startswith(f"{self.experiment_name}_v"):
                    try:
                        v = int(folder.replace(f"{self.experiment_name}_v", ""))
                        existing_versions.append(v)
                    except ValueError:
                        pass
        return max(existing_versions, default=0) + 1

    def get_version_output_dir(self) -> str:
        version_dir = os.path.join(self.models_dir, f"{self.experiment_name}_v{self.version}")
        os.makedirs(version_dir, exist_ok=True)
        return version_dir

    def log_run(
        self,
        base_model: str,
        num_epochs: int,
        learning_rate: float,
        lora_r: int,
        lora_alpha: int,
        train_loss: float,
        val_loss: float,
        result_status: str = "Success"
    ):
        output_dir = self.get_version_output_dir()
        run_record = {
            "version": f"v{self.version}",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "base_model": base_model,
            "output_dir": output_dir,
            "hyperparameters": {
                "epochs": num_epochs,
                "learning_rate": learning_rate,
                "lora_r": lora_r,
                "lora_alpha": lora_alpha
            },
            "metrics": {
                "train_loss": round(train_loss, 4),
                "val_loss": round(val_loss, 4),
                "overfit_warning": val_loss > (train_loss * 1.3)
            },
            "status": result_status
        }

        # Save to experiment_log.json
        logs = []
        if os.path.exists(LOG_PATH):
            try:
                with open(LOG_PATH, "r", encoding="utf-8") as f:
                    logs = json.load(f)
            except Exception:
                logs = []

        logs.append(run_record)
        with open(LOG_PATH, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2)

        print("\n" + "=" * 70)
        print(f" EXPERIMENT RUN SAVED: {run_record['version']} ")
        print("=" * 70)
        print(f"    - Versioned Checkpoint: {output_dir}")
        print(f"    - Training Loss: {train_loss:.4f} | Validation Loss: {val_loss:.4f}")
        if run_record["metrics"]["overfit_warning"]:
            print("    [!] WARNING: Validation loss is significantly higher than training loss (Possible Overfitting)")
        else:
            print("    [✔] Generalization Check: Good alignment between Train and Validation Loss")
        print("=" * 70)

        return run_record

if __name__ == "__main__":
    tracker = ExperimentTracker()
    print(f"Next Model Version Directory: {tracker.get_version_output_dir()}")
