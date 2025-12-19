"""
Spatial Entropy and Complexity Metrics for Vicsek Model.

This module implements information-theoretic and statistical physics measures
to quantify spatial order/disorder in collective motion systems.

Measures implemented:
1. Positional Entropy (Shannon entropy of spatial distribution)
2. Orientational Entropy (Shannon entropy of velocity directions)
3. Local Alignment Entropy (heterogeneity of local order)
4. Pair Correlation Entropy (from radial distribution function)
5. Voronoi Cell Entropy (geometric disorder measure)
6. Mutual Information (position-velocity coupling)
7. Spatial Complexity Index (composite measure)

References:
    - Shannon, C.E. (1948). A mathematical theory of communication.
    - Vicsek, T., et al. (1995). Physical Review Letters, 75(6), 1226.
    - Attanasi, A., et al. (2014). PLoS Computational Biology, 10(1).
"""

import numpy as np
from typing import Dict, Tuple, Optional
from scipy.spatial import cKDTree, Voronoi
from scipy.special import digamma


def compute_positional_entropy(
    positions: np.ndarray,
    box_size: float,
    n_bins: int = 10
) -> float:
    """
    Compute Shannon entropy of spatial particle distribution.
    
    Discretizes the simulation box into n_bins^3 cells and computes
    the entropy of the resulting occupation probability distribution.
    
    H_pos = -sum(p_i * log(p_i)) for occupied cells
    
    High entropy: uniform distribution (disordered)
    Low entropy: clustered distribution (ordered/aggregated)
    
    Normalized to [0, 1] where 1 = maximum entropy (uniform).
    
    Args:
        positions: (N, 3) array of particle positions
        box_size: Side length of cubic box
        n_bins: Number of bins per dimension
    
    Returns:
        Normalized positional entropy in [0, 1]
    """
    # Bin particles into 3D grid
    bin_edges = np.linspace(0, box_size, n_bins + 1)
    hist, _ = np.histogramdd(positions, bins=[bin_edges] * 3)
    
    # Compute probability distribution (only non-zero bins)
    total = hist.sum()
    if total == 0:
        return 0.0
    
    probs = hist.flatten() / total
    probs = probs[probs > 0]  # Remove zeros for log
    
    # Shannon entropy
    entropy = -np.sum(probs * np.log(probs))
    
    # Maximum entropy for uniform distribution in n_bins^3 cells
    # But limited by number of particles
    n_particles = len(positions)
    n_cells = n_bins ** 3
    
    # Maximum entropy: particles spread as uniformly as possible
    if n_particles >= n_cells:
        max_entropy = np.log(n_cells)
    else:
        # When fewer particles than cells, max entropy is log(N)
        max_entropy = np.log(n_particles)
    
    if max_entropy == 0:
        return 0.0
    
    return entropy / max_entropy


def compute_orientational_entropy(
    velocities: np.ndarray,
    n_bins_theta: int = 18,
    n_bins_phi: int = 36
) -> float:
    """
    Compute Shannon entropy of velocity orientations on unit sphere.
    
    Converts velocities to spherical coordinates and bins them to
    compute the entropy of the angular distribution.
    
    High entropy: isotropic velocity directions (disordered)
    Low entropy: aligned velocities (ordered/flocking)
    
    Normalized to [0, 1] where 1 = uniform distribution on sphere.
    
    Args:
        velocities: (N, 3) array of particle velocities
        n_bins_theta: Number of bins for polar angle [0, pi]
        n_bins_phi: Number of bins for azimuthal angle [0, 2pi]
    
    Returns:
        Normalized orientational entropy in [0, 1]
    """
    # Normalize velocities to unit vectors
    norms = np.linalg.norm(velocities, axis=1, keepdims=True)
    norms[norms < 1e-10] = 1.0
    unit_vel = velocities / norms
    
    # Convert to spherical coordinates
    # theta: polar angle from z-axis [0, pi]
    # phi: azimuthal angle in xy-plane [0, 2pi]
    theta = np.arccos(np.clip(unit_vel[:, 2], -1, 1))
    phi = np.arctan2(unit_vel[:, 1], unit_vel[:, 0]) + np.pi  # Shift to [0, 2pi]
    
    # 2D histogram on sphere
    theta_edges = np.linspace(0, np.pi, n_bins_theta + 1)
    phi_edges = np.linspace(0, 2 * np.pi, n_bins_phi + 1)
    
    hist, _, _ = np.histogram2d(theta, phi, bins=[theta_edges, phi_edges])
    
    # Weight by solid angle (sin(theta) factor for proper spherical measure)
    # Each bin has solid angle proportional to sin(theta_center) * dtheta * dphi
    theta_centers = (theta_edges[:-1] + theta_edges[1:]) / 2
    solid_angles = np.sin(theta_centers)[:, np.newaxis] * np.ones((1, n_bins_phi))
    
    # Normalize histogram by solid angle to get density
    weighted_hist = hist / (solid_angles + 1e-10)
    
    # Probability distribution
    total = weighted_hist.sum()
    if total == 0:
        return 0.0
    
    probs = weighted_hist.flatten() / total
    probs = probs[probs > 0]
    
    # Shannon entropy
    entropy = -np.sum(probs * np.log(probs))
    
    # Maximum entropy for uniform distribution on sphere
    n_particles = len(velocities)
    n_cells = n_bins_theta * n_bins_phi
    
    if n_particles >= n_cells:
        max_entropy = np.log(n_cells)
    else:
        max_entropy = np.log(n_particles)
    
    if max_entropy == 0:
        return 0.0
    
    return entropy / max_entropy


