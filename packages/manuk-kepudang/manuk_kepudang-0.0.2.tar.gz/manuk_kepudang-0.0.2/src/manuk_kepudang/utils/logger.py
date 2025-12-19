"""Comprehensive simulation logger for Vicsek model simulations."""

import logging
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


class SimulationLogger:
    """Logger for Vicsek simulations with detailed diagnostics."""
    
    def __init__(self, scenario_name: str, log_dir: str = "logs",
                 verbose: bool = True):
        """
        Initialize simulation logger.
        
        Args:
            scenario_name: Scenario name (for log filename)
            log_dir: Directory for log files
            verbose: Print messages to console
        """
        self.scenario_name = scenario_name
        self.log_dir = Path(log_dir)
        self.verbose = verbose
        
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / f"{scenario_name}.log"
        
        self.logger = self._setup_logger()
        self.warnings = []
        self.errors = []
    
    def _setup_logger(self):
        """Configure Python logging."""
        logger = logging.getLogger(f"manuk_kepudang_{self.scenario_name}")
        logger.setLevel(logging.DEBUG)
        logger.handlers = []
        
        handler = logging.FileHandler(self.log_file, mode='w')
        handler.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        return logger
    
    def info(self, msg: str):
        """Log informational message."""
        self.logger.info(msg)
    
    def warning(self, msg: str):
        """Log warning message."""
        self.logger.warning(msg)
        self.warnings.append(msg)
        
        if self.verbose:
            print(f"  WARNING: {msg}")
    
    def error(self, msg: str):
        """Log error message."""
        self.logger.error(msg)
        self.errors.append(msg)
        
        if self.verbose:
            print(f"  ERROR: {msg}")
    
    def log_parameters(self, params: Dict[str, Any]):
        """Log all simulation parameters."""
        self.info("=" * 70)
        self.info("3D VICSEK MODEL SIMULATION")
        self.info(f"Scenario: {params.get('scenario_name', 'Unknown')}")
        self.info("=" * 70)
        self.info("")
        
        self.info("SYSTEM PARAMETERS:")
        self.info(f"  N (particles): {params.get('n_particles', 200)}")
        self.info(f"  L (box size): {params.get('box_size', 10.0)}")
        self.info(f"  v0 (speed): {params.get('speed', 0.5)}")
        self.info(f"  r (interaction radius): {params.get('interaction_radius', 2.0)}")
        self.info(f"  eta (noise): {params.get('noise', 0.5)}")
        
        density = params.get('n_particles', 200) / (params.get('box_size', 10.0) ** 3)
        self.info(f"  rho (density): {density:.4f}")
        
        self.info("")
        self.info("SIMULATION PARAMETERS:")
        self.info(f"  dt (time step): {params.get('dt', 1.0)}")
        self.info(f"  n_steps: {params.get('n_steps', 500)}")
        self.info(f"  seed: {params.get('seed', 'None')}")
        self.info(f"  use_numba: {params.get('use_numba', True)}")
        self.info(f"  compute_entropy: {params.get('compute_entropy', True)}")
        
        self.info("")
        self.info("OUTPUT OPTIONS:")
        self.info(f"  Save CSV: {params.get('save_csv', True)}")
        self.info(f"  Save NetCDF: {params.get('save_netcdf', True)}")
        self.info(f"  Save PNG: {params.get('save_png', True)}")
        self.info(f"  Save GIF: {params.get('save_gif', True)}")
        self.info(f"  Output directory: {params.get('output_dir', 'outputs')}")
        
        self.info("=" * 70)
        self.info("")
    
    def log_timing(self, timing: Dict[str, float]):
        """Log timing breakdown."""
        self.info("=" * 70)
        self.info("TIMING BREAKDOWN:")
        self.info("=" * 70)
        
        sections = [
            ('system_init', 'System initialization'),
            ('solver_init', 'Solver initialization'),
            ('simulation', 'Main simulation'),
            ('metrics', 'Entropy metrics computation'),
            ('csv_save', 'CSV file saving'),
            ('netcdf_save', 'NetCDF file saving'),
            ('png_save', 'Static plot generation'),
            ('gif_save', 'Animation generation'),
            ('visualization', 'Total visualization')
        ]
        
        for key, desc in sections:
            if key in timing:
                self.info(f"  {desc}: {timing[key]:.3f} s")
        
        for key, value in sorted(timing.items()):
            if key not in [s[0] for s in sections] and key != 'total':
                self.info(f"  {key}: {value:.3f} s")
        
        self.info(f"  {'-' * 40}")
        total_time = timing.get('total', sum(timing.values()))
        self.info(f"  TOTAL: {total_time:.3f} s")
        
        self.info("=" * 70)
        self.info("")
    
    def log_results(self, results: Dict[str, Any]):
        """Log simulation results."""
        self.info("=" * 70)
        self.info("SIMULATION RESULTS:")
        self.info("=" * 70)
        self.info("")
        
        system = results['system']
        self.info(f"SYSTEM: {system}")
        
        self.info("")
        self.info("ORDER PARAMETER STATISTICS:")
        self.info(f"  Initial: {results['order_parameter'][0]:.6f}")
        self.info(f"  Final: {results['final_order_parameter']:.6f}")
        self.info(f"  Mean (2nd half): {results['mean_order_parameter']:.6f}")
        self.info(f"  Std (2nd half): {results['std_order_parameter']:.6f}")
        self.info(f"  Maximum: {results['max_order_parameter']:.6f}")
        self.info(f"  Minimum: {results['min_order_parameter']:.6f}")
        
        self.info("")
        self.info("SIMULATION SUMMARY:")
        self.info(f"  Time points saved: {len(results['time'])}")
        self.info(f"  Total simulation time: {results['time'][-1]:.2f}")
        
        self.info("=" * 70)
        self.info("")
    
    def finalize(self):
        """Write final summary."""
        self.info("=" * 70)
        self.info("SIMULATION SUMMARY:")
        self.info("=" * 70)
        self.info("")
        
        if self.errors:
            self.info(f"ERRORS: {len(self.errors)}")
            for i, err in enumerate(self.errors, 1):
                self.info(f"  {i}. {err}")
        else:
            self.info("ERRORS: None")
        
        self.info("")
        
        if self.warnings:
            self.info(f"WARNINGS: {len(self.warnings)}")
            for i, warn in enumerate(self.warnings, 1):
                self.info(f"  {i}. {warn}")
        else:
            self.info("WARNINGS: None")
        
        self.info("")
        self.info(f"Log file: {self.log_file}")
        self.info("=" * 70)
        self.info(f"Simulation completed: {self.scenario_name}")
        self.info(f"Timestamp: {datetime.now().isoformat()}")
        self.info("=" * 70)
