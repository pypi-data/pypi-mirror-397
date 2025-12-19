"""
Modalyzer: Operational Modal Analysis (OMA) toolkit.
Top-level exports for a friendly API.
"""

__version__ = "0.1.2"  # update when you publish a new build

from . import Preprocess, SSI, PolyMAX, ITD, EFDD, ModeShape

# Re-export submodules so they appear in dir(modalyzer)
from . import Preprocess, SSI, PolyMAX, ITD, EFDD, ModeShape

from .Preprocess import preprocess, choose_modes, results_table
from .EFDD import FDD_SVD_Diagram, FDD_ModeShape, FDD_Damping
from .SSI import SSI_Alg, stabilization_diagram
from .PolyMAX import PolyMAX, psd_func, svd_psd
from .ITD import ITD_alg
from .ModeShape import draw_mode_shapes, draw_MAC_diagram


__all__ = [
    "Preprocess", "SSI", "PolyMAX", "ITD", "EFDD", "ModeShape",
    "preprocess", "choose_modes", "results_table",
    "SSI_Alg", "psd_func", "svd_psd", "stabilization_diagram", "PolyMAX", "ITD_alg",
    "FDD_SVD_Diagram", "FDD_ModeShape", "FDD_Damping",
    "draw_mode_shapes", "draw_MAC_diagram",
]