def compute_local_alignment_field(
    positions: np.ndarray,
    velocities: np.ndarray,
    box_size: float,
    radius: float
) -> np.ndarray:
    """
    Compute local order parameter for each particle.
    
    For each particle, computes the alignment with its neighbors
    within the interaction radius.
    
    Args:
        positions: (N, 3) particle positions
        velocities: (N, 3) particle velocities
        box_size: Side length of cubic box
        radius: Interaction radius
    
    Returns:
        (N,) array of local order parameters in [0, 1]
    """
    n = len(positions)
    speed = np.linalg.norm(velocities[0])
    if speed < 1e-10:
        speed = 1.0
    
    local_phi = np.zeros(n)
    
    # Build KD-tree with periodic boundary handling
    # Use wrapped positions for tree queries
    tree = cKDTree(positions, boxsize=box_size)
    
    for i in range(n):
        # Find neighbors within radius
        neighbors = tree.query_ball_point(positions[i], radius)
        
        if len(neighbors) > 0:
            # Sum neighbor velocities
            vel_sum = np.sum(velocities[neighbors], axis=0)
            local_phi[i] = np.linalg.norm(vel_sum) / (len(neighbors) * speed)
        else:
            local_phi[i] = 1.0  # Single particle is "aligned" with itself
    
    return local_phi


def compute_local_alignment_entropy(
    positions: np.ndarray,
    velocities: np.ndarray,
    box_size: float,
    radius: float,
    n_bins: int = 20
) -> Tuple[float, np.ndarray]:
    """
    Compute entropy of local alignment distribution.
    
    Measures heterogeneity in local order across the system.
    
    High entropy: wide distribution of local alignments (heterogeneous)
    Low entropy: uniform local alignment everywhere (homogeneous)
    
    Args:
        positions: (N, 3) particle positions
        velocities: (N, 3) particle velocities
        box_size: Side length of cubic box
        radius: Interaction radius
        n_bins: Number of bins for histogram
    
    Returns:
        Tuple of (normalized entropy, local_phi array)
    """
    local_phi = compute_local_alignment_field(positions, velocities, box_size, radius)
    
    # Histogram of local order parameters
    hist, _ = np.histogram(local_phi, bins=n_bins, range=(0, 1))
    
    # Probability distribution
    total = hist.sum()
    if total == 0:
        return 0.0, local_phi
    
    probs = hist / total
    probs = probs[probs > 0]
    
    # Shannon entropy
    entropy = -np.sum(probs * np.log(probs))
    
    # Maximum entropy = log(n_bins) for uniform distribution
    max_entropy = np.log(n_bins)
    
    return entropy / max_entropy, local_phi


