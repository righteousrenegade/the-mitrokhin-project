# Mitrokhin Pattern Detection & Asset Index Roadmap

## Project Vision

Build an AI system that can analyze arbitrary documents, biographies, news events, or reports and assign an **"Asset Index"** score—a quantitative assessment of how closely the text matches KGB/Russian intelligence TTPs (Techniques, Tactics, and Procedures) documented in the Mitrokhin Archive.

**End-user experience:**
- Paste text into an AI interface
- Receive a composite risk/asset score (0–5 scale)
- Get a detailed breakdown of which TTPs were detected
- Understand why the score was assigned (explainability)

**Example output:**
```
INPUT: Biography of a Western academic with funding from Russian donors
OUTPUT:
  Recruitment Susceptibility: 4/5
  Compromise Potential: 2/5
  Financial Leverage: 4/5
  Ideological Alignment: 3/5
  Access/Influence: 3/5
  
  Contributing TTPs Detected:
    - FUNDING_COVERT (4 mentions, high confidence)
    - CULTIVATION_INTELLECTUAL (3 mentions, medium confidence)
    - USEFUL_IDIOT_UNWITTING (2 mentions, low confidence)
  
  Justification:
    Text reveals substantial unexplained funding from Russian sources, sustained 
    intellectual engagement with Kremlin-aligned institutions, and potential 
    unwitting amplification of Russian narratives through academic publications.
```

---

## Phase 1: Foundation & Dataset Preparation

### 1.1 Define the TTP Ontology

**Objective:** Create a canonical list of KGB/Russian intelligence TTPs grounded in Mitrokhin Archive analysis.

**Deliverables:**
- [ ] **TTP Taxonomy Document** (`docs/ttp_taxonomy.md`)
  - Structured list of 20–40 distinct TTP categories
  - Each entry includes:
    - Label (e.g., `RECRUITMENT_IDEOLOGICAL`)
    - Definition (1–2 sentences)
    - Historical references from Mitrokhin/KGB literature
    - Real-world examples from the archive
    - Related tactics (parent/child relationships)

- [ ] **Asset Index Dimensions Document** (`docs/asset_index_dimensions.md`)
  - Define 5–8 scoring dimensions, e.g.:
    - `RECRUITMENT_SUSCEPTIBILITY` (0–5): How likely is this person/entity to be recruited?
    - `COMPROMISE_POTENTIAL` (0–5): Blackmail, scandal, or leverage exploitable?
    - `EXISTING_ACCESS` (0–5): Does the person/entity have valuable information or influence?
    - `FINANCIAL_LEVERAGE` (0–5): Can money be used?
    - `IDEOLOGICAL_ALIGNMENT` (0–5): Alignment with Russian state interests?
    - `OPERATIONAL_UTILITY` (0–5): How useful would they be as an asset?
    - `CONTROL_RELIABILITY` (0–5): How controllable/stable is the relationship?
  - For each dimension, document:
    - What it measures
    - How it relates to TTPs
    - Scoring rubric (what 0, 2, 5 mean)

**Input:** Mitrokhin Archive books/documents, KGB lexicon, active measures literature

---

### 1.2 Gather and Digitize Source Material

**Objective:** Build a clean, processable corpus of Mitrokhin-derived text.

**Deliverables:**
- [ ] **Source Material Repository** (`data/raw/`)
  - Digitized excerpts from *The Sword and the Shield* (Mitrokhin/Andrew)
  - Excerpts from *The World Was Going Our Way* (related operations)
  - Public Cambridge Archive transcripts (where available)
  - Academic papers analyzing Mitrokhin revelations
  - Documents on KGB active measures and recruitment

- [ ] **Preprocessing Pipeline** (`scripts/preprocess.py`)
  - Text normalization
  - Section/paragraph extraction
  - Metadata tagging (source, date, operation type)
  - Output: clean JSONL format with `id`, `text`, `source`, `metadata`

**Acceptance criteria:**
  - Minimum 500 sentences/passages from Mitrokhin materials
  - Each passage cleanly attributed
  - No corrupted/garbled text

---

### 1.3 Bootstrap Initial Labels with AI-Assisted Annotation

**Objective:** Rapidly generate candidate TTP labels for corpus material using an LLM, then refine via human review.

**Deliverables:**
- [ ] **Annotation Prompt Template** (`prompts/ttp_labeling_prompt.md`)
  - Few-shot prompt that describes each TTP category
  - Examples of sentences and their TTP labels
  - Instructions to output JSON: `{"text": "...", "labels": [...]}`
  - Clear instruction to *only use labels from the ontology*

