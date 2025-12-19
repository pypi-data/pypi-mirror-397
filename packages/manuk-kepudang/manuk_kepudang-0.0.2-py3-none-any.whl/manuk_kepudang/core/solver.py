"""
3D Vicsek Model Solver with Numba Acceleration.

Implements the Vicsek alignment dynamics with optional JIT compilation
for high-performance simulation of collective motion.

References:
    Vicsek, T., et al. (1995). Novel type of phase transition in a system
    of self-driven particles. Physical Review Letters, 75(6), 1226.
"""

import numpy as np
from typing import Dict, Any, Optional
from tqdm import tqdm

from .systems import VicsekSystem

# Try to import numba, fall back to pure numpy if unavailable
try:
    from numba import jit, prange
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False
    def jit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    prange = range


@jit(nopython=True, parallel=True, cache=True)
def _update_velocities_numba(
    positions: np.ndarray,
    velocities: np.ndarray,
    box_size: float,
    radius: float,
    noise: float,
    speed: float
) -> np.ndarray:
    """
    Numba-accelerated velocity update with alignment dynamics.
    
    Implements the standard Vicsek model where:
    1. Compute average velocity direction of neighbors (normalized)
    2. Add angular noise proportional to eta
    3. Normalize to constant speed
    
    The noise parameter eta represents angular noise magnitude.
    At eta=0, particles align perfectly. At high eta, motion becomes random.
    
    Args:
        positions: (N, 3) particle positions
        velocities: (N, 3) particle velocities
        box_size: Simulation box size
        radius: Interaction radius
        noise: Noise magnitude (eta) - angular noise scale
        speed: Constant particle speed
    
    Returns:
        (N, 3) updated velocity array
    """
    n = positions.shape[0]
    new_vel = np.zeros((n, 3), dtype=np.float64)
    
    for i in prange(n):
        # Sum velocities of neighbors
        sum_vx = 0.0
        sum_vy = 0.0
        sum_vz = 0.0
        n_neighbors = 0
        
        for j in range(n):
            # Compute distance with PBC
            dx = positions[i, 0] - positions[j, 0]
            dy = positions[i, 1] - positions[j, 1]
            dz = positions[i, 2] - positions[j, 2]
            
            # Minimum image convention
            dx = dx - box_size * round(dx / box_size)
            dy = dy - box_size * round(dy / box_size)
            dz = dz - box_size * round(dz / box_size)
            
            dist = np.sqrt(dx*dx + dy*dy + dz*dz)
            
            if dist < radius:
                sum_vx += velocities[j, 0]
                sum_vy += velocities[j, 1]
                sum_vz += velocities[j, 2]
                n_neighbors += 1
        
        # CRITICAL FIX: Normalize the average velocity to unit vector
        # This ensures noise magnitude is relative to alignment, not neighbor count
        avg_norm = np.sqrt(sum_vx*sum_vx + sum_vy*sum_vy + sum_vz*sum_vz)
        if avg_norm > 1e-10:
            avg_vx = sum_vx / avg_norm
            avg_vy = sum_vy / avg_norm
            avg_vz = sum_vz / avg_norm
        else:
            # If no net direction, use random direction
            avg_vx = np.random.randn()
            avg_vy = np.random.randn()
            avg_vz = np.random.randn()
            norm_tmp = np.sqrt(avg_vx*avg_vx + avg_vy*avg_vy + avg_vz*avg_vz)
            if norm_tmp > 1e-10:
                avg_vx /= norm_tmp
                avg_vy /= norm_tmp
                avg_vz /= norm_tmp
        
        # Generate random unit vector for noise direction
        noise_x = np.random.randn()
        noise_y = np.random.randn()
        noise_z = np.random.randn()
        noise_norm = np.sqrt(noise_x*noise_x + noise_y*noise_y + noise_z*noise_z)
        if noise_norm > 1e-10:
            noise_x /= noise_norm
            noise_y /= noise_norm
            noise_z /= noise_norm
        
        # Add noise: new_direction = avg_direction + eta * noise_direction
        # At eta=0: perfect alignment with neighbors
        # At eta~1: comparable noise to alignment signal
        # At eta>>1: noise dominates, random motion
        new_vx = avg_vx + noise * noise_x
        new_vy = avg_vy + noise * noise_y
        new_vz = avg_vz + noise * noise_z
        
        # Normalize to constant speed
        norm = np.sqrt(new_vx*new_vx + new_vy*new_vy + new_vz*new_vz)
        if norm > 1e-10:
            new_vel[i, 0] = (new_vx / norm) * speed
            new_vel[i, 1] = (new_vy / norm) * speed
            new_vel[i, 2] = (new_vz / norm) * speed
        else:
            # Random direction if velocities cancel (rare at high noise)
            rx = np.random.randn()
            ry = np.random.randn()
            rz = np.random.randn()
            rnorm = np.sqrt(rx*rx + ry*ry + rz*rz)
            if rnorm > 1e-10:
                new_vel[i, 0] = (rx / rnorm) * speed
                new_vel[i, 1] = (ry / rnorm) * speed
                new_vel[i, 2] = (rz / rnorm) * speed
    
    return new_vel