def compute_radial_distribution_function(
    positions: np.ndarray,
    box_size: float,
    n_bins: int = 50,
    r_max: Optional[float] = None
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute the radial distribution function g(r).
    
    g(r) measures the probability of finding a particle at distance r
    from another particle, relative to an ideal gas.
    
    Args:
        positions: (N, 3) particle positions
        box_size: Side length of cubic box
        n_bins: Number of radial bins
        r_max: Maximum radius (default: box_size/2)
    
    Returns:
        Tuple of (r values, g(r) values)
    """
    n = len(positions)
    if r_max is None:
        r_max = box_size / 2
    
    # Compute all pairwise distances with PBC
    delta = positions[:, np.newaxis, :] - positions[np.newaxis, :, :]
    delta = delta - box_size * np.round(delta / box_size)
    distances = np.linalg.norm(delta, axis=2)
    
    # Remove self-distances (diagonal)
    mask = ~np.eye(n, dtype=bool)
    distances = distances[mask]
    
    # Histogram
    r_edges = np.linspace(0, r_max, n_bins + 1)
    hist, _ = np.histogram(distances, bins=r_edges)
    
    # Normalize by ideal gas expectation
    r_centers = (r_edges[:-1] + r_edges[1:]) / 2
    dr = r_edges[1] - r_edges[0]
    
    # Volume of spherical shell
    shell_volumes = 4 * np.pi * r_centers**2 * dr
    
    # Ideal gas density
    density = n / (box_size ** 3)
    
    # g(r) = histogram / (N * shell_volume * density)
    # Factor of 2 because we count each pair twice
    g_r = hist / (n * shell_volumes * density + 1e-10)
    
    return r_centers, g_r


def compute_pair_correlation_entropy(
    positions: np.ndarray,
    box_size: float,
    n_bins: int = 50
) -> float:
    """
    Compute entropy derived from pair correlation function.
    
    S_pair = -integral(g(r) * log(g(r)) * r^2 dr) (normalized)
    
    High entropy: g(r) ≈ 1 everywhere (ideal gas, disordered)
    Low entropy: strong peaks in g(r) (crystalline order)
    
    Args:
        positions: (N, 3) particle positions
        box_size: Side length of cubic box
        n_bins: Number of radial bins
    
    Returns:
        Normalized pair correlation entropy in [0, 1]
    """
    r, g_r = compute_radial_distribution_function(positions, box_size, n_bins)
    
    # Avoid log(0) and log of very small values
    g_r_safe = np.clip(g_r, 1e-10, None)
    
    # Entropy integrand: -g(r) * log(g(r)) * r^2
    # Weight by r^2 for proper 3D measure
    dr = r[1] - r[0] if len(r) > 1 else 1.0
    
    # Only include where g(r) > 0
    mask = g_r > 1e-10
    if not np.any(mask):
        return 1.0  # No correlations = ideal gas = max disorder
    
    # Compute weighted entropy
    integrand = np.zeros_like(g_r)
    integrand[mask] = -g_r[mask] * np.log(g_r_safe[mask]) * r[mask]**2
    
    entropy = np.sum(integrand) * dr
    
    # Normalize: ideal gas has g(r)=1, entropy = 0 in this formulation
    # Crystalline has sharp peaks, negative contribution
    # Rescale to [0, 1] empirically
    
    # Reference: ideal gas entropy
    ideal_integrand = r**2  # g(r)=1, -1*log(1)=0, but let's use deviation
    
    # Use deviation from ideal gas
    deviation = np.sum(np.abs(g_r - 1.0) * r**2) * dr
    max_deviation = np.sum(r**2) * dr  # Maximum if g(r) = 0 or 2 everywhere
    
    if max_deviation == 0:
        return 1.0
    
    # High deviation = low entropy (ordered), low deviation = high entropy (disordered)
    normalized_entropy = 1.0 - deviation / max_deviation
    
    return np.clip(normalized_entropy, 0, 1)


def compute_voronoi_entropy(
    positions: np.ndarray,
    box_size: float
) -> float:
    """
    Compute entropy of Voronoi cell volume distribution.
    
    In a perfectly ordered (crystalline) system, all Voronoi cells
    have the same volume. In a disordered system, volumes vary.
    
    Uses coefficient of variation as a disorder measure, converted
    to entropy-like scale.
    
    Args:
        positions: (N, 3) particle positions
        box_size: Side length of cubic box
    
    Returns:
        Normalized Voronoi entropy in [0, 1] (1 = disordered)
    """
    n = len(positions)
    if n < 4:
        return 0.5  # Not enough points
    
    try:
        # Create periodic copies for Voronoi with PBC
        # This is approximate - full PBC Voronoi is complex
        offsets = np.array([
            [0, 0, 0], [1, 0, 0], [-1, 0, 0],
            [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]
        ]) * box_size
        
        extended_pos = []
        for offset in offsets:
            extended_pos.append(positions + offset)
        extended_pos = np.vstack(extended_pos)
        
        # Compute Voronoi
        vor = Voronoi(extended_pos)
        
        # Get volumes of cells corresponding to original particles
        volumes = []
        for i in range(n):
            region_idx = vor.point_region[i]
            if region_idx == -1:
                continue
            region = vor.regions[region_idx]
            if -1 in region or len(region) == 0:
                continue
            
            # Compute volume using vertices
            vertices = vor.vertices[region]
            if len(vertices) < 4:
                continue
            
            # Use convex hull volume (approximate)
            try:
                from scipy.spatial import ConvexHull
                hull = ConvexHull(vertices)
                volumes.append(hull.volume)
            except:
                continue
        
        if len(volumes) < 3:
            return 0.5
        
        volumes = np.array(volumes)
        
        # Coefficient of variation as disorder measure
        cv = np.std(volumes) / (np.mean(volumes) + 1e-10)
        
        # Map CV to [0, 1] entropy scale
        # CV = 0 (all same) -> entropy = 0 (ordered)
        # CV > 1 (high variation) -> entropy -> 1 (disordered)
        entropy = 1.0 - np.exp(-cv)
        
        return np.clip(entropy, 0, 1)
    
    except Exception:
        return 0.5  # Return neutral value on error


def compute_velocity_position_mutual_information(
    positions: np.ndarray,
    velocities: np.ndarray,
    box_size: float,
    n_bins: int = 8
) -> float:
    """
    Compute mutual information between position and velocity direction.
    
    I(X; V) = H(X) + H(V) - H(X, V)
    
    High MI: velocity direction depends on position (spatial structure)
    Low MI: velocity independent of position (homogeneous behavior)
    
    Normalized to [0, 1].
    
    Args:
        positions: (N, 3) particle positions
        velocities: (N, 3) particle velocities
        box_size: Side length of cubic box
        n_bins: Number of bins per dimension
    
    Returns:
        Normalized mutual information in [0, 1]
    """
    n = len(positions)
    
    # Discretize positions into cells
    pos_bins = np.floor(positions / box_size * n_bins).astype(int)
    pos_bins = np.clip(pos_bins, 0, n_bins - 1)
    pos_idx = pos_bins[:, 0] * n_bins**2 + pos_bins[:, 1] * n_bins + pos_bins[:, 2]
    
    # Discretize velocity directions into octants (8 regions)
    vel_signs = (velocities > 0).astype(int)
    vel_idx = vel_signs[:, 0] * 4 + vel_signs[:, 1] * 2 + vel_signs[:, 2]
    
    # Joint histogram
    n_pos_bins = n_bins ** 3
    n_vel_bins = 8
    
    joint_hist = np.zeros((n_pos_bins, n_vel_bins))
    for i in range(n):
        joint_hist[pos_idx[i], vel_idx[i]] += 1
    
    # Marginal histograms
    pos_hist = joint_hist.sum(axis=1)
    vel_hist = joint_hist.sum(axis=0)
    
    # Probabilities
    p_joint = joint_hist / n
    p_pos = pos_hist / n
    p_vel = vel_hist / n
    
    # Entropies
    def entropy(p):
        p = p[p > 0]
        return -np.sum(p * np.log(p))
    
    H_pos = entropy(p_pos)
    H_vel = entropy(p_vel)
    H_joint = entropy(p_joint.flatten())
    
    # Mutual information
    MI = H_pos + H_vel - H_joint
    
    # Normalize by min(H_pos, H_vel)
    max_MI = min(H_pos, H_vel) if min(H_pos, H_vel) > 0 else 1.0
    
    return np.clip(MI / max_MI, 0, 1) if max_MI > 0 else 0.0


def compute_spatial_complexity_index(
    positions: np.ndarray,
    velocities: np.ndarray,
    box_size: float,
    radius: float
) -> Dict[str, float]:
    """
    Compute composite spatial complexity index combining multiple measures.
    
    The Spatial Complexity Index (SCI) is defined as:
    
    SCI = (H_pos + H_orient + H_local + H_pair + H_voronoi + (1-MI)) / 6
    
    Where all measures are normalized to [0, 1].
    
    Args:
        positions: (N, 3) particle positions
        velocities: (N, 3) particle velocities
        box_size: Side length of cubic box
        radius: Interaction radius for local alignment
    
    Returns:
        Dictionary with all entropy measures and composite index
    """
    # Compute all measures
    H_positional = compute_positional_entropy(positions, box_size)
    H_orientational = compute_orientational_entropy(velocities)
    H_local_align, local_phi = compute_local_alignment_entropy(
        positions, velocities, box_size, radius
    )
    H_pair = compute_pair_correlation_entropy(positions, box_size)
    H_voronoi = compute_voronoi_entropy(positions, box_size)
    MI_pos_vel = compute_velocity_position_mutual_information(
        positions, velocities, box_size
    )
    
    # Local alignment statistics
    local_phi_mean = np.mean(local_phi)
    local_phi_std = np.std(local_phi)
    
    # Composite index (equal weights, 6 components)
    # High SCI = high disorder/entropy
    weights = np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0]) / 6.0
    
    components = np.array([
        H_positional,
        H_orientational,
        H_local_align,
        H_pair,
        H_voronoi,
        1.0 - MI_pos_vel  # Invert MI: low coupling = high disorder
    ])
    
    SCI = np.sum(weights * components)
    
    return {
        'positional_entropy': H_positional,
        'orientational_entropy': H_orientational,
        'local_alignment_entropy': H_local_align,
        'pair_correlation_entropy': H_pair,
        'voronoi_entropy': H_voronoi,
        'position_velocity_mutual_info': MI_pos_vel,
        'local_alignment_mean': local_phi_mean,
        'local_alignment_std': local_phi_std,
        'spatial_complexity_index': SCI
    }


def compute_all_metrics(
    positions: np.ndarray,
    velocities: np.ndarray,
    box_size: float,
    speed: float,
    radius: float
) -> Dict[str, float]:
    """
    Compute all available metrics for a single time step.
    
    Args:
        positions: (N, 3) particle positions
        velocities: (N, 3) particle velocities
        box_size: Side length of cubic box
        speed: Particle speed (for order parameter normalization)
        radius: Interaction radius
    
    Returns:
        Dictionary with all metrics
    """
    n = len(positions)
    
    # Standard order parameter
    total_velocity = np.sum(velocities, axis=0)
    order_parameter = np.linalg.norm(total_velocity) / (n * speed)
    
    # Spatial complexity measures
    spatial_metrics = compute_spatial_complexity_index(
        positions, velocities, box_size, radius
    )
    
    # Combine all metrics
    result = {
        'order_parameter': order_parameter,
        **spatial_metrics
    }
    
    return result


def compute_metrics_timeseries(
    positions_history: np.ndarray,
    velocities_history: np.ndarray,
    time_array: np.ndarray,
    box_size: float,
    speed: float,
    radius: float,
    verbose: bool = True
) -> Dict[str, np.ndarray]:
    """
    Compute all metrics for entire simulation trajectory.
    
    Args:
        positions_history: (T, N, 3) position trajectory
        velocities_history: (T, N, 3) velocity trajectory
        time_array: (T,) time values
        box_size: Side length of cubic box
        speed: Particle speed
        radius: Interaction radius
        verbose: Print progress
    
    Returns:
        Dictionary with time series of all metrics
    """
    from tqdm import tqdm
    
    n_times = len(time_array)
    
    # Initialize storage
    metrics_keys = [
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
    
    results = {key: np.zeros(n_times) for key in metrics_keys}
    results['time'] = time_array.copy()
    
    iterator = tqdm(
        range(n_times),
        desc="      Computing metrics",
        ncols=70,
        bar_format='{desc}: {percentage:3.0f}%|{bar}| {n}/{total}',
        disable=not verbose
    )
    
    for t in iterator:
        metrics = compute_all_metrics(
            positions_history[t],
            velocities_history[t],
            box_size,
            speed,
            radius
        )
        
        for key in metrics_keys:
            results[key][t] = metrics[key]
    
    # Compute summary statistics
    half_idx = n_times // 2
    for key in metrics_keys:
        results[f'{key}_mean'] = np.mean(results[key][half_idx:])
        results[f'{key}_std'] = np.std(results[key][half_idx:])
        results[f'{key}_final'] = results[key][-1]
    
    return results
