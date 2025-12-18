# faged_pipeline

A modular Python pipeline for architectural and urban spatial analysis, supporting
annotation inspection, base graph construction, connectivity-aware transformation,
layout prototype extraction, and FaGED-based graph comparison.

Each step can be executed **independently** or **combined arbitrarily**, making the
pipeline suitable for both exploratory research and reproducible experiments.

---

## Features

- LabelMe annotation quality checks (visual & structural)
- Area-aware Base Graph (BG) construction
- Connectivity-aware Graph (CaG) transformation
- Automatic selection of optimal graph variant
- Layout prototype extraction via Infomap
- GED / nGED / FaGED (optimal edit paths)
- Batch processing with multiple Markov times
- Research-oriented, transparent, and extensible design

---

## Project Structure

faged_pipeline/
├─ pyproject.toml
├─ README.md
├─ src/
│ └─ faged_pipeline/
│ ├─ init.py
│ ├─ pipeline.py
│ ├─ step0_checks.py
│ ├─ step1_behavior.py
│ ├─ step2_basegraph.py
│ ├─ step3_transform.py
│ ├─ step4_prototype.py
│ └─ step5_faged.py
└─ notebooks/
└─ example_pipeline.ipynb