- [ ] **AI-Assisted Labeling Script** (`scripts/ai_label_bootstrap.py`)
  - Reads raw corpus from `data/raw/`
  - Batches sentences
  - Calls LLM API (OpenAI, Claude, local model) with annotation prompt
  - Captures predicted labels + confidence
  - Outputs to `data/labeled_candidates/`

- [ ] **Human Review Interface** (spreadsheet or Label Studio setup)
  - Simple CSV or Label Studio project with:
    - Pre-filled AI predictions
    - Toggle to accept/reject/correct each label
    - Comments field
  - Output: `data/labeled_reviewed/` (high-confidence labels only)

- [ ] **Labeling Guidelines Document** (`docs/labeling_guidelines.md`)
  - When to use each TTP label
  - Common ambiguous cases and how to resolve
  - Quality standards (inter-annotator agreement target: 80%+)

**Acceptance criteria:**
  - 300–500 sentences with reviewed TTP labels
  - Each label traceable to 1+ TTP categories
  - Consistent application of rules across dataset

---

## Phase 2: Build the TTP Classifier

### 2.1 Prepare Training Data

**Objective:** Convert reviewed labels into a machine-learning-ready format.

**Deliverables:**
- [ ] **Training Dataset Splits** (`data/train/`, `data/val/`, `data/test/`)
  - Format: JSONL with fields:
    ```json
    {
      "id": "sent_001",
      "text": "The agent was cultivated through philosophical discussions over years.",
      "labels": ["CULTIVATION_INTELLECTUAL", "LONG_TERM_APPROACH"],
      "source": "sword_and_shield_p234"
    }
    ```
  - Train set: 60% (300 sentences)
  - Validation set: 20% (100 sentences)
  - Test set: 20% (100 sentences)
  - Stratified by TTP distribution

- [ ] **Dataset Documentation** (`data/README.md`)
  - Label distribution charts
  - Class imbalance notes (how to handle if present)
  - Data quality flags


---

### 2.2 Train Sentence-Level TTP Classifier

**Objective:** Build a fine-tuned transformer model that predicts TTPs for any input sentence.

**Deliverables:**
- [ ] **Model Training Script** (`models/train_ttp_classifier.py`)
  - Loads JSONL data
  - Fine-tunes a pre-trained transformer (RoBERTa, BERT, or similar)
  - Multi-label classification task
  - Tracks metrics: precision, recall, F1 per label + macro-F1
  - Saves best checkpoint + hyperparameters

- [ ] **Trained Model Artifacts** (`models/checkpoints/ttp_classifier_v1/`)
  - Weights, tokenizer, config
  - Performance metrics JSON
  - Confusion matrix (which labels get confused?)

- [ ] **Model Card** (`models/ttp_classifier_v1_card.md`)
  - Architecture, training approach
  - Performance on test set
  - Known limitations
  - Inference time / resource requirements
  - False positive / false negative analysis

- [ ] **Inference Script** (`scripts/predict_ttps.py`)
  - Takes raw text → outputs sentence-level predictions with confidence
  - JSON output: `{"sentences": [{"text": "...", "predicted_labels": [...], "confidence": [...]}, ...]}`

**Success metrics:**
  - Test set F1 ≥ 0.75 (per-label macro-F1)
  - <5% error on a manual spot-check of 50 new sentences

---

## Phase 3: Build the Asset Index Model

### 3.1 Aggregate TTP Signals into Features

**Objective:** Convert sentence-level TTP predictions into document-level signals.

**Deliverables:**
- [ ] **Feature Aggregation Script** (`scripts/aggregate_ttps_to_features.py`)
  - Input: predicted TTPs for all sentences in a document
  - Outputs: feature vector with:
    - Count of each TTP label
    - Max confidence for each TTP label
    - Normalized frequency (TTP count / total sentences)
    - Co-occurrence patterns (e.g., `RECRUITMENT + KOMPROMAT` score)
    - Semantic clustering (e.g., "recruitment tactics" frequency)
  - Output format: JSON or pandas DataFrame


---

### 3.2 Curate Labeled Examples for Asset Index Training

**Objective:** Hand-label a small set of realistic documents with asset index scores.

**Deliverables:**
- [ ] **Annotated Asset Index Dataset** (`data/asset_index_examples/`)
  - 30–50 documents (biographies, news articles, reports) with hand-assigned scores
  - Each entry:
    ```json
    {
      "id": "doc_001",
      "text": "Full biography or article here...",
      "source": "example_bio_academic.txt",
      "asset_index": {
        "recruitment_susceptibility": 3,
        "compromise_potential": 2,
        "existing_access": 4,
        "financial_leverage": 3,
        "ideological_alignment": 2,
        "operational_utility": 3,
        "control_reliability": 2
      },
      "annotations_by": "primary_researcher",
      "reasoning": "Has valuable academic position, exposure to U.S. research, but limited ideological alignment."
    }
    ```