def _update_velocities_numpy(
    positions: np.ndarray,
    velocities: np.ndarray,
    box_size: float,
    radius: float,
    noise: float,
    speed: float
) -> np.ndarray:
    """
    NumPy-based velocity update (fallback when Numba unavailable).
    
    Args:
        positions: (N, 3) particle positions
        velocities: (N, 3) particle velocities
        box_size: Simulation box size
        radius: Interaction radius
        noise: Noise magnitude (eta)
        speed: Constant particle speed
    
    Returns:
        (N, 3) updated velocity array
    """
    n = positions.shape[0]
    
    # Compute pairwise distances with PBC
    delta = positions[:, np.newaxis, :] - positions[np.newaxis, :, :]
    delta = delta - box_size * np.round(delta / box_size)
    dists = np.linalg.norm(delta, axis=2)
    
    # Find neighbors (including self)
    adjacency = (dists < radius).astype(float)
    
    # Average neighbor velocities
    sum_vel = adjacency @ velocities
    
    # CRITICAL FIX: Normalize to unit vector before adding noise
    norms = np.linalg.norm(sum_vel, axis=1, keepdims=True)
    norms[norms < 1e-10] = 1.0
    avg_vel = sum_vel / norms
    
    # Add noise (unit random vectors scaled by eta)
    noise_vec = np.random.randn(n, 3)
    noise_norms = np.linalg.norm(noise_vec, axis=1, keepdims=True)
    noise_norms[noise_norms < 1e-10] = 1.0
    noise_vec = noise_vec / noise_norms
    
    new_vel = avg_vel + noise * noise_vec
    
    # Normalize to constant speed
    final_norms = np.linalg.norm(new_vel, axis=1, keepdims=True)
    final_norms[final_norms < 1e-10] = 1.0
    new_vel = (new_vel / final_norms) * speed
    
    return new_vel


class VicsekSolver:
    """
    Solver for the 3D Vicsek Model.
    
    Simulates collective motion of self-propelled particles with
    local alignment interactions and noise.
    """
    
    def __init__(self, dt: float = 1.0, use_numba: bool = True):
        """
        Initialize solver.
        
        Args:
            dt: Time step
            use_numba: Use Numba JIT acceleration if available
        """
        self.dt = dt
        self.use_numba = use_numba and NUMBA_AVAILABLE
        
        if use_numba and not NUMBA_AVAILABLE:
            import warnings
            warnings.warn(
                "Numba not available, falling back to NumPy implementation. "
                "Install numba for 10-100x speedup: pip install numba"
            )
    
    def solve(
        self,
        system: VicsekSystem,
        n_steps: int = 500,
        save_interval: int = 1,
        verbose: bool = True
    ) -> Dict[str, Any]:
        """
        Run Vicsek simulation.
        
        Args:
            system: VicsekSystem instance
            n_steps: Number of simulation steps
            save_interval: Save state every N steps
            verbose: Print progress information
        
        Returns:
            Dictionary with simulation results
        """
        n_saves = n_steps // save_interval + 1
        n_particles = system.n_particles
        
        # Storage arrays
        positions_history = np.zeros((n_saves, n_particles, 3))
        velocities_history = np.zeros((n_saves, n_particles, 3))
        order_parameter = np.zeros(n_saves)
        time_array = np.zeros(n_saves)
        
        # Initial state
        positions_history[0] = system.positions.copy()
        velocities_history[0] = system.velocities.copy()
        order_parameter[0] = system.compute_order_parameter()
        time_array[0] = 0.0
        
        save_idx = 1
        
        if verbose:
            print(f"      Running {n_steps} steps with dt={self.dt}")
            print(f"      Numba acceleration: {'enabled' if self.use_numba else 'disabled'}")
            print(f"      Initial order parameter: {order_parameter[0]:.4f}")
        
        # Select update function
        update_func = _update_velocities_numba if self.use_numba else _update_velocities_numpy
        
        # Warmup JIT compilation
        if self.use_numba and verbose:
            print("      Compiling Numba kernels (first run only)...")
            _ = update_func(
                system.positions[:10].copy(),
                system.velocities[:10].copy(),
                system.box_size,
                system.interaction_radius,
                system.noise,
                system.speed
            )
        
        # Main simulation loop
        iterator = tqdm(
            range(1, n_steps + 1),
            desc="      Simulating",
            ncols=70,
            bar_format='{desc}: {percentage:3.0f}%|{bar}| {n}/{total}',
            disable=not verbose
        )
        
        for step in iterator:
            # Update velocities (alignment + noise)
            system.velocities = update_func(
                system.positions,
                system.velocities,
                system.box_size,
                system.interaction_radius,
                system.noise,
                system.speed
            )
            
            # Update positions
            system.positions += system.velocities * self.dt
            
            # Apply periodic boundaries
            system.apply_periodic_boundary()
            
            # Save state
            if step % save_interval == 0:
                positions_history[save_idx] = system.positions.copy()
                velocities_history[save_idx] = system.velocities.copy()
                order_parameter[save_idx] = system.compute_order_parameter()
                time_array[save_idx] = step * self.dt
                save_idx += 1
        
        # Compile results
        result = {
            'time': time_array[:save_idx],
            'positions': positions_history[:save_idx],
            'velocities': velocities_history[:save_idx],
            'order_parameter': order_parameter[:save_idx],
            'system': system,
            'n_steps': n_steps,
            'dt': self.dt,
            'save_interval': save_interval,
            'final_order_parameter': order_parameter[save_idx - 1],
            'mean_order_parameter': np.mean(order_parameter[save_idx // 2:save_idx]),
            'std_order_parameter': np.std(order_parameter[save_idx // 2:save_idx]),
            'max_order_parameter': np.max(order_parameter[:save_idx]),
            'min_order_parameter': np.min(order_parameter[:save_idx])
        }
        
        if verbose:
            print(f"\n      Final order parameter: {result['final_order_parameter']:.4f}")
            print(f"      Mean order parameter (2nd half): {result['mean_order_parameter']:.4f}")
        
        return result
