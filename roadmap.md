# Mitrokhin Pattern Detection, Asset & Propaganda Index Roadmap

## Project Vision

Build an AI system that can analyze arbitrary documents, biographies, news events, or reports and assign:

1. An **"Asset Index"** score — a quantitative assessment of how closely the text matches KGB/Russian intelligence TTPs (Techniques, Tactics, and Procedures) related to recruitment, cultivation, and control as documented in the Mitrokhin Archive.
2. A **"Propaganda Index"** score — a quantitative assessment of how closely the content matches known Russian propaganda patterns and active-measure narratives, grounded where possible in Mitrokhin active measures material and later Russian information operations.

No graph/network analysis, no link analysis, and no social graph inference. The focus is purely on **what the text says and how it says it**:
- Does this text look like something produced by or about a recruitable/useful asset (Asset Index)?
- Does this text look like Russian propaganda or closely aligned narratives (Propaganda Index)?

**End-user experience:**
- Paste a biography, document, article, or news event into an AI interface
- Receive:
  - Asset Index scores on several dimensions (recruitment susceptibility, compromise potential, etc.)
  - Propaganda Index scores on several dimensions (narrative alignment, active-measures signature, etc.)
  - A breakdown of which TTPs / narrative patterns were detected
  - A short justification describing why the scores were assigned

**Example output:**
```
INPUT: Biography of a Western academic with funding from Russian donors

OUTPUT:

ASSET INDEX
  Recruitment Susceptibility: 4/5
  Compromise Potential: 2/5
  Financial Leverage: 4/5
  Ideological Alignment: 3/5
  Access/Influence: 3/5

  Contributing TTPs Detected:
    - FUNDING_COVERT (4 mentions, high confidence)
    - CULTIVATION_INTELLECTUAL (3 mentions, medium confidence)
    - USEFUL_IDIOT_UNWITTING (2 mentions, low confidence)

  Justification (Asset Index):
    Text reveals substantial unexplained funding from Russian sources, sustained
    intellectual engagement with Kremlin-aligned institutions, and potential
    unwitting amplification of Russian narratives through academic publications.

PROPAGANDA INDEX
  Narrative Alignment with Russian State Messaging: 3/5
  Active-Measures / Disinformation Signature: 2/5
  Useful-Idiot Pattern: 4/5

  Contributing Propaganda Patterns Detected:
    - WESTERN_HYPOCRISY_FRAMING (2 mentions, medium confidence)
    - BOTH_SIDES_FALSE_EQUIVALENCY (2 mentions, medium confidence)
    - GEOPOLITICAL_NEUTRALITY_FRAMING (1 mention, low confidence)

  Justification (Propaganda Index):
    Content consistently frames Western institutions as morally equivalent to or
    worse than Russian actions, uses false equivalencies, and provides intellectual
    cover for Russian policy positions without explicit coordination signals.
```

---

## Phase 1: Foundation & Dataset Preparation

### 1.1 Define the TTP & Narrative Ontology

**Objective:** Create two canonical ontologies:
- A **Recruitment / Asset TTP ontology** grounded in Mitrokhin
- A **Propaganda / Narrative-pattern ontology** grounded in Mitrokhin active measures + modern Russian information operations

**Deliverables:**

- [ ] **Asset TTP Taxonomy Document** (`docs/ttp_taxonomy_asset.md`)
  - Structured list of ~20–40 distinct TTP categories focused on:
    - Recruitment approaches
    - Cultivation methods
    - Control mechanisms
    - Asset handling and tasking patterns
  - Each entry includes:
    - Label (e.g., `RECRUITMENT_IDEOLOGICAL`, `RECRUITMENT_KOMPROMAT`, `CULTIVATION_INTELLECTUAL`)
    - Definition (1–3 sentences)
    - Historical references from Mitrokhin / KGB literature
    - Example excerpts from Mitrokhin-derived texts