- [ ] **Annotation Guidelines** (`docs/asset_index_annotation_guidelines.md`)
  - When to assign each score (0, 1, 2, 3, 4, 5)
  - Examples of documents at each level
  - How to justify the score


---

### 3.3 Train Asset Index Regressor

**Objective:** Build a model that predicts asset index scores from TTP features.

**Deliverables:**
- [ ] **Asset Index Model Training Script** (`models/train_asset_index_model.py`)
  - Input features: TTP aggregates from 3.1 + optional metadata (country, sector, etc.)
  - Target: asset index scores (0–5 for each dimension)
  - Model type: multi-output regression (scikit-learn, XGBoost) or multi-task neural net
  - Handles small dataset gracefully (regularization, cross-validation)
  - Outputs: trained model + feature importance analysis

- [ ] **Trained Model Artifacts** (`models/asset_index_v1/`)
  - Serialized model (pickle, joblib, etc.)
  - Feature importance scores
  - Cross-validation metrics (RMSE, MAE per dimension)

- [ ] **Model Card** (`models/asset_index_v1_card.md`)
  - Training approach, data size
  - Performance metrics
  - Feature importance (which TTPs drive which scores?)
  - Known limitations (small training set, etc.)


---

## Phase 4: Build the Full Pipeline & Explainability Layer

### 4.1 Integrate into End-to-End Pipeline

**Objective:** Create a unified inference script that takes raw text → asset index score + explanation.

**Deliverables:**
- [ ] **Unified Inference Script** (`scripts/full_pipeline.py`)
  - Input: document text
  - Step 1: Split into sentences
  - Step 2: Predict TTPs for each sentence (2.2)
  - Step 3: Aggregate TTP features (3.1)
  - Step 4: Predict asset index scores (3.3)
  - Output: JSON with all intermediate results + final scores

- [ ] **Pipeline Wrapper Class** (`src/asset_index_pipeline.py`)
  - Encapsulates the pipeline for easy reuse
  - Methods: `analyze(text) → Dict[asset_scores, ttp_breakdown, explanation]`
  - Error handling, logging

---

### 4.2 Build Explainability Layer

**Objective:** Generate human-readable justifications for asset index scores.

**Deliverables:**
- [ ] **Explanation Generator** (`src/explainer.py`)
  - Rules-based + LLM-based approach:
    - Identify top-contributing TTPs for each asset dimension
    - Rank sentences by confidence + impact on score
    - Summarize in natural language
  - Output: structured JSON explanation

  Example:
  ```json
  {
    "recruitment_susceptibility": {
      "score": 4,
      "top_contributing_ttps": [
        {"ttp": "CULTIVATION_INTELLECTUAL", "mentions": 3, "confidence": 0.92},
        {"ttp": "IDEOLOGICAL_APPEAL", "mentions": 2, "confidence": 0.87}
      ],
      "key_sentences": [
        "The subject regularly attends symposiums hosted by Kremlin-aligned think tanks.",
        "Long-standing academic interest in alternative geopolitical frameworks."
      ],
      "summary": "Subject shows strong receptivity to intellectual cultivation and has demonstrated ideological sympathies that align with Russian state narratives. Extended engagement with Russian academic networks suggests opportunity for recruitment."
    }
  }
  ```

- [ ] **Visualization Templates** (`notebooks/visualize_results.ipynb`)
  - Asset index radar chart
  - TTP contribution bar chart
  - Key sentence highlighting
  - Example outputs for demo purposes

---

### 4.3 API / Web Interface (Optional, MVP)

**Objective:** Make the system accessible via API or simple web UI.

**Deliverables:**
- [ ] **FastAPI Server** (`src/api.py`)
  - Endpoint: `POST /analyze`
  - Input: `{"text": "..."}`
  - Output: Full asset index + explanation JSON
  - Rate limiting, logging, error handling

- [ ] **Simple Web UI** (`frontend/index.html` + `frontend/app.js`)
  - Textarea for text input
  - Submit button
  - Display asset index scores + breakdown
  - Copy-to-clipboard for full output
  - Entirely client-side (optional: call local/remote API)

- [ ] **Docker Setup** (`Dockerfile`, `docker-compose.yml`)
  - Containerize the API + model
  - Easy local deployment

---

## Phase 5: Refinement, Evaluation & Documentation

### 5.1 Test on Real-World Data

**Objective:** Validate the system on held-out examples that mimic real use cases.

