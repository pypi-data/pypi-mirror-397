"""
Visualization for 3D Vicsek Model.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from mpl_toolkits.mplot3d import Axes3D
from pathlib import Path
from tqdm import tqdm
from typing import Dict, Any, Optional
import warnings

warnings.filterwarnings('ignore')

from PIL import Image, ImageFilter, ImageEnhance
import io


class Animator:
    """
    Create professional visualizations for Vicsek collective motion
    with stunning visual effects.
    """
    
    # Cyberpunk/Neon dark theme color palette
    COLOR_BG = '#0A0E14'
    COLOR_BG_LIGHTER = '#11151C'
    COLOR_BG_PANEL = '#151A23'
    COLOR_PARTICLE = '#00F5D4'
    COLOR_VELOCITY = '#FF6B9D'
    COLOR_ACCENT = '#FFE66D'
    COLOR_ACCENT2 = '#00D9FF'
    COLOR_ACCENT3 = '#FF9F1C'
    COLOR_GRID = '#1E2633'
    COLOR_TEXT = '#E6EDF3'
    COLOR_TITLE = '#FFFFFF'
    COLOR_GLOW = '#00F5D4'
    
    def __init__(self, fps: int = 30, dpi: int = 150):
        """
        Initialize animator.
        
        Args:
            fps: Frames per second for animations
            dpi: Resolution for output images
        """
        self.fps = fps
        self.dpi = dpi
        self._setup_style()
    
    def _setup_style(self):
        """Setup matplotlib dark theme styling with enhanced aesthetics."""
        plt.style.use('dark_background')
        plt.rcParams.update({
            'figure.facecolor': self.COLOR_BG,
            'axes.facecolor': self.COLOR_BG_LIGHTER,
            'axes.edgecolor': self.COLOR_GRID,
            'axes.labelcolor': self.COLOR_TEXT,
            'axes.titlecolor': self.COLOR_TITLE,
            'xtick.color': self.COLOR_TEXT,
            'ytick.color': self.COLOR_TEXT,
            'text.color': self.COLOR_TEXT,
            'grid.color': self.COLOR_GRID,
            'grid.alpha': 0.4,
            'legend.facecolor': self.COLOR_BG_PANEL,
            'legend.edgecolor': self.COLOR_GRID,
            'font.family': 'sans-serif',
            'font.size': 11,
            'axes.labelsize': 13,
            'axes.titlesize': 15,
            'lines.antialiased': True,
            'figure.autolayout': False,
        })
    
    def _add_glow_effect(self, image: Image.Image, intensity: float = 1.5) -> Image.Image:
        """Add subtle glow effect to image."""
        glow = image.filter(ImageFilter.GaussianBlur(radius=3))
        enhancer = ImageEnhance.Brightness(glow)
        glow = enhancer.enhance(0.5)
        return Image.blend(image, glow, alpha=0.15)
    
    def create_static_plot(
        self,
        result: Dict[str, Any],
        filepath: str,
        title: str = "3D Vicsek Model",
        metrics: Optional[Dict[str, Any]] = None
    ):
        """
        Create static plot with order parameter time series and final state.
        
        Args:
            result: Simulation result dictionary
            filepath: Output file path
            title: Plot title
            metrics: Optional entropy metrics dictionary
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Determine layout based on whether we have metrics
        if metrics is not None:
            fig = plt.figure(figsize=(20, 10), facecolor=self.COLOR_BG)
            fig.suptitle(f'{title}\nCollective Motion Dynamics',
                        fontsize=18, fontweight='bold', color=self.COLOR_TITLE, y=0.98)
            
            # Create 2x2 grid
            ax1 = fig.add_subplot(221, facecolor=self.COLOR_BG_LIGHTER)
            ax2 = fig.add_subplot(222, projection='3d', facecolor=self.COLOR_BG)
            ax3 = fig.add_subplot(223, facecolor=self.COLOR_BG_LIGHTER)
            ax4 = fig.add_subplot(224, facecolor=self.COLOR_BG_LIGHTER)
        else:
            fig = plt.figure(figsize=(16, 6), facecolor=self.COLOR_BG)
            fig.suptitle(f'{title}\nCollective Motion Dynamics',
                        fontsize=18, fontweight='bold', color=self.COLOR_TITLE, y=0.98)
            ax1 = fig.add_subplot(121, facecolor=self.COLOR_BG_LIGHTER)
            ax2 = fig.add_subplot(122, projection='3d', facecolor=self.COLOR_BG)
        
        # Plot 1: Order parameter time series
        time = result['time']
        phi = result['order_parameter']
        
        ax1.plot(time, phi, color=self.COLOR_PARTICLE, lw=2, alpha=0.9)
        ax1.fill_between(time, 0, phi, color=self.COLOR_PARTICLE, alpha=0.2)
        
        ax1.axhline(y=result['mean_order_parameter'], color=self.COLOR_ACCENT,
                   linestyle='--', lw=1.5, alpha=0.8, label=f"Mean: {result['mean_order_parameter']:.3f}")
        
        ax1.set_xlabel('Time', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Order Parameter φ', fontsize=14, fontweight='bold')
        ax1.set_title('Alignment Evolution', fontsize=14, fontweight='bold', pad=10)
        ax1.set_ylim(0, 1.05)
        ax1.set_xlim(time[0], time[-1])
        ax1.legend(loc='upper right', fontsize=11)
        ax1.grid(True, alpha=0.3)
        
        for spine in ax1.spines.values():
            spine.set_color(self.COLOR_GRID)
        
        # Plot 2: Final state 3D visualization
        pos = result['positions'][-1]
        vel = result['velocities'][-1]
        L = result['system'].box_size
        
        ax2.quiver(pos[:, 0], pos[:, 1], pos[:, 2],
                  vel[:, 0], vel[:, 1], vel[:, 2],
                  length=1.5, normalize=True, color=self.COLOR_PARTICLE, alpha=0.7)
        
        ax2.set_xlim(0, L)
        ax2.set_ylim(0, L)
        ax2.set_zlim(0, L)
        ax2.set_xlabel('X', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Y', fontsize=12, fontweight='bold')
        ax2.set_zlabel('Z', fontsize=12, fontweight='bold')
        ax2.set_title(f'Final State (φ = {result["final_order_parameter"]:.3f})',
                     fontsize=14, fontweight='bold', pad=10)
        
        ax2.xaxis.pane.fill = True
        ax2.yaxis.pane.fill = True
        ax2.zaxis.pane.fill = True
        ax2.xaxis.pane.set_facecolor(self.COLOR_BG_LIGHTER)
        ax2.yaxis.pane.set_facecolor(self.COLOR_BG_LIGHTER)
        ax2.zaxis.pane.set_facecolor(self.COLOR_BG_LIGHTER)
        ax2.tick_params(colors=self.COLOR_TEXT, labelsize=9)
        
        # Plot 3 & 4: Entropy metrics (if available)
        if metrics is not None:
            # Plot 3: Entropy measures over time
            ax3.plot(metrics['time'], metrics['orientational_entropy'],
                    color=self.COLOR_PARTICLE, lw=2, alpha=0.9, label='Orientational')
            ax3.plot(metrics['time'], metrics['positional_entropy'],
                    color=self.COLOR_ACCENT2, lw=2, alpha=0.9, label='Positional')
            ax3.plot(metrics['time'], metrics['spatial_complexity_index'],
                    color=self.COLOR_ACCENT3, lw=2, alpha=0.9, label='SCI')
            
            ax3.set_xlabel('Time', fontsize=14, fontweight='bold')
            ax3.set_ylabel('Entropy (normalized)', fontsize=14, fontweight='bold')
            ax3.set_title('Spatial Entropy Evolution', fontsize=14, fontweight='bold', pad=10)
            ax3.set_ylim(0, 1.05)
            ax3.set_xlim(time[0], time[-1])
            ax3.legend(loc='upper right', fontsize=10)
            ax3.grid(True, alpha=0.3)
            
            for spine in ax3.spines.values():
                spine.set_color(self.COLOR_GRID)
            
            # Plot 4: Final entropy summary (bar chart)
            entropy_names = ['Orient.', 'Position.', 'Local\nAlign.', 'Pair\nCorr.', 'Voronoi', 'SCI']
            entropy_values = [
                metrics['orientational_entropy_final'],
                metrics['positional_entropy_final'],
                metrics['local_alignment_entropy_final'],
                metrics['pair_correlation_entropy_final'],
                metrics['voronoi_entropy_final'],
                metrics['spatial_complexity_index_final']
            ]
            
            colors = [self.COLOR_PARTICLE, self.COLOR_ACCENT2, self.COLOR_VELOCITY,
                     self.COLOR_ACCENT, self.COLOR_ACCENT3, '#FFFFFF']
            
            bars = ax4.bar(entropy_names, entropy_values, color=colors, alpha=0.8, edgecolor='white')
            
            ax4.set_ylabel('Entropy (normalized)', fontsize=14, fontweight='bold')
            ax4.set_title('Final Entropy Measures', fontsize=14, fontweight='bold', pad=10)
            ax4.set_ylim(0, 1.05)
            ax4.grid(True, alpha=0.3, axis='y')
            
            # Add value labels on bars
            for bar, val in zip(bars, entropy_values):
                ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                        f'{val:.2f}', ha='center', va='bottom', fontsize=10,
                        color=self.COLOR_TEXT, fontweight='bold')
            
            for spine in ax4.spines.values():
                spine.set_color(self.COLOR_GRID)
        
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        plt.savefig(filepath, dpi=self.dpi, facecolor=self.COLOR_BG,
                   edgecolor='none', bbox_inches='tight')
        plt.close(fig)
    
    def create_animation(self, result: Dict[str, Any], filepath: str,
                         title: str = "3D Vicsek Model", skip: int = None,
                         duration_seconds: float = 15.0):
        """
        Create stunning animated 3D visualization of collective motion
        with dramatic camera movement.
        
        Args:
            result: Simulation result dictionary
            filepath: Output file path
            title: Animation title
            skip: Frame skip (auto-calculated if None)
            duration_seconds: Target duration for the animation in seconds
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        positions = result['positions']
        velocities = result['velocities']
        time = result['time']
        phi = result['order_parameter']
        system = result['system']
        L = system.box_size
        N = system.n_particles
        eta = system.noise
        v0 = system.speed
        r = system.interaction_radius
        rho = N / (L ** 3)
        
        n_frames_total = len(time)
        
        # Target frames based on desired duration
        target_frames = int(duration_seconds * self.fps)
        target_frames = min(target_frames, 300)
        skip = max(1, n_frames_total // target_frames) if skip is None else skip
        
        frame_indices = np.arange(0, n_frames_total, skip)
        n_frames = len(frame_indices)
        
        print(f"      Generating {n_frames} frames...")
        
        anim_dpi = 120
        frames = []
        
        # Dramatic camera motion: full 360° rotation with smooth elevation changes
        t_norm = np.linspace(0, 1, n_frames)
        
        # Full rotation (360°) with easing for smooth start/end
        ease_func = lambda t: t - 0.05 * np.sin(2 * np.pi * t)  # Slight easing
        azim_start, azim_end = 0, 360
        azims = azim_start + (azim_end - azim_start) * ease_func(t_norm)
        
        # Dramatic elevation: sweep from low to high and back
        elevs = 15 + 25 * np.sin(np.pi * t_norm)  # 15° to 40° and back
        
        # Optional: add slight "zoom" effect via distance (not directly supported, but we can adjust)
        
        for i, idx in enumerate(tqdm(frame_indices,
                                      desc="      Rendering",
                                      ncols=70,
                                      bar_format='{desc}: {percentage:3.0f}%|{bar}| {n}/{total}')):
            
            fig = plt.figure(figsize=(12, 10), facecolor=self.COLOR_BG, dpi=anim_dpi)
            ax = fig.add_subplot(111, projection='3d', facecolor=self.COLOR_BG)
            
            pos = positions[idx]
            vel = velocities[idx]
            
            ax.view_init(elev=elevs[i], azim=azims[i])
            ax.set_xlim(0, L)
            ax.set_ylim(0, L)
            ax.set_zlim(0, L)
            
            # Draw particles with velocity vectors
            ax.quiver(pos[:, 0], pos[:, 1], pos[:, 2],
                     vel[:, 0], vel[:, 1], vel[:, 2],
                     length=1.3, normalize=True,
                     color=self.COLOR_PARTICLE, alpha=0.7, linewidth=1.0,
                     arrow_length_ratio=0.3)
            
            # Clean axis labels
            ax.set_xlabel('X', fontsize=11, fontweight='bold', color=self.COLOR_TEXT, labelpad=8)
            ax.set_ylabel('Y', fontsize=11, fontweight='bold', color=self.COLOR_TEXT, labelpad=8)
            ax.set_zlabel('Z', fontsize=11, fontweight='bold', color=self.COLOR_TEXT, labelpad=8)
            
            # Title
            ax.set_title(
                f'{title}',
                fontsize=16, fontweight='bold', color=self.COLOR_TITLE, pad=20
            )
            
            # Style 3D panes
            ax.xaxis.pane.fill = True
            ax.yaxis.pane.fill = True
            ax.zaxis.pane.fill = True
            ax.xaxis.pane.set_facecolor(self.COLOR_BG_PANEL)
            ax.yaxis.pane.set_facecolor(self.COLOR_BG_PANEL)
            ax.zaxis.pane.set_facecolor(self.COLOR_BG_PANEL)
            ax.xaxis.pane.set_edgecolor(self.COLOR_GRID)
            ax.yaxis.pane.set_edgecolor(self.COLOR_GRID)
            ax.zaxis.pane.set_edgecolor(self.COLOR_GRID)
            ax.xaxis.pane.set_alpha(0.9)
            ax.yaxis.pane.set_alpha(0.9)
            ax.zaxis.pane.set_alpha(0.9)
            ax.tick_params(colors=self.COLOR_TEXT, labelsize=9)
            
            # Hide tick labels for cleaner look
            ax.set_xticklabels([])
            ax.set_yticklabels([])
            ax.set_zticklabels([])
            
            # Parameter info box (top-left)
            param_text = (
                f'N = {N}\n'
                f'L = {L:.1f}\n'
                f'v₀ = {v0:.2f}\n'
                f'r = {r:.1f}\n'
                f'η = {eta:.2f}\n'
                f'ρ = {rho:.3f}'
            )
            ax.text2D(0.02, 0.98, param_text,
                     transform=ax.transAxes, fontsize=10, fontweight='bold',
                     color=self.COLOR_TEXT, ha='left', va='top',
                     alpha=0.9, family='monospace',
                     bbox=dict(boxstyle='round,pad=0.4', facecolor=self.COLOR_BG_PANEL,
                              edgecolor=self.COLOR_GRID, alpha=0.9))
            
            # Time and phi info (bottom center)
            info_text = f't = {time[idx]:.1f}  |  φ = {phi[idx]:.3f}'
            ax.text2D(0.5, 0.02, info_text,
                     transform=ax.transAxes, fontsize=12, fontweight='bold',
                     color=self.COLOR_ACCENT, ha='center', va='bottom',
                     alpha=0.95)
            
            fig.tight_layout()
            
            # Render to buffer
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=anim_dpi,
                       facecolor=self.COLOR_BG, edgecolor='none')
            buf.seek(0)
            frame_img = Image.open(buf).copy()
            
            # Add subtle glow effect
            frame_img = self._add_glow_effect(frame_img, intensity=1.2)
            
            frames.append(frame_img)
            buf.close()
            plt.close(fig)
        
        # Smooth playback
        frame_duration_ms = int(1000 / self.fps)
        
        print(f"      Saving GIF ({n_frames} frames)...")
        
        frames[0].save(
            str(filepath),
            save_all=True,
            append_images=frames[1:],
            duration=frame_duration_ms,
            loop=0,
            optimize=True,
            quality=85
        )
        
        print(f"      Done! Saved to {filepath.name}")
