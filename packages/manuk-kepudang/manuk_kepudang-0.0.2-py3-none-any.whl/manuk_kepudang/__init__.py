"""manuk-kepudang: 3D Vicsek Model Collective Motion Simulator"""

__version__ = "0.0.2"
__author__ = "Sandy H. S. Herho, Gandhi Napitupulu, Iwan P. Anwar, Nurjanna J. Trilaksono, Rusmawan Suwarman, Dasapta E. Irawan"
__email__ = "sandy.herho@email.ucr.edu"
__license__ = "MIT"

from .core.solver import VicsekSolver
from .core.systems import VicsekSystem
from .core.metrics import (
    compute_positional_entropy,
    compute_orientational_entropy,
    compute_local_alignment_entropy,
    compute_pair_correlation_entropy,
    compute_voronoi_entropy,
    compute_velocity_position_mutual_information,
    compute_spatial_complexity_index,
    compute_all_metrics,
    compute_metrics_timeseries
)
from .io.config_manager import ConfigManager
from .io.data_handler import DataHandler

__all__ = [
    "VicsekSolver",
    "VicsekSystem",
    "ConfigManager",
    "DataHandler",
    "compute_positional_entropy",
    "compute_orientational_entropy",
    "compute_local_alignment_entropy",
    "compute_pair_correlation_entropy",
    "compute_voronoi_entropy",
    "compute_velocity_position_mutual_information",
    "compute_spatial_complexity_index",
    "compute_all_metrics",
    "compute_metrics_timeseries"
]