**Deliverables:**
- [ ] **Test Dataset** (`data/test_cases/`)
  - 20–30 diverse documents:
    - News articles (real & synthetic)
    - Academic biographies
    - Corporate profiles
    - Social media posts
    - Open-source intelligence reports
  - Hand-labeled ground truth asset indices by domain experts
  - Blind evaluation (researchers don't see model output until after scoring)

- [ ] **Evaluation Report** (`docs/evaluation_report.md`)
  - Accuracy metrics (how often does the model match expert scores?)
  - Failure analysis (where does it go wrong?)
  - Ablation studies (how much does each TTP category contribute?)
  - Robustness testing (adversarial examples, paraphrasing)

---

### 5.2 Iterate & Improve

**Objective:** Use evaluation results to refine models and data.

**Deliverables:**
- [ ] **Refined Labeled Dataset v2** (`data/labeled_reviewed_v2/`)
  - If v1 has systematic errors, expand & correct
  - Aim for 500–1000 sentences

- [ ] **Updated TTP Classifier v2** (`models/checkpoints/ttp_classifier_v2/`)
  - Retrain on expanded dataset
  - Target test F1 ≥ 0.80

- [ ] **Updated Asset Index Model v2** (`models/asset_index_v2/`)
  - Retrain with revised ontology (if needed)
  - Better feature engineering

---

### 5.3 Documentation & Community Contribution

**Objective:** Make the project reproducible and shareable.

**Deliverables:**
- [ ] **Comprehensive README** (`README.md`)
  - Project overview, use cases, ethical considerations
  - Quick start guide
  - Architecture diagram
  - Installation & usage examples

- [ ] **Architecture Document** (`docs/architecture.md`)
  - System components
  - Data flow diagram
  - Model descriptions
  - Scalability notes

- [ ] **Contributing Guide** (`CONTRIBUTING.md`)
  - How to improve the TTP ontology
  - How to add new test cases
  - How to retrain models


---

## Phase 6: Advanced Features (Optional, Post-MVP)

### 6.1 Interactive Explanation UI
- Highlight sentences contributing to each score
- Show confidence levels

### 6.2 Comparative Analysis
- Compare multiple documents side-by-side
- Identify networks or patterns across multiple entities

### 6.3 Temporal Analysis
- Track asset index changes over time
- Detect shifts in TTPs or risk profile

### 6.4 Continuous Learning
- Feedback loop: user corrections → model retraining
- Active learning: flag low-confidence predictions for review

---

## Milestones

| Phase | Milestone | Duration |
|-------|-----------|----------|
| **1.1** | TTP Ontology defined |
| **1.2** | Source material gathered & cleaned |
| **1.3** | Bootstrap labels + manual review |
| **2.1** | Training data ready |
| **2.2** | TTP classifier trained & validated |
| **3.1–3.2** | Asset index features + training data |
| **3.3** | Asset index model trained |
| **4.1–4.2** | Full pipeline + explainability |
| **5.1–5.2** | Testing, evaluation, iteration |
| **5.3** | Documentation complete | 2–3 weeks |


---

## Success Criteria

- [ ] TTP classifier achieves ≥0.80 F1 on held-out test set
- [ ] Asset index model predictions agree with expert annotations ≥75% of the time
- [ ] System can process a typical biography (500–1000 words) in <5 seconds
- [ ] Explainability output is readable and actionable for non-ML users
- [ ] Codebase is documented, reproducible, and open-source ready
- [ ] At least 1 external reviewer validates use case and methodology

---

## Risk & Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Small training dataset → overfitting | Model fails on new data | Use transfer learning, regularization, data augmentation |
| TTP ontology poorly defined → noisy labels | Garbage in, garbage out | Iterate on ontology based on early results; achieve high inter-annotator agreement |
| Adversarial/synthetic text fools model | False positives create liability | Test robustness; document limitations; add human review step |
| Scope creep (too many TTPs, asset dims) | Project becomes unmanageable | Ruthlessly prioritize; start with 20–30 TTPs and 5–7 asset dims |
| Ethical misuse (over-confident scoring) | Reputational/legal liability | License clearly, add disclaimers, require human judgment in loop |

---

## Next Steps

1. **This week:** Read Mitrokhin source material, sketch TTP taxonomy (Phase 1.1)
2. **Next week:** Create TTP taxonomy document + asset index dimensions (Phase 1.1 complete)
3. **Week 3:** Begin source material digitization (Phase 1.2)
4. **Week 4:** Set up annotation infrastructure + AI labeling prompt (Phase 1.3)
5. **Ongoing:** Iterate, refine, and expand as you learn more