- [ ] **Asset Index Dimensions Document** (`docs/asset_index_dimensions.md`)
  - Define 5–8 scoring dimensions, e.g.:
    - `RECRUITMENT_SUSCEPTIBILITY` (0–5)
    - `COMPROMISE_POTENTIAL` (0–5)
    - `EXISTING_ACCESS` (0–5)
    - `FINANCIAL_LEVERAGE` (0–5)
    - `IDEOLOGICAL_ALIGNMENT` (0–5)
    - `OPERATIONAL_UTILITY` (0–5)
    - `CONTROL_RELIABILITY` (0–5)
  - For each dimension, document:
    - What it measures
    - Which TTPs most strongly contribute to it
    - Scoring rubric (what 0, 2, 5 mean; include examples)

- [ ] **Propaganda Pattern Taxonomy Document** (`docs/propaganda_taxonomy.md`)
  - Structured list of ~20–40 narrative and rhetorical patterns, e.g.:
    - `ENCIRCLEMENT_NARRATIVE` ("Russia is surrounded by hostile NATO powers")
    - `NATO_EXPANSION_EXISTENTIAL_THREAT`
    - `WESTERN_HYPOCRISY_FRAMING`
    - `BOTH_SIDES_FALSE_EQUIVALENCY`
    - `WHATABOUTISM`
    - `UKRAINE_CORRUPTION_NARRATIVE`
    - `SANCTIONS_COUNTER_NARRATIVE`
    - `US_DECLINE_DEGENERACY`
  - Each entry includes:
    - Label
    - Definition
    - Key phrases / structures to look for (heuristic patterns)
    - Example excerpts from known Russian propaganda or Mitrokhin active-measures descriptions

- [ ] **Propaganda Index Dimensions Document** (`docs/propaganda_index_dimensions.md`)
  - Define 3–5 scoring dimensions, e.g.:
    - `RUSSIAN_NARRATIVE_ALIGNMENT` (0–5): closeness to documented Kremlin narratives
    - `ACTIVE_MEASURES_SIGNATURE` (0–5): structural similarity to disinformation tradecraft
    - `USEFUL_IDIOT_PATTERN` (0–5): how much the text unknowingly advances Russian interests
  - For each dimension, document:
    - What it measures
    - Which propaganda patterns drive it
    - Scoring rubric (with examples)

**Input:** Mitrokhin Archive, KGB lexicon, active measures literature, documented Russian propaganda case studies

---

### 1.2 Gather and Digitize Source Material

**Objective:** Build two clean corpora:
- Asset / recruitment / TTP corpus
- Propaganda / information-operations corpus

**Deliverables:**

- [ ] **Asset / TTP Corpus** (`data/raw/asset_ttp/`)
  - Digitized excerpts from *The Sword and the Shield* and *The World Was Going Our Way*
  - Public Cambridge Archive transcripts (where available)
  - Academic papers summarizing KGB recruitment & tradecraft
  - Output format: JSONL with fields: `id`, `text`, `source`, `type="asset_ttp"`, `metadata`

- [ ] **Propaganda Corpus** (`data/raw/propaganda/`)
  - Mitrokhin references to active measures
  - Public examples of Russian propaganda (RT, Sputnik, IRA posts, documented campaigns)
  - Academic / NGO analyses of Russian narratives
  - Output format: JSONL with `id`, `text`, `source`, `type="propaganda"`, `metadata`

- [ ] **Preprocessing Pipeline** (`scripts/preprocess.py`)
  - Text normalization (whitespace, case if needed)
  - Section/paragraph/sentence extraction
  - Basic cleaning
  - Attaches metadata (date, publication, etc.)

**Acceptance criteria:**
  - At least 500–1000 sentences/passages in the asset corpus
  - At least 500–1000 sentences/passages in the propaganda corpus
  - All items have clear source metadata

---

### 1.3 Bootstrap Initial Labels with AI-Assisted Annotation

**Objective:** Use an LLM to pre-label asset TTPs and propaganda patterns, then correct/curate manually.

**Deliverables:**

