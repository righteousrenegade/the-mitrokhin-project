# EU vs Disinfo Pattern Extraction

A self-contained module for analyzing disinformation cases from the EU vs Disinfo database to build comprehensive propaganda pattern databases for AI training.

## Important Note

Due to anti-bot protection on the EU vs Disinfo website, **automated scraping is not currently possible**. This module now focuses on **manual data collection and analysis tools**.

## Features

- **Manual Data Collection Workflow**: Structured process for collecting propaganda patterns
- **Interactive Data Entry**: Helper tools for organizing manually collected examples  
- **Pattern Analysis Framework**: Taxonomy-based classification system
- **AI Context Generation**: Export data for use in AI system prompts
- **Demo Analysis Tools**: Test pattern recognition capabilities

## Quick Start - LLM-Powered Workflow

### 1. Set up the environment
```bash
pip install -r requirements.txt
```

### 2. Start LM Studio
1. Install and run LM Studio with a local model
2. Test connection:
```bash
python llm_pattern_extractor.py --test-connection
```

### 3. Process articles with LLM analysis
**Interactive mode** (single articles):
```bash
python llm_pattern_extractor.py --interactive
```

**Batch mode** (multiple articles):
```bash
# Create template
python batch_processor.py --create-csv-template

# Fill in template.csv with your articles, then:
python batch_processor.py --csv template.csv
```

### 4. Generate comprehensive TTP definitions
```bash
python ttp_definition_generator.py
```

### 5. Test pattern recognition
```bash
python propaganda_analyzer_demo.py
```

### Programmatic Usage

```python
from euvsdisinfo import EUDisinfoExtractor

# Create extractor with custom output directory
extractor = EUDisinfoExtractor(output_dir="my_corpus")

# Process article list
list_url = "https://euvsdisinfo.eu/disinformation-cases/?view=list"
processed_ids = extractor.process_article_list(list_url, max_articles=100)

# Generate taxonomy from corpus
taxonomy = extractor.generate_taxonomy_candidates(min_frequency=3)
```

## Output Structure

```
data/corpus/
├── articles/           # EU vs Disinfo analyses + metadata
├── sources/            # Original source articles (propaganda content)
├── summaries/          # Quick reference summaries
├── batch_summary_*.json
└── taxonomy_candidates_*.json
```

## Documentation

- `docs/eu_disinfo_extractor_guide.md` - Comprehensive usage guide
- `docs/ENHANCEMENT_SUMMARY.md` - Technical implementation details

## Scripts

- `scripts/extract_eu_disinfo.py` - Example usage patterns
- `eu_disinfo_extractor.py` - Main CLI interface

## Integration

This module is designed to integrate with the larger Mitrokhin project for propaganda analysis and taxonomy development. The extracted corpus provides training data for machine learning models and taxonomy refinement.

## Development

```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests
pytest

# Format code
black .
```