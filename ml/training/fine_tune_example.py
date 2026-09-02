"""
AutoMind AI — Domain Fine-Tuning Script & Vector Ingestion
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from train_on_dataset import main

if __name__ == "__main__":
    main()
