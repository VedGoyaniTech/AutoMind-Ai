# 📊 AutoMind AI — Comprehensive Training Dataset Audit Report

**Audit Date:** 2026-09-10 09:06:18 UTC  
**Audited Files:** 30  
**Total JSONL Lines:** 3733 (across all version splits)  
**Duplicate Content Hash Groups:** 588  

---

## 🚨 Key Audit Findings & Governance Decisions

1. **Line Count != Unique Verified Automotive Knowledge:** There are **3733 total lines** across tracked JSONL files. These are predominantly version iterations (`train.jsonl`, `train_v2.jsonl`, `train_v3.jsonl`, `train_v4.jsonl`, `master_v2`, `master_v3`, `master_v4`). They do **not** represent 3733 unique verified automotive facts.
2. **Domain Contamination in `master_v4_combined_dataset.jsonl`:** Discovered non-automotive questions including locomotive engineering (e.g. WAG-9 / WAP-7 electric railway locomotives) and unrelated corporate finance questions. **Action:** Quarantined. Forbidden from fine-tuning.
3. **TweetEval Benchmark Exclusion:** TweetEval files in `backend/data/tweet_eval/` cover emotion, irony, emoji, and stance detection (e.g. political figures, climate). They are standard NLP benchmarks and are **strictly excluded** from automotive model training.
4. **Held-Out Test Leakage Prevention:** `ml/datasets/test/test.jsonl` and `test_eval.jsonl` are frozen evaluation sets. Training export pipelines strictly reject records designated as `test` or `evaluation`.
5. **Zero Dynamic Spec Memorization:** Model weights must only learn intent detection, entity resolution, citation formatting, and safe abstention. Actual prices, variant features, and RTO rules are dynamically sourced from versioned SQL tables.

---

## 📋 File-by-File Inventory and Classification

| File | Lines | Valid JSON | Contaminated | Provenance % | Recommendation |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `backend/data/finetune_dataset.jsonl` | 8 | 8 | 0 | 0.0% | **legacy_experiment_archive** |
| `backend/data/fixtures/training/clarification_abstention_fixture.jsonl` | 2 | 2 | 0 | 0.0% | **fixture_only** |
| `backend/data/fixtures/training/evidence_bound_answer_fixture.jsonl` | 2 | 2 | 0 | 0.0% | **fixture_only** |
| `backend/data/fixtures/training/held_out_evaluation_fixture.jsonl` | 2 | 2 | 0 | 0.0% | **fixture_only** |
| `backend/data/fixtures/training/intent_tool_routing_fixture.jsonl` | 3 | 3 | 0 | 100.0% | **fixture_only** |
| `backend/data/fixtures/training/multilingual_automotive_fixture.jsonl` | 2 | 2 | 0 | 0.0% | **fixture_only** |
| `backend/data/fixtures/training/safety_prompt_injection_fixture.jsonl` | 2 | 2 | 0 | 0.0% | **fixture_only** |
| `backend/data/fixtures/training/vehicle_entity_resolution_fixture.jsonl` | 3 | 3 | 0 | 0.0% | **fixture_only** |
| `ml/datasets/cleaned/master_cleaned_catalog.jsonl` | 268 | 268 | 4 | 0.0% | **quarantine_candidate** |
| `ml/datasets/combined_cleaned_dataset.jsonl` | 307 | 307 | 4 | 0.0% | **quarantine_candidate** |
| `ml/datasets/darkB_electric_vehicles_qa_dataset.jsonl` | 278 | 278 | 3 | 0.0% | **quarantine_candidate** |
| `ml/datasets/formatted_instruction_dataset.jsonl` | 307 | 307 | 4 | 0.0% | **quarantine_candidate** |
| `ml/datasets/master_v2_combined_dataset.jsonl` | 307 | 307 | 4 | 0.0% | **quarantine_candidate** |
| `ml/datasets/master_v3_combined_dataset.jsonl` | 314 | 314 | 4 | 0.0% | **quarantine_candidate** |
| `ml/datasets/master_v4_combined_dataset.jsonl` | 320 | 320 | 4 | 0.0% | **quarantine_candidate** |
| `ml/datasets/quarantine/quarantine.jsonl` | 58 | 58 | 0 | 0.0% | **legacy_experiment_archive** |
| `ml/datasets/sample_instruction_dataset.jsonl` | 3 | 3 | 0 | 0.0% | **fixture_only** |
| `ml/datasets/test/test.jsonl` | 28 | 28 | 1 | 0.0% | **quarantine_candidate** |
| `ml/datasets/test_eval.jsonl` | 31 | 31 | 1 | 0.0% | **quarantine_candidate** |
| `ml/datasets/test_eval_v2.jsonl` | 17 | 17 | 0 | 0.0% | **held_out_evaluation_never_train** |
| `ml/datasets/train.jsonl` | 276 | 276 | 3 | 0.0% | **quarantine_candidate** |
| `ml/datasets/train/train.jsonl` | 214 | 214 | 2 | 0.0% | **quarantine_candidate** |
| `ml/datasets/train_v2.jsonl` | 260 | 260 | 4 | 0.0% | **quarantine_candidate** |
| `ml/datasets/train_v3.jsonl` | 282 | 282 | 3 | 0.0% | **quarantine_candidate** |
| `ml/datasets/train_v4.jsonl` | 288 | 288 | 3 | 0.0% | **quarantine_candidate** |
| `ml/datasets/validation.jsonl` | 31 | 31 | 1 | 0.0% | **quarantine_candidate** |
| `ml/datasets/validation/validation.jsonl` | 26 | 26 | 1 | 0.0% | **quarantine_candidate** |
| `ml/datasets/validation_v2.jsonl` | 30 | 30 | 0 | 0.0% | **legacy_experiment_archive** |
| `ml/datasets/validation_v3.jsonl` | 32 | 32 | 1 | 0.0% | **quarantine_candidate** |
| `ml/datasets/validation_v4.jsonl` | 32 | 32 | 1 | 0.0% | **quarantine_candidate** |

