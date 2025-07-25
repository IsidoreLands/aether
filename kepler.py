import matplotlib.pyplot as plt
import numpy as np
import shared_config as cfg  # Import shared config

def get_line(start, end):
    """Bresenham's Line Algorithm"""
    x1, y1 = start
    x2, y2 = end
    dx = x2 - x1
    dy = y2 - y1
    is_steep = abs(dy) > abs(dx)
    if is_steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2
    swapped = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        swapped = True
    dx = x2 - x1
    dy = abs(y2 - y1)
    error = int(dx / 2.0)
    ystep = 1 if y1 < y2 else -1
    y = y1
    points = []
    for x in range(x1, x2 + 1):
        coord = (y, x) if is_steep else (x, y)
        points.append(coord)
        error -= dy
        if error < 0:
            y += ystep
            error += dx
    if swapped:
        points.reverse()
    return points

class KeplerGrid:
    def __init__(self, max_depth=5):
        self.max_depth = max_depth
        self.size = cfg.grid_size  # From shared config
        self.pad_offset = int((cfg.margin_mm / cfg.physical_size_mm) * self.size)  # Scale margin to units (e.g., ~50 units for 50mm)
        self.axis_pad = self.pad_offset + 20
        
        # --- Physical Properties ---
        phi = (1 + np.sqrt(5)) / 2
        sqrt_phi = np.sqrt(phi)
        self.long_leg = self.size - 1
        self.short_leg = int(np.round(self.long_leg / sqrt_phi))

        # --- Grid & Pad Coordinates for Bottom-Left Triangle ---
        self.point_a = np.array([0, 0])
        self.point_b = np.array([self.short_leg, 0])
        self.point_c = np.array([0, self.long_leg])
        self.pad_a = np.array([self.point_a[0], -self.pad_offset])
        self.pad_b = np.array([self.point_b[0], -self.pad_offset])
        self.pad_c = np.array([-self.pad_offset, self.point_c[1]])

        # --- Grid & Pad Coordinates for Mirrored Top-Right Triangle ---
        self.point_d = np.array([self.size - 1, self.size - 1])
        self.point_e = np.array([self.size - 1 - self.short_leg, self.size - 1])
        self.point_f = np.array([self.size - 1, self.size - 1 - self.long_leg])
        self.pad_d = np.array([self.point_d[0], self.size - 1 + self.pad_offset])
        self.pad_e = np.array([self.point_e[0], self.size - 1 + self.pad_offset])
        self.pad_f = np.array([self.size - 1 + self.pad_offset, self.point_f[1]])

    def draw_kepler(self, lines, p1, p2, p3, depth):
        if depth > self.max_depth:
            return
        lines.append((p1, p2))
        lines.append((p1, p3))
        lines.append((p2, p3))
        if depth == self.max_depth:
            return
        short = np.linalg.norm(p2 - p1)
        if short < 1e-6:  # Avoid degenerate cases
            return
        hyp = np.linalg.norm(p3 - p2)
        BD = short ** 2 / hyp
        v = p3 - p2
        unit_v = v / hyp
        D = p2 + unit_v * BD
        self.draw_kepler(lines, D, p2, p1, depth + 1)
        self.draw_kepler(lines, D, p3, p1, depth + 1)

    def generate_lines(self):
        """Generates the lines for the Kepler meshes only."""
        lines = []
        # Original triangle
        self.draw_kepler(lines, self.point_a, self.point_b, self.point_c, 0)
        # Mirrored triangle
        self.draw_kepler(lines, self.point_d, self.point_e, self.point_f, 0)
        return lines

    def generate_grid_array(self):
        """Generates the NumPy array for the Kepler meshes only."""
        grid = np.zeros((self.size, self.size))
        lines = self.generate_lines()
        for line in lines:
            p1, p2 = line
            points = get_line((int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])))
            for px, py in points:
                if 0 <= px < self.size and 0 <= py < self.size:
                    grid[py, px] = 1.0
        return grid

    def generate_plot(self):
        """Generates the full plot including grids, pads, and breakers."""
        kepler_lines = self.generate_lines()
        
        # --- Setup Plot Canvas ---
        fig, ax = plt.subplots(figsize=(9, 9))
        ax.set_xlim(-self.axis_pad, self.size + self.axis_pad)
        ax.set_ylim(-self.axis_pad, self.size + self.axis_pad)
        ax.set_aspect('equal')
        ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.5, color='gray')  # Reference grid in gray

        # --- Plot Kepler Grids (copper in red for visual diff) ---
        for line in kepler_lines:
            p1, p2 = line
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], 'r-', linewidth=1.5)  # Copper color

        # --- Plot Connections & Breakers for Bottom-Left Grid (redundant paths) ---
        # A (dual paths with curve approx)
        ax.plot([self.point_a[0], self.pad_a[0] - 10, self.pad_a[0]], [self.point_a[1], self.pad_a[1] + 30, self.pad_a[1] + 20], 'r-', linewidth=1.5)  # Redundant path 1
        ax.plot([self.point_a[0] + 5, self.pad_a[0] + 10, self.pad_a[0]], [self.point_a[1] - 5, self.pad_a[1] + 25, self.pad_a[1] + 20], 'r-', linewidth=1.5)  # Redundant path 2
        ax.plot([self.pad_a[0] - 10, self.pad_a[0] + 10, self.pad_a[0] - 10, self.pad_a[0] + 10, self.pad_a[0]],
                [self.pad_a[1] + 20, self.pad_a[1] + 15, self.pad_a[1] + 10, self.pad_a[1] + 5, self.pad_a[1]], 'r-', linewidth=0.5)  # Breaker
        ax.text(self.pad_a[0] + 20, self.pad_a[1], 'Breaker A (0.15mm fuse)', fontsize=8, color='blue')  # Reference label
        
        # B (similar)
        ax.plot([self.point_b[0], self.pad_b[0] - 10, self.pad_b[0]], [self.point_b[1], self.pad_b[1] + 30, self.pad_b[1] + 20], 'r-', linewidth=1.5)
        ax.plot([self.point_b[0] - 5, self.pad_b[0] + 10, self.pad_b[0]], [self.point_b[1] - 5, self.pad_b[1] + 25, self.pad_b[1] + 20], 'r-', linewidth=1.5)
        ax.plot([self.pad_b[0] - 10, self.pad_b[0] + 10, self.pad_b[0] - 10, self.pad_b[0] + 10, self.pad_b[0]],
                [self.pad_b[1] + 20, self.pad_b[1] + 15, self.pad_b[1] + 10, self.pad_b[1] + 5, self.pad_b[1]], 'r-', linewidth=0.5)
        ax.text(self.pad_b[0] + 20, self.pad_b[1], 'Breaker B (0.15mm fuse)', fontsize=8, color='blue')
        
        # C
        ax.plot([self.point_c[0], self.pad_c[0] + 30, self.pad_c[0] + 20], [self.point_c[1], self.pad_c[1] - 10, self.pad_c[1]], 'r-', linewidth=1.5)
        ax.plot([self.point_c[0] - 5, self.pad_c[0] + 25, self.pad_c[0] + 20], [self.point_c[1] + 5, self.pad_c[1] + 10, self.pad_c[1]], 'r-', linewidth=1.5)
        ax.plot([self.pad_c[0] + 20, self.pad_c[0] + 15, self.pad_c[0] + 10, self.pad_c[0] + 5, self.pad_c[0]],
                [self.pad_c[1] - 10, self.pad_c[1] + 10, self.pad_c[1] - 10, self.pad_c[1] + 10, self.pad_c[1]], 'r-', linewidth=0.5)
        ax.text(self.pad_c[0], self.pad_c[1] + 20, 'Breaker C (0.15mm fuse)', fontsize=8, color='blue')

        # --- Plot Connections & Breakers for Top-Right Grid (similar redundancy) ---
        # D
        ax.plot([self.point_d[0], self.pad_d[0] - 10, self.pad_d[0]], [self.point_d[1], self.pad_d[1] - 30, self.pad_d[1] - 20], 'r-', linewidth=1.5)
        ax.plot([self.point_d[0] + 5, self.pad_d[0] + 10, self.pad_d[0]], [self.point_d[1] + 5, self.pad_d[1] - 25, self.pad_d[1] - 20], 'r-', linewidth=1.5)
        ax.plot([self.pad_d[0] - 10, self.pad_d[0] + 10, self.pad_d[0] - 10, self.pad_d[0] + 10, self.pad_d[0]],
                [self.pad_d[1] - 20, self.pad_d[1] - 15, self.pad_d[1] - 10, self.pad_d[1] - 5, self.pad_d[1]], 'r-', linewidth=0.5)
        ax.text(self.pad_d[0] + 20, self.pad_d[1], 'Breaker D (0.15mm fuse)', fontsize=8, color='blue')
        
        # E
        ax.plot([self.point_e[0], self.pad_e[0] - 10, self.pad_e[0]], [self.point_e[1], self.pad_e[1] - 30, self.pad_e[1] - 20], 'r-', linewidth=1.5)
        ax.plot([self.point_e[0] - 5, self.pad_e[0] + 10, self.pad_e[0]], [self.point_e[1] + 5, self.pad_e[1] - 25, self.pad_e[1] - 20], 'r-', linewidth=1.5)
        ax.plot([self.pad_e[0] - 10, self.pad_e[0] + 10, self.pad_e[0] - 10, self.pad_e[0] + 10, self.pad_e[0]],
                [self.pad_e[1] - 20, self.pad_e[1] - 15, self.pad_e[1] - 10, self.pad_e[1] - 5, self.pad_e[1]], 'r-', linewidth=0.5)
        ax.text(self.pad_e[0] + 20, self.pad_e[1], 'Breaker E (0.15mm fuse)', fontsize=8, color='blue')
        
        # F
        ax.plot([self.point_f[0], self.pad_f[0] - 30, self.pad_f[0] - 20], [self.point_f[1], self.pad_f[1] - 10, self.pad_f[1]], 'r-', linewidth=1.5)
        ax.plot([self.point_f[0] + 5, self.pad_f[0] - 25, self.pad_f[0] - 20], [self.point_f[1] + 5, self.pad_f[1] + 10, self.pad_f[1]], 'r-', linewidth=1.5)
        ax.plot([self.pad_f[0] - 20, self.pad_f[0] - 15, self.pad_f[0] - 10, self.pad_f[0] - 5, self.pad_f[0]],
                [self.pad_f[1] - 10, self.pad_f[1] + 10, self.pad_f[1] - 10, self.pad_f[1] + 10, self.pad_f[1]], 'r-', linewidth=0.5)
        ax.text(self.pad_f[0], self.pad_f[1] + 20, 'Breaker F (0.15mm fuse)', fontsize=8, color='blue')

        # --- Optional Ground Trace (external routing between grids for safety) ---
        ground_mid_bottom = np.array([self.size / 2, -self.pad_offset])
        ground_mid_top = np.array([self.size / 2, self.size + self.pad_offset])
        ax.plot([ground_mid_bottom[0] - 20, ground_mid_bottom[0] + 20], [ground_mid_bottom[1], ground_mid_bottom[1]], 'r--', linewidth=1.5, label='Optional Ground Trace')
        ax.plot([ground_mid_top[0] - 20, ground_mid_top[0] + 20], [ground_mid_top[1], ground_mid_top[1]], 'r--', linewidth=1.5)

        # --- Mark all 6 External Solder Pads ---
        all_pads_x = [self.pad_a[0], self.pad_b[0], self.pad_c[0], self.pad_d[0], self.pad_e[0], self.pad_f[0]]
        all_pads_y = [self.pad_a[1], self.pad_b[1], self.pad_c[1], self.pad_d[1], self.pad_e[1], self.pad_f[1]]
        ax.scatter(all_pads_x, all_pads_y, color='green', s=100, label='External Solder Pads', zorder=5)  # Green for pads in visual

        # --- Final Touches ---
        ax.set_title('Mirrored Kepler Grids on 1000 × 1000 Units (12" × 12" Acrylic)\nwith Enhanced Safety, Reliability, and Efficiency Features\n(Insulate Traces; Use Non-Toxic Etching with Ventilation)')
        
        # Save full visual SVG/PNG (with colors for reference)
        plt.savefig('kepler_full_visual.png', dpi=300)
        plt.savefig('kepler_full_visual.svg', format='svg')
        
        # Save copper-only SVG (black lines, no colors/labels for direct KiCAD import to F.Cu)
        copper_fig, copper_ax = plt.subplots(figsize=(9, 9))
        copper_ax.set_xlim(-self.axis_pad, self.size + self.axis_pad)
        copper_ax.set_ylim(-self.axis_pad, self.size + self.axis_pad)
        copper_ax.set_aspect('equal')
        copper_ax.axis('off')  # No reference grid
        for line in kepler_lines:
            p1, p2 = line
            copper_ax.plot([p1[0], p2[0]], [p1[1], p2[1]], 'k-', linewidth=1.5)
        # Add extensions and breakers in black (omit labels/grounds as non-copper)
        # Repeat plotting for A-F extensions/breakers here without text or colors
        copper_ax.plot([self.point_a[0], self.pad_a[0] - 10, self.pad_a[0]], [self.point_a[1], self.pad_a[1] + 30, self.pad_a[1] + 20], 'k-', linewidth=1.5)
        copper_ax.plot([self.point_a[0] + 5, self.pad_a[0] + 10, self.pad_a[0]], [self.point_a[1] - 5, self.pad_a[1] + 25, self.pad_a[1] + 20], 'k-', linewidth=1.5)
        copper_ax.plot([self.pad_a[0] - 10, self.pad_a[0] + 10, self.pad_a[0] - 10, self.pad_a[0] + 10, self.pad_a[0]],
                       [self.pad_a[1] + 20, self.pad_a[1] + 15, self.pad_a[1] + 10, self.pad_a[1] + 5, self.pad_a[1]], 'k-', linewidth=0.5)
        # ... (repeat for B, C, D, E, F similarly)
        copper_fig.savefig('kepler_copper_only.svg', format='svg')
        plt.close(copper_fig)  # Close copper fig
        
        plt.show()

        # Save rasterized grid for reference/simulation mirroring
        grid_array = self.generate_grid_array()
        np.savez('kepler_grid_final.npz', grid=grid_array)

# --- Main Execution ---
if __name__ == '__main__':
    grid = KeplerGrid(max_depth=5)
    grid.generate_plot()