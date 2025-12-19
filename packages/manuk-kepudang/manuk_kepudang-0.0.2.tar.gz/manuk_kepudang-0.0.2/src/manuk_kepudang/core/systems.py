"""
3D Vicsek Model System Definition.

The Vicsek model (1995) describes self-propelled particles exhibiting
collective motion through simple local alignment rules:
    1. Each particle moves with constant speed v0
    2. Each particle aligns with neighbors within radius r
    3. Random noise eta is added to the alignment

References:
    Vicsek, T., et al. (1995). Novel type of phase transition in a system
    of self-driven particles. Physical Review Letters, 75(6), 1226.
"""

import numpy as np
from typing import Tuple, Optional


class VicsekSystem:
    """
    3D Vicsek Model System.
    
    Attributes:
        n_particles: Number of particles
        box_size: Side length of cubic simulation box
        speed: Constant speed of all particles
        interaction_radius: Radius for neighbor interactions
        noise: Noise magnitude (eta)
        positions: (N, 3) array of particle positions
        velocities: (N, 3) array of particle velocities
    """
    
    def __init__(
        self,
        n_particles: int = 200,
        box_size: float = 10.0,
        speed: float = 0.5,
        interaction_radius: float = 2.0,
        noise: float = 0.5,
        seed: Optional[int] = None
    ):
        """
        Initialize Vicsek system.
        
        Args:
            n_particles: Number of particles
            box_size: Side length of cubic box (L)
            speed: Constant particle speed (v0)
            interaction_radius: Interaction radius (r)
            noise: Noise magnitude (eta)
            seed: Random seed for reproducibility
        """
        self.n_particles = n_particles
        self.box_size = box_size
        self.speed = speed
        self.interaction_radius = interaction_radius
        self.noise = noise
        self.seed = seed
        
        if seed is not None:
            np.random.seed(seed)
        
        # Initialize random positions in box
        self.positions = np.random.rand(n_particles, 3) * box_size
        
        # Initialize random velocities (normalized to speed)
        vel = np.random.randn(n_particles, 3)
        norms = np.linalg.norm(vel, axis=1, keepdims=True)
        norms[norms == 0] = 1.0  # Avoid division by zero
        self.velocities = (vel / norms) * speed
    
    def compute_order_parameter(self) -> float:
        """
        Compute the order parameter (alignment measure).
        
        phi = (1 / N * v0) * |sum(v_i)|
        
        phi ~ 0: disordered (random motion)
        phi ~ 1: ordered (collective alignment)
        
        Returns:
            Order parameter value between 0 and 1
        """
        total_velocity = np.sum(self.velocities, axis=0)
        magnitude = np.linalg.norm(total_velocity)
        return magnitude / (self.n_particles * self.speed)
    
    def compute_density(self) -> float:
        """
        Compute particle density.
        
        Returns:
            Number density (particles per unit volume)
        """
        return self.n_particles / (self.box_size ** 3)
    
    def get_state(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get current system state.
        
        Returns:
            Tuple of (positions, velocities) arrays
        """
        return self.positions.copy(), self.velocities.copy()
    
    def set_state(self, positions: np.ndarray, velocities: np.ndarray):
        """
        Set system state.
        
        Args:
            positions: (N, 3) array of positions
            velocities: (N, 3) array of velocities
        """
        self.positions = positions.copy()
        self.velocities = velocities.copy()
    
    def apply_periodic_boundary(self):
        """Apply periodic boundary conditions to positions."""
        self.positions = np.mod(self.positions, self.box_size)
    
    def __repr__(self) -> str:
        return (
            f"VicsekSystem(N={self.n_particles}, L={self.box_size}, "
            f"v0={self.speed}, r={self.interaction_radius}, η={self.noise})"
        )
