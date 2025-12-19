# Modalyzer

Open-source Python library for Operational Modal Analysis (OMA) and system identification.

Modalyzer provides multiple algorithms — EFDD/FDD, SSI (cov/data), ITD, and PolyMAX (p-LSCF) — along with tools for preprocessing, stabilization diagrams, and mode-shape visualization for common structures.

> **Status:** Actively developed research software. APIs may evolve as the project matures.

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

Modalyzer is available on PyPI.

```bash
pip install modalyzer
```

CPU-only PyTorch (recommended)

Modalyzer is CPU-only. To avoid CUDA downloads on Linux, install PyTorch explicitly from the CPU index before installing Modalyzer:
```bash
pip install --index-url https://download.pytorch.org/whl/cpu torch
pip install modalyzer
```

### Dependencies
The modules use: `numpy`, `pandas`, `matplotlib`, `scipy`, `torch`, `plotly`, and `nbformat`. They will be install alongside modalyzer.
Also you can install them manually (not recommended):
```bash
pip install numpy pandas matplotlib scipy torch plotly nbformat
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
├─ Examples/
│  └─ ...
├─ tests/
│  └─ test_basic.py
├─ README.md
├─ LICENSE
└─ AUTHORS.md
```

> **Tip:** Most core functions accept both `numpy` arrays and `pandas` DataFrames; when matrices are in sensor‑by‑time or time‑by‑sensor shape, some functions auto‑transpose to `[channels, samples]` internally.

---

## YouTube Tutorial Playlist

A tutorial playlist is provided demonstrating how to use Modalyzer with your own datasets.

https://www.youtube.com/watch?v=fZnCtZ2--gM&list=PLLPCQlWev9z_SivHPs4FIOE7zmSMDCrVj

---

## Citing

If you use Modalyzer in academic work, citation is appreciated.

Shamsaddinlou, A., Nikoofaraz, M., De Domenico, D., & Longo, M.
Computationally Efficient Python-based Operational Modal Analysis of Structures: Modalyzer.
Journal of Vibration and Control. https://doi.org/10.1177/10775463251410790

---

## License

This project is released under the MIT License.
See the LICENSE file for details.

---

## Contributing

Pull requests and issues are welcome. If you plan significant changes, please open an issue to discuss the proposal first.

- Please use example Jupyter notebooks in Examples folder for test. Data is provided.
- Open an issue for bug reports or feature requests
- Please include small reproducible examples when reporting bugs.

