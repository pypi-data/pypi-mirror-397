#!/usr/bin/env python
"""
Command Line Interface for manuk-kepudang 3D Vicsek Model Simulator.
"""

import argparse
import sys
from pathlib import Path

from .core.solver import VicsekSolver
from .core.systems import VicsekSystem
from .core.metrics import compute_metrics_timeseries
from .io.config_manager import ConfigManager
from .io.data_handler import DataHandler
from .visualization.animator import Animator
from .utils.logger import SimulationLogger
from .utils.timer import Timer


def print_header():
    """Print ASCII art header."""
    print("\n" + "=" * 70)
    print(" " * 12 + "manuk-kepudang: 3D Vicsek Model Simulator")
    print(" " * 25 + "Version 0.0.2")
    print("=" * 70)
    print("\n  Collective Motion and Flocking Behavior Simulation")
    print("  Self-Propelled Particles with Local Alignment")
    print("  License: MIT")
    print("=" * 70 + "\n")


def normalize_scenario_name(scenario_name: str) -> str:
    """Convert scenario name to clean filename format."""
    clean = scenario_name.lower()
    clean = clean.replace(' - ', '_')
    clean = clean.replace('-', '_')
    clean = clean.replace(' ', '_')
    
    while '__' in clean:
        clean = clean.replace('__', '_')
    
    if clean.startswith('case_'):
        parts = clean.split('_')
        if len(parts) >= 2 and parts[1].isdigit():
            case_num = parts[1]
            rest = '_'.join(parts[2:])
            clean = f"case{case_num}_{rest}"
    
    clean = clean.rstrip('_')
    return clean


def run_scenario(config: dict, output_dir: str = "outputs",
                verbose: bool = True):
    """Run a complete Vicsek simulation scenario."""
    scenario_name = config.get('scenario_name', 'simulation')
    clean_name = normalize_scenario_name(scenario_name)
    
    if verbose:
        print(f"\n{'=' * 70}")
        print(f"SCENARIO: {scenario_name}")
        print(f"{'=' * 70}")
    
    logger = SimulationLogger(clean_name, "logs", verbose)
    timer = Timer()
    timer.start("total")
    
    try:
        logger.log_parameters(config)
        
        # [1/8] Initialize system
        with timer.time_section("system_init"):
            if verbose:
                print("\n[1/8] Initializing Vicsek system...")
            
            system = VicsekSystem(
                n_particles=config.get('n_particles', 200),
                box_size=config.get('box_size', 10.0),
                speed=config.get('speed', 0.5),
                interaction_radius=config.get('interaction_radius', 2.0),
                noise=config.get('noise', 0.5),
                seed=config.get('seed', None)
            )
            
            if verbose:
                print(f"      N={system.n_particles}, L={system.box_size}, "
                      f"v0={system.speed}, r={system.interaction_radius}, η={system.noise}")
        
        # [2/8] Initialize solver
        with timer.time_section("solver_init"):
            if verbose:
                print("\n[2/8] Initializing solver...")
            
            solver = VicsekSolver(
                dt=config.get('dt', 1.0),
                use_numba=config.get('use_numba', True)
            )
            
            if verbose:
                print(f"      dt={solver.dt}, Numba={'enabled' if solver.use_numba else 'disabled'}")
        
        # [3/8] Run simulation
        with timer.time_section("simulation"):
            if verbose:
                print("\n[3/8] Running simulation...")
            
            result = solver.solve(
                system=system,
                n_steps=config.get('n_steps', 500),
                verbose=verbose
            )
            
            logger.log_results(result)
        
        # [4/8] Compute entropy metrics
        metrics = None
        if config.get('compute_entropy', True):
            with timer.time_section("metrics"):
                if verbose:
                    print("\n[4/8] Computing spatial entropy metrics...")
                
                metrics = compute_metrics_timeseries(
                    result['positions'],
                    result['velocities'],
                    result['time'],
                    system.box_size,
                    system.speed,
                    system.interaction_radius,
                    verbose=verbose
                )
                
                if verbose:
                    print(f"\n      Final Spatial Complexity Index: {metrics['spatial_complexity_index_final']:.4f}")
                    print(f"      Final Orientational Entropy: {metrics['orientational_entropy_final']:.4f}")
        else:
            if verbose:
                print("\n[4/8] Skipping entropy metrics (disabled in config)")
        
        # [5/8] Save CSV data
        if config.get('save_csv', True):
            with timer.time_section("csv_save"):
                if verbose:
                    print("\n[5/8] Saving CSV data...")
                
                csv_dir = Path(output_dir) / "csv"
                csv_dir.mkdir(parents=True, exist_ok=True)
                
                # Order parameter
                phi_file = csv_dir / f"{clean_name}_order_parameter.csv"
                DataHandler.save_order_parameter_csv(phi_file, result)
                if verbose:
                    print(f"      Saved: {phi_file}")
                
                # Final state trajectory
                traj_file = csv_dir / f"{clean_name}_final_state.csv"
                DataHandler.save_trajectory_csv(traj_file, result, step=-1)
                if verbose:
                    print(f"      Saved: {traj_file}")
                
                # Entropy metrics
                if metrics is not None:
                    entropy_file = csv_dir / f"{clean_name}_entropy_timeseries.csv"
                    DataHandler.save_entropy_metrics_csv(entropy_file, metrics)
                    if verbose:
                        print(f"      Saved: {entropy_file}")
                    
                    summary_file = csv_dir / f"{clean_name}_entropy_summary.csv"
                    DataHandler.save_entropy_summary_csv(summary_file, metrics)
                    if verbose:
                        print(f"      Saved: {summary_file}")
        
        # [6/8] Save NetCDF
        if config.get('save_netcdf', True):
            with timer.time_section("netcdf_save"):
                if verbose:
                    print("\n[6/8] Saving NetCDF data...")
                
                nc_dir = Path(output_dir) / "netcdf"
                nc_dir.mkdir(parents=True, exist_ok=True)
                
                nc_file = nc_dir / f"{clean_name}.nc"
                DataHandler.save_netcdf(nc_file, result, config, metrics)
                
                if verbose:
                    print(f"      Saved: {nc_file}")
        
        # [7/8] Generate visualizations
        with timer.time_section("visualization"):
            if verbose:
                print("\n[7/8] Generating visualizations...")
            
            animator = Animator(
                fps=config.get('animation_fps', 30),
                dpi=config.get('animation_dpi', 150)
            )
            
            if config.get('save_png', True):
                with timer.time_section("png_save"):
                    if verbose:
                        print("      Creating static plots...")
                    
                    fig_dir = Path(output_dir) / "figs"
                    fig_dir.mkdir(parents=True, exist_ok=True)
                    
                    png_file = fig_dir / f"{clean_name}_summary.png"
                    animator.create_static_plot(result, png_file, scenario_name, metrics)
                    
                    if verbose:
                        print(f"      Saved: {png_file}")
            
            if config.get('save_gif', True):
                with timer.time_section("gif_save"):
                    if verbose:
                        print("      Creating animation...")
                    
                    gif_dir = Path(output_dir) / "gifs"
                    gif_dir.mkdir(parents=True, exist_ok=True)
                    
                    gif_file = gif_dir / f"{clean_name}_animation.gif"
                    skip = config.get('animation_skip', 5)
                    duration = config.get('animation_duration', 15.0)
                    animator.create_animation(result, gif_file, scenario_name,
                                            skip=skip, duration_seconds=duration)
                    
                    if verbose:
                        print(f"      Saved: {gif_file}")
        
        timer.stop("total")
        logger.log_timing(timer.get_times())
        
        # [8/8] Summary
        sim_time = timer.times.get('simulation', 0)
        metrics_time = timer.times.get('metrics', 0)
        total_time = timer.times.get('total', 0)
        
        if verbose:
            print(f"\n[8/8] SIMULATION COMPLETED")
            print(f"{'=' * 70}")
            print(f"  Final order parameter: {result['final_order_parameter']:.4f}")
            print(f"  Mean order parameter: {result['mean_order_parameter']:.4f}")
            if metrics is not None:
                print(f"  Final SCI (disorder): {metrics['spatial_complexity_index_final']:.4f}")
            print(f"  Simulation time: {sim_time:.2f} s")
            if metrics_time > 0:
                print(f"  Metrics computation: {metrics_time:.2f} s")
            print(f"  Total time: {total_time:.2f} s")
            
            if logger.warnings:
                print(f"  Warnings: {len(logger.warnings)}")
            if logger.errors:
                print(f"  Errors: {len(logger.errors)}")
            
            print(f"{'=' * 70}\n")
    
    except Exception as e:
        logger.error(f"Simulation failed: {str(e)}")
        
        if verbose:
            print(f"\n{'=' * 70}")
            print(f"SIMULATION FAILED")
            print(f"  Error: {str(e)}")
            print(f"{'=' * 70}\n")
        
        raise
    
    finally:
        logger.finalize()


