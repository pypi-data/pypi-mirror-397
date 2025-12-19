# `manuk-kepudang`: A Python Library for 3D Vicsek Model Simulation

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://img.shields.io/pypi/v/manuk-kepudang.svg)](https://pypi.org/project/manuk-kepudang/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![DOI](https://zenodo.org/badge/1105820721.svg)](https://doi.org/10.5281/zenodo.17747396)

[![NumPy](https://img.shields.io/badge/NumPy-%23013243.svg?logo=numpy&logoColor=white)](https://numpy.org/)
[![SciPy](https://img.shields.io/badge/SciPy-%230C55A5.svg?logo=scipy&logoColor=white)](https://scipy.org/)
[![Matplotlib](https://img.shields.io/badge/Matplotlib-%23ffffff.svg?logo=Matplotlib&logoColor=black)](https://matplotlib.org/)
[![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![netCDF4](https://img.shields.io/badge/netCDF4-%23004B87.svg)](https://unidata.github.io/netcdf4-python/)
[![Numba](https://img.shields.io/badge/Numba-%2300A3E0.svg?logo=numba&logoColor=white)](https://numba.pydata.org/)
[![Pillow](https://img.shields.io/badge/Pillow-%23000000.svg)](https://python-pillow.org/)
[![tqdm](https://img.shields.io/badge/tqdm-%23FFC107.svg)](https://tqdm.github.io/)

A Python library for simulating collective motion using the 3D Vicsek model with Numba JIT acceleration and spatial entropy metrics.

## Model

The Vicsek model (1995) describes self-propelled particles exhibiting collective motion through simple alignment rules. In 3D, each particle $i$ updates its velocity according to:

$$\mathbf{v}_i(t + \Delta t) = v_0 \cdot \hat{\mathbf{u}}\left( \langle \hat{\mathbf{v}}_j \rangle_{|r_{ij}| < r} + \eta \boldsymbol{\xi}_i \right)$$

where:
- $v_0$ is the constant speed of all particles
- $\langle \hat{\mathbf{v}}_j \rangle$ is the **normalized** average velocity of neighbors within radius $r$
- $\eta$ is the noise amplitude
- $\boldsymbol{\xi}_i$ is a random unit vector
- $\hat{\mathbf{u}}(\cdot)$ denotes normalization to unit vector

Position updates follow:

$$\mathbf{r}_i(t + \Delta t) = \mathbf{r}_i(t) + \mathbf{v}_i(t + \Delta t) \cdot \Delta t$$

with periodic boundary conditions in a cubic box of side $L$.

### Key Parameters

| Parameter | Symbol | Description | Typical Range |
|:---------:|:------:|:------------|:-------------:|
| N | $N$ | Number of particles | 50-5000 |
| L | $L$ | Box size | 5-50 |
| v0 | $v_0$ | Particle speed | 0.1-1.0 |
| r | $r$ | Interaction radius | 1.0-5.0 |
| eta | $\eta$ | Noise magnitude | 0.0-2.0 |
| dt | $\Delta t$ | Time step | 0.1-1.0 |

### Order Parameter

The collective alignment is quantified by the order parameter:

$$\phi = \frac{1}{N v_0} \left| \sum_{i=1}^{N} \mathbf{v}_i \right|$$

where $\phi \approx 0$ indicates disordered motion and $\phi \approx 1$ indicates collective alignment.

## Spatial Entropy Metrics

This library includes rigorous information-theoretic measures to quantify spatial order/disorder:

| Metric | Description | High Value | Low Value |
|:------:|:------------|:-----------|:----------|
| Positional Entropy | Shannon entropy of spatial distribution | Uniform (disordered) | Clustered (ordered) |
| Orientational Entropy | Entropy of velocity directions on unit sphere | Isotropic (disordered) | Aligned (ordered) |
| Local Alignment Entropy | Heterogeneity of local order | Heterogeneous | Homogeneous |
| Pair Correlation Entropy | From radial distribution function g(r) | Ideal gas | Crystalline |
| Voronoi Cell Entropy | Geometric packing disorder | Irregular | Regular |
| Position-Velocity MI | Mutual information coupling | Spatial structure | Homogeneous |
| **Spatial Complexity Index** | Weighted composite measure | Disordered | Ordered |

*SCI = (H_positional + H_orientational + H_local_align + H_pair + H_voronoi + (1-MI)) / 6

## Installation

**From PyPI:**
```bash
pip install manuk-kepudang
```

**From source:**
```bash
git clone https://github.com/sandyherho/manuk-kepudang.git
cd manuk-kepudang
pip install .
```

**Development installation with Poetry:**
```bash
git clone https://github.com/sandyherho/manuk-kepudang.git
cd manuk-kepudang
poetry install
```

## Quick Start

**CLI:**
```bash
manuk-kepudang case1          # Run ordered phase scenario
manuk-kepudang case2          # Run disordered phase scenario
manuk-kepudang --all          # Run all test cases
manuk-kepudang case1 --no-entropy  # Skip entropy computation
```

**Python API:**
```python
from manuk_kepudang import VicsekSystem, VicsekSolver
from manuk_kepudang import compute_metrics_timeseries

# Create system with 200 particles
system = VicsekSystem(
    n_particles=200,
    box_size=10.0,
    speed=0.5,
    interaction_radius=2.0,
    noise=0.3
)

# Initialize solver with Numba acceleration
solver = VicsekSolver(dt=1.0, use_numba=True)

# Run simulation for 500 steps
result = solver.solve(system, n_steps=500)

# Compute entropy metrics
metrics = compute_metrics_timeseries(
    result['positions'],
    result['velocities'],
    result['time'],
    system.box_size,
    system.speed,
    system.interaction_radius
)

print(f"Final order parameter: {result['final_order_parameter']:.4f}")
print(f"Final SCI (disorder): {metrics['spatial_complexity_index_final']:.4f}")
```

## Features

- **High-performance**: Numba JIT compilation for 10-100x speedup
- **3D simulation**: Full three-dimensional particle dynamics
- **Periodic boundaries**: Correct handling of boundary conditions
- **Order parameter tracking**: Real-time collective alignment measurement
- **Spatial entropy metrics**: Rigorous information-theoretic disorder measures
- **Multiple output formats**: CSV, NetCDF (CF-compliant), PNG, GIF
- **Configurable scenarios**: Text-based configuration files

## Output Files

The library generates:

- **CSV files**: 
  - `*_order_parameter.csv` - Order parameter time series
  - `*_entropy_timeseries.csv` - All entropy measures over time
  - `*_entropy_summary.csv` - Statistics (mean, std, min, max, final)
  - `*_final_state.csv` - Final particle positions and velocities
- **NetCDF**: Full trajectory data with all metrics and CF-compliant metadata
  - Variables: `x`, `y`, `z`, `vx`, `vy`, `vz`, `order_parameter`, all entropy metrics
- **PNG**: Static summary plots with entropy visualization
- **GIF**: Animated 3D visualization with camera rotation

## Test Cases

| Case | Description | N | η |
|:----:|:------------|:-:|:-:|
| 1 | Ordered phase | 200 | 0.3 |
| 2 | Disordered phase | 200 | 2.0 |
| 3 | Large system | 500 | 0.5 |
| 4 | Phase transition | 300 | 1.0 |

## Dependencies

- **numpy** >= 1.20.0
- **scipy** >= 1.7.0
- **matplotlib** >= 3.3.0
- **pandas** >= 1.3.0
- **netCDF4** >= 1.5.0
- **numba** >= 0.53.0
- **Pillow** >= 8.0.0
- **tqdm** >= 4.60.0

## License

MIT © Sandy H. S. Herho, Gandhi Napitupulu, Iwan P. Anwar, Nurjanna J. Trilaksono, Rusmawan Suwarman, Dasapta E. Irawan

## Citation

```bibtex
@software{herho2025_manuk_kepudang,
  title   = {manuk-kepudang: A Python library for 3D Vicsek model simulation},
  author  = {Herho, Sandy H. S. and Napitupulu, G. and Anwar, Iwan P. and Trilaksono, Nurjanna J. and Suwarman, Rusmawan and Irawan, Dasapta E.},
  year    = {2025},
  url     = {https://github.com/sandyherho/manuk-kepudang}
}
```
