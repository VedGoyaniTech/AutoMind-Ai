# 🛡️ AutoMind AI — External Data-Source Policy & Data Governance

**Version:** 1.0.0  
**Effective Date:** 2026-09-10  
**Status:** Approved & Enforced  

---

## 1. Core Operating Principle

> **Vehicle facts, variant specifications, ex-showroom prices, safety ratings, RTO taxation rules, and insurance assumptions are source-backed, versioned product data—never memorized into LLM training weights.**

AutoMind AI enforces strict factual separation:
1. **Relational / Structured Product Data (SQL):** All dynamic pricing, specifications, safety ratings, and tax rules reside in relational models backed by an immutable `sources` provenance record, an official publication date, an effective date, a last verified timestamp, and a human review status.
2. **Knowledge Retrieval Documents (RAG):** Official guides, safety protocols, and regulatory explainers reside in Markdown files with mandatory `.metadata.json` sidecars tracking license, publisher, checksum, and verification dates.
3. **Fine-Tuning / Evaluation Datasets (ML):** Models are trained strictly on task behavior (intent routing, vehicle entity disambiguation, multi-lingual dialogue, tool-call formatting, and polite abstention when facts are unverified). Fine-tuning never embeds mutable catalogue facts.

---

## 2. Approved Source Families & Strict Ingestion Rules

| Source Family | Permitted Use | Required Metadata & Proof | Prohibitions / Constraints |
| :--- | :--- | :--- | :--- |
| **OEM Official Brochures, Price Lists & Portals** (e.g., Tata Motors, Hyundai India, Maruti Suzuki) | Ex-showroom prices, technical dimensions, powertrain specs, feature matrices. | Source document URL or file path, publication date, effective date, sha256 checksum, license/permission type. | Do NOT scrape unauthorized dealer portals. Ex-showroom prices must be dated and designated by city/state. |
| **Bharat NCAP (BNCAP)** | India crash safety star ratings and adult/child protection scores. | Tested vehicle make/model/variant, test date, adult score, child score, official report URL. | **NEVER** transfer ratings to a different facelift, generation, or untested variant. |
| **Global NCAP (Safer Cars for India)** | Historical crash safety evidence. | Programme (`Global NCAP`), test year, protocol edition, tested variant. | Must clearly display protocol difference note (e.g., pre-2022 vs post-2022 protocol). |
| **State Transport Departments / MoRTH / Parivahan** | RTO road tax percentages, green cess, registration fees, BH-series rules. | Official gazette notification reference, state code, fuel type slab, price threshold, effective date. | Must require human review (`review_status = "approved"`) before pricing engine activation. |
| **VAHAN / Open Government Data (OGD)** | Macro sales velocity, fuel-mix trends, segment registration signals. | Public aggregate dataset citation, release date, ministry attribution. | **STRICTLY FORBIDDEN:** Any individual vehicle RC number, VIN, owner identity, or personal registration records. |
| **SIAM (Society of Indian Automobile Manufacturers)** | Macro production, domestic sales, and export volume trends. | Licensed dataset agreement ID, subscription validity, attribution notice. | Model-level confidential sales data cannot be ingested without commercial distribution rights. |
| **BEE / CAFE / ARAI** | Fuel efficiency standards, CAFE compliance benchmarks, certified range. | Official ARAI certificate number or BEE notification reference. | Certified test figures must be labeled as laboratory test cycles, not real-world guarantees. |
| **Government Charging Registries / Licensed EV APIs** | Public EV charging station locations, connector types, power capacity. | Source registry ID, coordinates, last-verified timestamp. | Do NOT claim real-time live slot availability without active telemetry connection and recent heartbeat. |
| **IRDAI / Insurer Master Tariffs** | Motor OD and TP insurance slab baselines. | Tariff schedule circular number, effective financial year. | Outputs must explicitly state: *"Indicative estimate based on IRDAI norms; actual insurer quote may vary."* |

---

## 3. Explicitly Prohibited Data Sources & Practices