---

## 🛑 Contamination Details

### `ml/datasets/cleaned/master_cleaned_catalog.jsonl` (4 contaminated records)
- **Line 133** (Terms: `locomotive`): *"Why didn't the smaller locomotive ever operate on public tracks despite being able reach considerable speeds?..."*
- **Line 163** (Terms: `railway`): *"How might ground level power affect the cost or complexity of certain projects such as railway constructions?..."*
- **Line 233** (Terms: `railway`): *"What happened to Robert Anderson's invention after he attempted to patent it?..."*

### `ml/datasets/combined_cleaned_dataset.jsonl` (4 contaminated records)
- **Line 1** (Terms: `locomotive`): *"Why didn't the smaller locomotive ever operate on public tracks despite being able reach considerable speeds?..."*
- **Line 50** (Terms: `railway`): *"What happened to Robert Anderson's invention after he attempted to patent it?..."*
- **Line 58** (Terms: `locomotive`): *"How did the work of inventors like Nicolas - Joseph Cugnot , Richard Trevithick , and Samuel Brown contribute to the evo..."*

### `ml/datasets/darkB_electric_vehicles_qa_dataset.jsonl` (3 contaminated records)
- **Line 41** (Terms: `railway`): *"What happened to Robert Anderson's invention after he attempted to patent it?..."*
- **Line 118** (Terms: `locomotive`): *"Why didn't the smaller locomotive ever operate on public tracks despite being able reach considerable speeds?..."*
- **Line 132** (Terms: `railway`): *"How might ground level power affect the cost or complexity of certain projects such as railway constructions?..."*

### `ml/datasets/formatted_instruction_dataset.jsonl` (4 contaminated records)
- **Line 1** (Terms: `locomotive`): *"Why didn't the smaller locomotive ever operate on public tracks despite being able reach considerable speeds?..."*
- **Line 50** (Terms: `railway`): *"What happened to Robert Anderson's invention after he attempted to patent it?..."*
- **Line 58** (Terms: `locomotive`): *"How did the work of inventors like Nicolas - Joseph Cugnot , Richard Trevithick , and Samuel Brown contribute to the evo..."*

### `ml/datasets/master_v2_combined_dataset.jsonl` (4 contaminated records)
- **Line 1** (Terms: `locomotive`): *"Why didn't the smaller locomotive ever operate on public tracks despite being able reach considerable speeds?..."*
- **Line 50** (Terms: `railway`): *"What happened to Robert Anderson's invention after he attempted to patent it?..."*
- **Line 58** (Terms: `locomotive`): *"How did the work of inventors like Nicolas - Joseph Cugnot , Richard Trevithick , and Samuel Brown contribute to the evo..."*

### `ml/datasets/master_v3_combined_dataset.jsonl` (4 contaminated records)
- **Line 1** (Terms: `locomotive`): *"Why didn't the smaller locomotive ever operate on public tracks despite being able reach considerable speeds?..."*
- **Line 50** (Terms: `railway`): *"What happened to Robert Anderson's invention after he attempted to patent it?..."*
- **Line 58** (Terms: `locomotive`): *"How did the work of inventors like Nicolas - Joseph Cugnot , Richard Trevithick , and Samuel Brown contribute to the evo..."*