- [ ] **Two Annotation Prompt Templates**
  - `prompts/asset_ttp_labeling_prompt.md`
    - Explains the asset TTP ontology
    - Provides 5–10 example sentences with correct labels
    - Instructs model to output JSON: `{"text": "...", "asset_ttp_labels": ["..."]}`
  - `prompts/propaganda_labeling_prompt.md`
    - Explains propaganda pattern ontology
    - Provides examples
    - JSON: `{"text": "...", "propaganda_labels": ["..."]}`

- [ ] **AI-Assisted Labeling Script** (`scripts/ai_label_bootstrap.py`)
  - Reads from `data/raw/asset_ttp/` and `data/raw/propaganda/`
  - Calls LLM with appropriate prompt
  - Writes candidate labels to `data/labeled_candidates/asset_ttp/` and `.../propaganda/`

- [ ] **Human Review Workflow**
  - You (and any collaborator) review AI labels
  - Use CSV/Label Studio for quick correction
  - Save final labels to `data/labeled_reviewed/asset_ttp/` and `.../propaganda/`

- [ ] **Labeling Guidelines**
  - `docs/labeling_guidelines_asset.md`
  - `docs/labeling_guidelines_propaganda.md`

**Acceptance criteria:**
  - 300–500 manually reviewed, high-confidence labeled sentences for asset TTPs
  - 300–500 manually reviewed, high-confidence labeled sentences for propaganda patterns

---

## Phase 2: Build Two Sentence-Level Classifiers

### 2.1 Prepare Training Data

**Objective:** Turn reviewed labels into training/validation/test splits.

**Deliverables:**

- [ ] **Asset TTP Dataset Splits** (`data/asset_ttp_train/`, `data/asset_ttp_val/`, `data/asset_ttp_test/`)
  - JSONL format:
    ```json
    {
      "id": "asset_sent_001",
      "text": "The agent was cultivated through philosophical discussions over years.",
      "labels": ["CULTIVATION_INTELLECTUAL", "LONG_TERM_APPROACH"],
      "source": "sword_and_shield_p234"
    }
    ```

- [ ] **Propaganda Dataset Splits** (`data/propaganda_train/`, `data/propaganda_val/`, `data/propaganda_test/`)
  - JSONL format:
    ```json
    {
      "id": "prop_sent_001",
      "text": "NATO's expansion leaves Russia no choice but to defend itself.",
      "labels": ["NATO_EXPANSION_EXISTENTIAL_THREAT", "ENCIRCLEMENT_NARRATIVE"],
      "source": "rt_example_2016"
    }
    ```

- [ ] **Dataset README** (`data/README.md`)
  - Label distributions
  - Class imbalance notes

---

### 2.2 Train Asset TTP Classifier

**Objective:** Fine-tune a transformer to detect Mitrokhin-style TTPs in text.

**Deliverables:**

- [ ] **Training Script** (`models/train_asset_ttp_classifier.py`)
  - Multi-label classification (sigmoid output per label)
  - Tracks precision/recall/F1 per label + macro-F1

- [ ] **Checkpoint & Artifacts** (`models/checkpoints/asset_ttp_classifier_v1/`)
  - Model weights
  - Tokenizer
  - Config
  - Metrics JSON

- [ ] **Inference Script** (`scripts/predict_asset_ttps.py`)
  - Input: text
  - Output: per-sentence TTP labels + confidence

---

### 2.3 Train Propaganda Pattern Classifier

**Objective:** Fine-tune a second transformer to detect propaganda narratives.

**Deliverables:**

- [ ] **Training Script** (`models/train_propaganda_classifier.py`)
  - Multi-label classification
  - Similar logging/metrics as asset model

- [ ] **Checkpoint & Artifacts** (`models/checkpoints/propaganda_classifier_v1/`)

- [ ] **Inference Script** (`scripts/predict_propaganda_patterns.py`)
  - Input: text
  - Output: per-sentence propaganda labels + confidence

**Success metrics (both models):**
  - Macro-F1 ≥ 0.75 on test set
  - Manual spot-check on 50 unseen sentences: <5–10% egregious errors

---

## Phase 3: Build the Asset & Propaganda Index Models

