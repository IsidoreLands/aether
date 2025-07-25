import matplotlib.pyplot as plt
import numpy as np

def get_line(start, end):
    """Bresenham's Line Algorithm - General version.
    Produces a list of tuples (x, y) from start to end."""
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
    def __init__(self, max_depth=5, size=1000):
        self.max_depth = max_depth
        self.size = size
        # Placeholder properties (customize based on materials/copper specs)
        self.resistance = 0.1  # Ohms (example; calculate as rho * total_length / (width * thickness))
        self.capacitance = 10e-12  # Farads (parasitic; low for DC control)
        self.permeability = 1.0  # Relative (≈1 for copper; ferrofluid 2-5)
        self.magnetism = 'Paramagnetic'  # Ferrofluid property
        self.permittivity = 3.0  # Relative (acrylic ≈2.5-3.5)
        self.dielectricity = 'Low loss'  # Qualitative for insulation
        phi = (1 + np.sqrt(5)) / 2
        sqrt_phi = np.sqrt(phi)
        self.long_leg = self.size - 1
        self.short_leg = int(np.round(self.long_leg / sqrt_phi))
        self.point_a = np.array([0, 0])      # Right angle (connection pad)
        self.point_b = np.array([self.short_leg, 0])    # Short leg end (connection pad)
        self.point_c = np.array([0, self.long_leg])   # Long leg end (connection pad)

    def draw_kepler(self, lines, p1, p2, p3, depth):
        if depth > self.max_depth:
            return
        lines.append((p1, p2))
        lines.append((p1, p3))
        lines.append((p2, p3))
        if depth == self.max_depth:
            return
        short = np.linalg.norm(p2 - p1)
        hyp = np.linalg.norm(p3 - p2)
        BD = short ** 2 / hyp
        v = p3 - p2
        unit_v = v / hyp
        D = p2 + unit_v * BD
        self.draw_kepler(lines, D, p2, p1, depth + 1)
        self.draw_kepler(lines, D, p3, p1, depth + 1)

    def generate_lines(self):
        lines = []
        self.draw_kepler(lines, self.point_a, self.point_b, self.point_c, 0)
        return lines

    def generate_grid_array(self):
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
        lines = self.generate_lines()
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.set_xlim(0, self.size)
        ax.set_ylim(0, self.size)
        ax.set_aspect('equal')
        ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.5)
        
        # Plot the grid lines
        for line in lines:
            p1, p2 = line
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], 'k-', linewidth=1)
        
        # Mark connection points (pads)
        ax.scatter([self.point_a[0], self.point_b[0], self.point_c[0]], [self.point_a[1], self.point_b[1], self.point_c[1]], color='r', s=100, label='Solder Pads')
        
        ax.legend(loc='upper right')
        ax.set_title('Recursive Kepler Grid on 1000 × 1000 Units\n(Scaled to 12" × 12" Acrylic for Ferrofluid Control)')
        
        plt.savefig('kepler_grid.png')
        plt.savefig('kepler_grid.svg', format='svg')
        plt.show()

        # Save rasterized grid for reference/simulation mirroring
        grid_array = self.generate_grid_array()
        np.savez('kepler_grid.npz', grid=grid_array)

# Usage
if __name__ == '__main__':
    grid = KeplerGrid(max_depth=5)  # Adjust depth for grid density
    grid.generate_plot()