### `ml/datasets/master_v4_combined_dataset.jsonl` (4 contaminated records)
- **Line 1** (Terms: `locomotive`): *"Why didn't the smaller locomotive ever operate on public tracks despite being able reach considerable speeds?..."*
- **Line 50** (Terms: `railway`): *"What happened to Robert Anderson's invention after he attempted to patent it?..."*
- **Line 58** (Terms: `locomotive`): *"How did the work of inventors like Nicolas - Joseph Cugnot , Richard Trevithick , and Samuel Brown contribute to the evo..."*

### `ml/datasets/test/test.jsonl` (1 contaminated records)
- **Line 23** (Terms: `locomotive`): *"How did the work of inventors like Nicolas - Joseph Cugnot , Richard Trevithick , and Samuel Brown contribute to the evo..."*

### `ml/datasets/test_eval.jsonl` (1 contaminated records)
- **Line 31** (Terms: `locomotive`): *"How did the work of inventors like Nicolas - Joseph Cugnot , Richard Trevithick , and Samuel Brown contribute to the evo..."*

### `ml/datasets/train.jsonl` (3 contaminated records)
- **Line 154** (Terms: `locomotive`): *"Why didn't the smaller locomotive ever operate on public tracks despite being able reach considerable speeds?..."*
- **Line 185** (Terms: `railway`): *"How might ground level power affect the cost or complexity of certain projects such as railway constructions?..."*
- **Line 272** (Terms: `railway`): *"What happened to Robert Anderson's invention after he attempted to patent it?..."*

### `ml/datasets/train/train.jsonl` (2 contaminated records)
- **Line 133** (Terms: `locomotive`): *"Why didn't the smaller locomotive ever operate on public tracks despite being able reach considerable speeds?..."*
- **Line 163** (Terms: `railway`): *"How might ground level power affect the cost or complexity of certain projects such as railway constructions?..."*

### `ml/datasets/train_v2.jsonl` (4 contaminated records)
- **Line 1** (Terms: `locomotive`): *"Why didn't the smaller locomotive ever operate on public tracks despite being able reach considerable speeds?..."*
- **Line 50** (Terms: `railway`): *"What happened to Robert Anderson's invention after he attempted to patent it?..."*
- **Line 58** (Terms: `locomotive`): *"How did the work of inventors like Nicolas - Joseph Cugnot , Richard Trevithick , and Samuel Brown contribute to the evo..."*

### `ml/datasets/train_v3.jsonl` (3 contaminated records)
- **Line 160** (Terms: `locomotive`): *"Why didn't the smaller locomotive ever operate on public tracks despite being able reach considerable speeds?..."*
- **Line 193** (Terms: `railway`): *"How might ground level power affect the cost or complexity of certain projects such as railway constructions?..."*
- **Line 278** (Terms: `railway`): *"What happened to Robert Anderson's invention after he attempted to patent it?..."*

### `ml/datasets/train_v4.jsonl` (3 contaminated records)
- **Line 164** (Terms: `locomotive`): *"Why didn't the smaller locomotive ever operate on public tracks despite being able reach considerable speeds?..."*
- **Line 198** (Terms: `railway`): *"How might ground level power affect the cost or complexity of certain projects such as railway constructions?..."*
- **Line 284** (Terms: `railway`): *"What happened to Robert Anderson's invention after he attempted to patent it?..."*

### `ml/datasets/validation.jsonl` (1 contaminated records)
- **Line 31** (Terms: `locomotive`): *"How did the work of inventors like Nicolas - Joseph Cugnot , Richard Trevithick , and Samuel Brown contribute to the evo..."*

### `ml/datasets/validation/validation.jsonl` (1 contaminated records)
- **Line 19** (Terms: `railway`): *"What happened to Robert Anderson's invention after he attempted to patent it?..."*

### `ml/datasets/validation_v3.jsonl` (1 contaminated records)
- **Line 32** (Terms: `locomotive`): *"How did the work of inventors like Nicolas - Joseph Cugnot , Richard Trevithick , and Samuel Brown contribute to the evo..."*

### `ml/datasets/validation_v4.jsonl` (1 contaminated records)
- **Line 32** (Terms: `locomotive`): *"How did the work of inventors like Nicolas - Joseph Cugnot , Richard Trevithick , and Samuel Brown contribute to the evo..."*
