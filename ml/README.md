# AutoMind AI — Machine Learning & Fine-Tuning Layer

## Knowledge Architecture Principle
In **AutoMind AI**, structured vehicle specifications, live regional pricing, safety ratings, and dynamic features stay inside the **MySQL + Vector RAG layer**. Large Language Models should NOT be relied upon to memorize changing numbers directly inside model weights.

## Optional Fine-Tuning Purpose
Optional fine-tuning can be conducted using Hugging Face PEFT/LoRA for:
1. Adapting response formatting (bullet points, comparison matrix generation).
2. Automating vehicle question intent classification.
3. Aligning tone to authoritative automotive consulting.

## Dataset Format
Instruction datasets are stored in JSONL format inside `datasets/`:
```json
{"instruction": "...", "input": "...", "output": "..."}
```

## Running Fine-Tuning Example
```bash
python ml/training/fine_tune_example.py
```