### 3.1 Aggregate Sentence-Level Signals to Document-Level Features

**Objective:** Turn predictions from Phase 2 into document-level vectors.

**Deliverables:**

- [ ] **Asset Feature Aggregator** (`scripts/aggregate_asset_ttps_to_features.py`)
  - For each input document/biography:
    - Run `predict_asset_ttps.py`
    - Compute features:
      - Count of each TTP label
      - Normalized frequency (per sentence)
      - Maximum and average confidence per label
      - Simple co-occurrence patterns (e.g., `RECRUITMENT_IDEOLOGICAL + CULTIVATION_INTELLECTUAL`)
    - Output: feature vector in JSON/CSV

- [ ] **Propaganda Feature Aggregator** (`scripts/aggregate_propaganda_to_features.py`)
  - For each input article/document:
    - Run `predict_propaganda_patterns.py`
    - Compute analogous features for propaganda labels

---

### 3.2 Create Hand-Labeled Index Examples

**Objective:** Build small but high-quality labeled sets for supervised index scoring.

**Deliverables:**

- [ ] **Asset Index Example Set** (`data/asset_index_examples/`)
  - 30–50 biographies/articles
  - Each annotated with:
    ```json
    {
      "id": "doc_001",
      "text": "Full biography...",
      "asset_index": {
        "recruitment_susceptibility": 3,
        "compromise_potential": 2,
        "existing_access": 4,
        "financial_leverage": 3,
        "ideological_alignment": 2,
        "operational_utility": 3,
        "control_reliability": 2
      },
      "notes": "Has high-value access and unexplained funding but unclear ideological commitment."
    }
    ```

- [ ] **Propaganda Index Example Set** (`data/propaganda_index_examples/`)
  - 30–50 articles/posts
  - Each annotated with, for example:
    ```json
    {
      "id": "article_001",
      "text": "Full article...",
      "propaganda_index": {
        "russian_narrative_alignment": 4,
        "active_measures_signature": 3,
        "useful_idiot_pattern": 2
      },
      "notes": "Strong alignment with Kremlin NATO talking points but written in mainstream Western outlet."
    }
    ```

- [ ] **Annotation Guidelines**
  - `docs/asset_index_annotation_guidelines.md`
  - `docs/propaganda_index_annotation_guidelines.md`

---

### 3.3 Train Asset Index & Propaganda Index Models

**Objective:** Learn mappings from feature vectors → index scores.

**Deliverables:**

- [ ] **Asset Index Model** (`models/train_asset_index_model.py`)
  - Multi-output regression or multi-task classification
  - Input: features from `aggregate_asset_ttps_to_features.py`
  - Output: 5–8 asset index scores

- [ ] **Propaganda Index Model** (`models/train_propaganda_index_model.py`)
  - Similar structure for propaganda scores

- [ ] **Saved Models & Cards**
  - `models/asset_index_v1/` + `models/asset_index_v1_card.md`
  - `models/propaganda_index_v1/` + `models/propaganda_index_v1_card.md`

**Target:**
  - Correlation ≥ 0.75 with human labels on held-out examples
  - Qualitative agreement with your own expert judgment most of the time

---

## Phase 4: End-to-End Pipeline & Explainability

### 4.1 Unified Inference Pipeline

**Objective:** One interface that goes from raw text → both indexes + explanations.

**Deliverables:**

- [ ] **Pipeline Wrapper** (`src/index_pipeline.py`)
  - Steps:
    1. Split input into sentences
    2. Run asset TTP classifier → collect predictions
    3. Run propaganda classifier → collect predictions
    4. Aggregate to features for each index
    5. Run index models → get numeric scores
    6. Call explainer (below) → textual justification
  - Method: `analyze(text) → {asset_index, propaganda_index, explanations, per_sentence_labels}`

- [ ] **CLI Tool** (`scripts/run_analysis.py`)
  - Usage:
    ```bash
    python scripts/run_analysis.py --input-file example.txt --output-json result.json
    ```

---

### 4.2 Explainability Layer

