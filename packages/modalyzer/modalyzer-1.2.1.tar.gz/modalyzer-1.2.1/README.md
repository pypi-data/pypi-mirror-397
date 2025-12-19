# Modalyzer

Open‑source Python library for Operational Modal Analysis (OMA) and system identification.  
Modalyzer provides multiple algorithms — EFDD/FDD, SSI (cov/data), ITD, and PolyMAX — along with helpers for preprocessing, stabilization diagrams, and drawing mode shapes for common structures.

> **Status:** research code under active revision, shared to accompany an open‑source paper. Interfaces may still evolve.

---

## Key Features

- **Preprocessing**: detrend, band‑pass filter, decimate, channel removal, and auto‑sync across channels.
- **Frequency Domain Decomposition (EFDD/FDD)**: PSD SVD, manual peak picking, complex mode shapes, SDOF autocorrelation damping.
- **SSI (cov & data variants)**: state‑space estimation and pole stabilization.
- **ITD**: fast coarse extraction of poles and damping.
- **PolyMAX / p‑LSCF**: accurate poles and mode shapes and a stabilization diagram.
- **Plots**: stabilization diagrams, MAC, and structure‑specific mode‑shape drawings (Farrar 4‑story frame, bridges, etc.).

---

## Installation

Modalyzer is currently distributed as source. You can install it in editable mode:

```bash
# Clone your (test) repository then install locally
git clone https://github.com/<your-username>/modalyzer-test.git
cd modalyzer-test
python -m venv .venv
# Windows PowerShell:
. .venv\\Scripts\\Activate.ps1
pip install -U pip
pip install -e .  # optional; or just run with PYTHONPATH
```

If you don't have a `setup.py/pyproject.toml` yet, you can still **use it as a plain package** by keeping this repo root on your `PYTHONPATH` or by running examples from the repo root.

### Dependencies
The modules use: `numpy`, `pandas`, `matplotlib`, `scipy`, `torch`, and optionally `plotly`. Install them with:
```bash
pip install numpy pandas matplotlib scipy torch plotly
```

---


## Repository Layout

```
modalyzer/
├─ src/modalyzer/
│  ├─ Preprocess.py         # preprocess(), choose_modes(), results_table(), etc.
│  ├─ EFDD.py               # FDD_SVD_Diagram(), FDD_ModeShape(), FDD_Damping(), ...
│  ├─ SSI.py                # SSI_COV(), SSI_DATA(), modal_parameters(), Stable_Poles(), stabilization_diagram()
│  ├─ ITD.py                # ITD_alg(), helpers for correlation & poles
│  ├─ PolyMAX.py            # PolyMAX(), independent_mode_shape(), stabilization_diagram(), ...
│  └─ ModeShape.py          # draw_mode_shapes(), draw_MAC_diagram(), structure‑specific plotters
├─ tests/
│  └─ test_basic.py
├─ README.md
├─ LICENSE
└─ AUTHORS.md
```

> **Tip:** Most core functions accept both `numpy` arrays and `pandas` DataFrames; when matrices are in sensor‑by‑time or time‑by‑sensor shape, some functions auto‑transpose to `[channels, samples]` internally.

---

## Citing

If this library helps your research, please cite the Modalyzer paper (details will be added once it is published). You can also star the repository to support the project.

A `CITATION.cff` will be added after publication.

---

## License

This project is licensed under the terms in `LICENSE` (e.g., BSD‑3‑Clause or MIT depending on your choice).

---

## Contributing

Pull requests and issues are welcome. If you plan significant changes, please open an issue to discuss the proposal first.

- Run tests with `pytest` (to be expanded).
- Follow PEP8/black where possible.
- Please include small reproducible examples when reporting bugs.