def main():
    """Main entry point for command-line interface."""
    parser = argparse.ArgumentParser(
        description='manuk-kepudang: 3D Vicsek Model Simulator',
        epilog='Example: manuk-kepudang case1'
    )
    
    parser.add_argument(
        'case',
        nargs='?',
        choices=['case1', 'case2', 'case3', 'case4'],
        help='Test case to run (case1-4)'
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        help='Path to custom configuration file'
    )
    
    parser.add_argument(
        '--all', '-a',
        action='store_true',
        help='Run all test cases sequentially'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        type=str,
        default='outputs',
        help='Output directory for results (default: outputs)'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Quiet mode (minimal output)'
    )
    
    parser.add_argument(
        '--no-entropy',
        action='store_true',
        help='Skip entropy/complexity metric computation'
    )
    
    args = parser.parse_args()
    verbose = not args.quiet
    
    if verbose:
        print_header()
    
    # Custom config
    if args.config:
        config = ConfigManager.load(args.config)
        if args.no_entropy:
            config['compute_entropy'] = False
        run_scenario(config, args.output_dir, verbose)
    
    # All cases
    elif args.all:
        configs_dir = Path(__file__).parent.parent.parent / 'configs'
        config_files = sorted(configs_dir.glob('case*.txt'))
        
        if not config_files:
            print("ERROR: No configuration files found in configs/")
            sys.exit(1)
        
        for i, cfg_file in enumerate(config_files, 1):
            if verbose:
                print(f"\n[Case {i}/{len(config_files)}] Running {cfg_file.stem}...")
            
            config = ConfigManager.load(str(cfg_file))
            if args.no_entropy:
                config['compute_entropy'] = False
            run_scenario(config, args.output_dir, verbose)
    
    # Single case
    elif args.case:
        case_map = {
            'case1': 'case1_ordered_phase',
            'case2': 'case2_disordered_phase',
            'case3': 'case3_large_system',
            'case4': 'case4_phase_transition'
        }
        
        cfg_name = case_map[args.case]
        configs_dir = Path(__file__).parent.parent.parent / 'configs'
        cfg_file = configs_dir / f'{cfg_name}.txt'
        
        if cfg_file.exists():
            config = ConfigManager.load(str(cfg_file))
            if args.no_entropy:
                config['compute_entropy'] = False
            run_scenario(config, args.output_dir, verbose)
        else:
            print(f"ERROR: Configuration file not found: {cfg_file}")
            sys.exit(1)
    
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == '__main__':
    main()