**Objective:** Human-readable justifications grounded in the detected patterns.

**Deliverables:**

- [ ] **Explanation Generator** (`src/explainer.py`)
  - Inputs:
    - Asset index scores
    - Propaganda index scores
    - Per-sentence TTP / propaganda predictions
  - Outputs per index:
    - Top contributing labels + counts + average confidence
    - 3–10 key sentences quoted from the input
    - Short natural-language summary (can be LLM-assisted but bound to evidence)

- [ ] **Example Notebooks** (`notebooks/`)
  - `01_basic_demo.ipynb`: run pipeline on a biography
  - `02_propaganda_demo.ipynb`: run pipeline on an article

---

### 4.3 API / Simple UI (Optional MVP)

**Objective:** Simple way to use the system interactively.

**Deliverables:**

- [ ] **FastAPI Service** (`src/api.py`)
  - `POST /analyze` → returns full JSON output

- [ ] **Minimal Web UI** (`frontend/index.html`, `frontend/app.js`)
  - Text box for input
  - Shows asset and propaganda scores side-by-side
  - Shows key sentences and labels

---

## Phase 5: Evaluation, Iteration, Documentation

### 5.1 Real-World Evaluation

- Build a small evaluation set of real biographies and articles
- Have you + collaborator score them blind
- Compare human scores vs. model scores
- Document where the system fails (false positives/negatives)

### 5.2 Iterate

- Expand labeled datasets where performance is weakest
- Refine ontologies (merge or split labels as needed)
- Retrain classifiers and index models

### 5.3 Documentation

- Update `README.md` with:
  - Clear statement: **no network, link, or social graph analysis** — content-only
  - Example usage
  - Limitations and ethical constraints

---

## Repository Structure (Content-Only Version)

```
mitrokhin-asset-index/
├── README.md
├── docs/
│   ├── ttp_taxonomy_asset.md
│   ├── propaganda_taxonomy.md
│   ├── asset_index_dimensions.md
│   ├── propaganda_index_dimensions.md
│   ├── labeling_guidelines_asset.md
│   ├── labeling_guidelines_propaganda.md
│   ├── asset_index_annotation_guidelines.md
│   ├── propaganda_index_annotation_guidelines.md
│   └── evaluation_report.md
├── data/
│   ├── raw/
│   │   ├── asset_ttp/
│   │   └── propaganda/
│   ├── labeled_candidates/
│   │   ├── asset_ttp/
│   │   └── propaganda/
│   ├── labeled_reviewed/
│   │   ├── asset_ttp/
│   │   └── propaganda/
│   ├── asset_ttp_train/ asset_ttp_val/ asset_ttp_test/
│   ├── propaganda_train/ propaganda_val/ propaganda_test/
│   ├── asset_index_examples/
│   └── propaganda_index_examples/
├── models/
│   ├── train_asset_ttp_classifier.py
│   ├── train_propaganda_classifier.py
│   ├── train_asset_index_model.py
│   ├── train_propaganda_index_model.py
│   └── checkpoints/
│       ├── asset_ttp_classifier_v1/
│       ├── propaganda_classifier_v1/
│       ├── asset_index_v1/
│       └── propaganda_index_v1/
├── src/
│   ├── __init__.py
│   ├── index_pipeline.py
│   ├── explainer.py
│   └── api.py
├── scripts/
│   ├── preprocess.py
│   ├── ai_label_bootstrap.py
│   ├── predict_asset_ttps.py
│   ├── predict_propaganda_patterns.py
│   ├── aggregate_asset_ttps_to_features.py
│   ├── aggregate_propaganda_to_features.py
│   └── run_analysis.py
├── notebooks/
│   ├── 01_basic_demo.ipynb
│   └── 02_propaganda_demo.ipynb
├── frontend/
│   ├── index.html
│   └── app.js
├── tests/
│   ├── test_asset_ttp_classifier.py
│   ├── test_propaganda_classifier.py
│   ├── test_index_models.py
│   └── test_pipeline.py
├── requirements.txt
└── setup.py
```
