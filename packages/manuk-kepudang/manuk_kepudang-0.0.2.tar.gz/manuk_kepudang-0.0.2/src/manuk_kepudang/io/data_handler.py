"""Data handler for saving simulation results to CSV and NetCDF."""

import numpy as np
import pandas as pd
from netCDF4 import Dataset
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


class DataHandler:
    """Handle saving simulation data to various formats."""
    
    @staticmethod
    def save_order_parameter_csv(filepath: str, result: Dict[str, Any]):
        """
        Save order parameter time series to CSV.
        
        Args:
            filepath: Output file path
            result: Simulation result dictionary
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        df = pd.DataFrame({
            'Time': result['time'],
            'Order_Parameter': result['order_parameter']
        })
        
        df.to_csv(filepath, index=False, float_format='%.8e')
    
    @staticmethod
    def save_entropy_metrics_csv(filepath: str, metrics: Dict[str, Any]):
        """
        Save entropy/complexity metrics time series to CSV.
        
        Args:
            filepath: Output file path
            metrics: Metrics dictionary from compute_metrics_timeseries
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Build DataFrame from time series
        columns = {
            'Time': metrics['time'],
            'Order_Parameter': metrics['order_parameter'],
            'Positional_Entropy': metrics['positional_entropy'],
            'Orientational_Entropy': metrics['orientational_entropy'],
            'Local_Alignment_Entropy': metrics['local_alignment_entropy'],
            'Pair_Correlation_Entropy': metrics['pair_correlation_entropy'],
            'Voronoi_Entropy': metrics['voronoi_entropy'],
            'Position_Velocity_MI': metrics['position_velocity_mutual_info'],
            'Local_Alignment_Mean': metrics['local_alignment_mean'],
            'Local_Alignment_Std': metrics['local_alignment_std'],
            'Spatial_Complexity_Index': metrics['spatial_complexity_index']
        }
        
        df = pd.DataFrame(columns)
        df.to_csv(filepath, index=False, float_format='%.8e')
    
    @staticmethod
    def save_entropy_summary_csv(filepath: str, metrics: Dict[str, Any]):
        """
        Save summary statistics of entropy metrics to CSV.
        
        Args:
            filepath: Output file path
            metrics: Metrics dictionary from compute_metrics_timeseries
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Extract summary statistics
        metric_names = [
            'order_parameter',
            'positional_entropy',
            'orientational_entropy',
            'local_alignment_entropy',
            'pair_correlation_entropy',
            'voronoi_entropy',
            'position_velocity_mutual_info',
            'local_alignment_mean',
            'local_alignment_std',
            'spatial_complexity_index'
        ]
        
        rows = []
        for name in metric_names:
            rows.append({
                'Metric': name,
                'Mean_2nd_Half': metrics.get(f'{name}_mean', np.nan),
                'Std_2nd_Half': metrics.get(f'{name}_std', np.nan),
                'Final_Value': metrics.get(f'{name}_final', np.nan),
                'Min': np.min(metrics.get(name, [np.nan])),
                'Max': np.max(metrics.get(name, [np.nan]))
            })
        
        df = pd.DataFrame(rows)
        df.to_csv(filepath, index=False, float_format='%.8e')
    
    @staticmethod
    def save_trajectory_csv(filepath: str, result: Dict[str, Any], step: int = -1):
        """
        Save particle positions and velocities at a given step.
        
        Args:
            filepath: Output file path
            result: Simulation result dictionary
            step: Time step index (-1 for final)
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        pos = result['positions'][step]
        vel = result['velocities'][step]
        
        df = pd.DataFrame({
            'Particle_ID': np.arange(pos.shape[0]),
            'x': pos[:, 0],
            'y': pos[:, 1],
            'z': pos[:, 2],
            'vx': vel[:, 0],
            'vy': vel[:, 1],
            'vz': vel[:, 2]
        })
        
        df.to_csv(filepath, index=False, float_format='%.8e')
    
    @staticmethod
    def save_netcdf(
        filepath: str,
        result: Dict[str, Any],
        config: Dict[str, Any],
        metrics: Dict[str, Any] = None
    ):
        """
        Save complete simulation data to NetCDF format.
        
        Args:
            filepath: Output file path
            result: Simulation result dictionary
            config: Configuration dictionary
            metrics: Optional metrics dictionary from compute_metrics_timeseries
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with Dataset(filepath, 'w', format='NETCDF4') as nc:
            # Dimensions
            n_time = len(result['time'])
            n_particles = result['positions'].shape[1]
            
            nc.createDimension('time', n_time)
            nc.createDimension('particle', n_particles)
            nc.createDimension('spatial', 3)
            
            # Time coordinate
            nc_time = nc.createVariable('time', 'f8', ('time',), zlib=True)
            nc_time[:] = result['time']
            nc_time.units = "simulation_time_units"
            nc_time.long_name = "simulation_time"
            nc_time.axis = "T"
            
            # Particle coordinate
            nc_particle = nc.createVariable('particle', 'i4', ('particle',), zlib=True)
            nc_particle[:] = np.arange(n_particles)
            nc_particle.long_name = "particle_index"
            nc_particle.units = "1"
            
            # Spatial coordinate (x=0, y=1, z=2)
            nc_spatial = nc.createVariable('spatial', 'i4', ('spatial',), zlib=True)
            nc_spatial[:] = np.array([0, 1, 2])
            nc_spatial.long_name = "spatial_dimension"
            nc_spatial.comment = "0=x, 1=y, 2=z"
            
            # Order parameter
            nc_phi = nc.createVariable('order_parameter', 'f8', ('time',), zlib=True)
            nc_phi[:] = result['order_parameter']
            nc_phi.units = "dimensionless"
            nc_phi.long_name = "collective_alignment_order_parameter"
            nc_phi.valid_range = [0.0, 1.0]
            
            # Positions (full 3D array)
            nc_pos = nc.createVariable('positions', 'f8', ('time', 'particle', 'spatial'), zlib=True)
            nc_pos[:] = result['positions']
            nc_pos.units = "simulation_length_units"
            nc_pos.long_name = "particle_positions"
            nc_pos.coordinates = "time particle spatial"
            
            # Velocities (full 3D array)
            nc_vel = nc.createVariable('velocities', 'f8', ('time', 'particle', 'spatial'), zlib=True)
            nc_vel[:] = result['velocities']
            nc_vel.units = "simulation_velocity_units"
            nc_vel.long_name = "particle_velocities"
            nc_vel.coordinates = "time particle spatial"
            
            # Individual position components for convenience
            nc_x = nc.createVariable('x', 'f8', ('time', 'particle'), zlib=True)
            nc_x[:] = result['positions'][:, :, 0]
            nc_x.units = "simulation_length_units"
            nc_x.long_name = "particle_x_position"
            nc_x.axis = "X"
            
            nc_y = nc.createVariable('y', 'f8', ('time', 'particle'), zlib=True)
            nc_y[:] = result['positions'][:, :, 1]
            nc_y.units = "simulation_length_units"
            nc_y.long_name = "particle_y_position"
            nc_y.axis = "Y"
            
            nc_z = nc.createVariable('z', 'f8', ('time', 'particle'), zlib=True)
            nc_z[:] = result['positions'][:, :, 2]
            nc_z.units = "simulation_length_units"
            nc_z.long_name = "particle_z_position"
            nc_z.axis = "Z"
            
            # Individual velocity components for convenience
            nc_vx = nc.createVariable('vx', 'f8', ('time', 'particle'), zlib=True)
            nc_vx[:] = result['velocities'][:, :, 0]
            nc_vx.units = "simulation_velocity_units"
            nc_vx.long_name = "particle_x_velocity"
            
            nc_vy = nc.createVariable('vy', 'f8', ('time', 'particle'), zlib=True)
            nc_vy[:] = result['velocities'][:, :, 1]
            nc_vy.units = "simulation_velocity_units"
            nc_vy.long_name = "particle_y_velocity"
            
            nc_vz = nc.createVariable('vz', 'f8', ('time', 'particle'), zlib=True)
            nc_vz[:] = result['velocities'][:, :, 2]
            nc_vz.units = "simulation_velocity_units"
            nc_vz.long_name = "particle_z_velocity"
            
            # Add entropy metrics if provided
            if metrics is not None:
                # Positional entropy
                nc_var = nc.createVariable('positional_entropy', 'f8', ('time',), zlib=True)
                nc_var[:] = metrics['positional_entropy']
                nc_var.units = "dimensionless"
                nc_var.long_name = "shannon_entropy_of_spatial_distribution"
                nc_var.valid_range = [0.0, 1.0]
                nc_var.description = "High=uniform/disordered, Low=clustered/ordered"
                
                # Orientational entropy
                nc_var = nc.createVariable('orientational_entropy', 'f8', ('time',), zlib=True)
                nc_var[:] = metrics['orientational_entropy']
                nc_var.units = "dimensionless"
                nc_var.long_name = "shannon_entropy_of_velocity_orientations"
                nc_var.valid_range = [0.0, 1.0]
                nc_var.description = "High=isotropic/disordered, Low=aligned/ordered"
                
                # Local alignment entropy
                nc_var = nc.createVariable('local_alignment_entropy', 'f8', ('time',), zlib=True)
                nc_var[:] = metrics['local_alignment_entropy']
                nc_var.units = "dimensionless"
                nc_var.long_name = "entropy_of_local_order_parameter_distribution"
                nc_var.valid_range = [0.0, 1.0]
                nc_var.description = "High=heterogeneous local order, Low=homogeneous"
                
                # Pair correlation entropy
                nc_var = nc.createVariable('pair_correlation_entropy', 'f8', ('time',), zlib=True)
                nc_var[:] = metrics['pair_correlation_entropy']
                nc_var.units = "dimensionless"
                nc_var.long_name = "entropy_from_radial_distribution_function"
                nc_var.valid_range = [0.0, 1.0]
                nc_var.description = "High=ideal_gas/disordered, Low=crystalline/ordered"
                
                # Voronoi entropy
                nc_var = nc.createVariable('voronoi_entropy', 'f8', ('time',), zlib=True)
                nc_var[:] = metrics['voronoi_entropy']
                nc_var.units = "dimensionless"
                nc_var.long_name = "entropy_of_voronoi_cell_volumes"
                nc_var.valid_range = [0.0, 1.0]
                nc_var.description = "High=disordered packing, Low=regular packing"
                
                # Mutual information
                nc_var = nc.createVariable('position_velocity_mutual_info', 'f8', ('time',), zlib=True)
                nc_var[:] = metrics['position_velocity_mutual_info']
                nc_var.units = "dimensionless"
                nc_var.long_name = "mutual_information_position_velocity"
                nc_var.valid_range = [0.0, 1.0]
                nc_var.description = "High=spatial structure in velocity field, Low=homogeneous"
                
                # Local alignment mean
                nc_var = nc.createVariable('local_alignment_mean', 'f8', ('time',), zlib=True)
                nc_var[:] = metrics['local_alignment_mean']
                nc_var.units = "dimensionless"
                nc_var.long_name = "mean_local_order_parameter"
                nc_var.valid_range = [0.0, 1.0]
                
                # Local alignment std
                nc_var = nc.createVariable('local_alignment_std', 'f8', ('time',), zlib=True)
                nc_var[:] = metrics['local_alignment_std']
                nc_var.units = "dimensionless"
                nc_var.long_name = "std_local_order_parameter"
                
                # Spatial complexity index
                nc_var = nc.createVariable('spatial_complexity_index', 'f8', ('time',), zlib=True)
                nc_var[:] = metrics['spatial_complexity_index']
                nc_var.units = "dimensionless"
                nc_var.long_name = "composite_spatial_complexity_index"
                nc_var.valid_range = [0.0, 1.0]
                nc_var.description = "Weighted average of entropy measures. High=disordered, Low=ordered"
            
            # Global attributes
            system = result['system']
            nc.title = "3D Vicsek Model Simulation"
            nc.scenario_name = config.get('scenario_name', 'unknown')
            nc.institution = "manuk-kepudang"
            nc.source = "manuk-kepudang v0.0.1"
            nc.history = f"Created {datetime.now().isoformat()}"
            nc.Conventions = "CF-1.8"
            
            # System parameters
            nc.n_particles = int(system.n_particles)
            nc.box_size = float(system.box_size)
            nc.speed = float(system.speed)
            nc.interaction_radius = float(system.interaction_radius)
            nc.noise = float(system.noise)
            
            # Simulation parameters
            nc.n_steps = int(result['n_steps'])
            nc.dt = float(result['dt'])
            nc.save_interval = int(result['save_interval'])
            
            # Summary statistics - order parameter
            nc.final_order_parameter = float(result['final_order_parameter'])
            nc.mean_order_parameter = float(result['mean_order_parameter'])
            nc.std_order_parameter = float(result['std_order_parameter'])
            nc.max_order_parameter = float(result['max_order_parameter'])
            nc.min_order_parameter = float(result['min_order_parameter'])
            
            # Summary statistics - entropy metrics
            if metrics is not None:
                nc.final_positional_entropy = float(metrics['positional_entropy_final'])
                nc.mean_positional_entropy = float(metrics['positional_entropy_mean'])
                nc.final_orientational_entropy = float(metrics['orientational_entropy_final'])
                nc.mean_orientational_entropy = float(metrics['orientational_entropy_mean'])
                nc.final_spatial_complexity_index = float(metrics['spatial_complexity_index_final'])
                nc.mean_spatial_complexity_index = float(metrics['spatial_complexity_index_mean'])
            
            # References
            nc.author = "Sandy H. S. Herho, Gandhi Napitupulu, Iwan P. Anwar, Nurjanna J. Trilaksono, Rusmawan Suwarman, Dasapta E. Irawan"
            nc.email = "sandy.herho@email.ucr.edu"
            nc.license = "MIT"