The following data categories and acquisition techniques are strictly prohibited across AutoMind AI:
- ❌ **Unlicensed Competitor & Dealer Scraping:** Automated scraping of CarDekho, CarWale, ZigWheels, or individual dealership websites.
- ❌ **Search Snippets as Ground Truth:** Unverified web search summaries, search engine snippets, or automated LLM web crawlers storing facts without document proof.
- ❌ **Random Kaggle / Community Datasets:** Unverified third-party CSVs/JSONs with unknown lineage, outdated prices, or speculative specs.
- ❌ **TweetEval & Unrelated NLP Benchmarks:** Inclusion of TweetEval (tweet stance/sentiment) or unrelated NLP corpora in automotive fine-tuning.
- ❌ **Contaminated Multi-Domain Datasets:** Corpora containing non-automotive domains (e.g. railway locomotives, corporate balance sheets, stock tickers) such as `master_v4_combined_dataset.jsonl`.
- ❌ **Unredacted User Feedback / PII:** Customer chat logs containing names, phone numbers, email addresses, license plate numbers, or VINs.
- ❌ **Model Hallucinations as Ground Truth:** Treating synthetic LLM outputs as verified automotive facts without independent human validation.

---

## 4. Source & Fact Verification Lifecycle

Every piece of automotive factual data transitions through a deterministic state machine:

```
[draft] ──> [pending_review] ──> [approved] ──> [stale] (after review_cycle / price revision)
                                     │
                                     └──> [rejected / revoked]
```

### Lifecycle Rules:
1. **Draft:** Data imported from an automated pipeline or staging file. Not accessible to user-facing RAG or pricing engine.
2. **Pending Review:** Awaiting verification by an automotive domain specialist against official OEM/Gov documents.
3. **Approved:** Verified against an official document with recorded `source_id`, `effective_date`, and `last_verified_at`. Available to production query engines.
4. **Stale:** A fact whose `last_verified_at` exceeds the threshold (e.g., 90 days for prices, 180 days for specs) or where a newer notification has been published. Pricing engine returns a freshness warning.
5. **Revoked:** Erroneous or superseded record. Preserved in history for auditability, but deactivated via `revoked = True`.

---

## 5. Instructions for Data Owners: Supplying the First 25-Model Catalogue

To onboard the initial 25 high-demand Indian vehicle models (e.g. Tata Nexon, Hyundai Creta, Maruti Brezza, Mahindra XUV700, etc.) without legal risk:

### Step 1: Legal Acquisition & Archiving
1. Download official manufacturer PDF brochures and official ex-showroom price lists directly from official OEM media or consumer portals:
   - Tata Motors: `tatamotors.com` / `cars.tatamotors.com`
   - Hyundai India: `hyundai.com/in`
   - Maruti Suzuki Arena / Nexa: `marutisuzuki.com`
   - Mahindra Auto: `auto.mahindra.com`
2. Download official Bharat NCAP test sheets from `bharatncap.org.in`.
3. Download state RTO road tax notifications from Parivahan/State Transport gazettes.
4. Archive PDFs in secure object storage or `data/raw/` (git-ignored) with SHA-256 hashes.

### Step 2: Prepare the Catalogue Import JSON
Format the catalogue using the validated schema (`backend/app/schemas/provenance.py` and sample in `backend/data/fixtures/sample_catalogue_import.json`):
- Every source must specify: `source_uid`, `publisher`, `licence`, `acquisition_method = "direct_download"`, `allowed_use = "internal_rag"`, `published_date`, and `review_status = "approved"`.
- Prices must be exact strings for Decimal conversion (e.g. `"799990.00"`).
- Every variant must explicitly reference its `source_uid`.

### Step 3: Dry-Run Validation
Run the validation CLI inside the backend environment:
```bash
docker run --rm -v "$(pwd):/project" -w /project/backend project-v-backend:latest \
  python scripts/data_foundation_cli.py validate-catalogue-import --file data/incoming/catalogue_25_models.json --dry-run
```

### Step 4: Authorised Ingestion
Once validation passes with zero errors, execute the import:
```bash
docker run --rm -v "$(pwd):/project" -w /project/backend project-v-backend:latest \
  python scripts/data_foundation_cli.py import-catalogue-data --file data/incoming/catalogue_25_models.json
```

---

## 6. Audit & Compliance SLA

- **Bi-Weekly Audit:** The CLI command `python scripts/data_foundation_cli.py audit-training-data` must run in CI/CD before any model training or release.
- **Price Freshness:** Ex-showroom prices older than 45 days trigger an automated administrative alert.
- **RTO Tax Slabs:** Changes in state budget gazettes must be published as a new `RTORuleVersion` with effective date, leaving the previous version intact for historical lookups.
