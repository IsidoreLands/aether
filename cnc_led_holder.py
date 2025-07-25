import svgwrite
import shared_config as cfg  # Import shared config
import matplotlib.pyplot as plt
import numpy as np

def generate_led_holder_svg(filename='led_holder_design.svg'):
    # Calculate rows/cols based on config
    effective_size = cfg.physical_size_mm - 2 * cfg.margin_mm
    rows = cols = int(effective_size / cfg.led_spacing_mm) + 1  # e.g., ~20 for 15mm spacing
    
    # Create SVG drawing
    dwg = svgwrite.Drawing(filename, profile='full', size=(f'{cfg.physical_size_mm + 2*cfg.margin_mm}mm', f'{cfg.physical_size_mm + 2*cfg.margin_mm}mm'))
    
    # Outer rectangle (material outline)
    dwg.add(dwg.rect(insert=(0, 0), size=(cfg.physical_size_mm + 2*cfg.margin_mm, cfg.physical_size_mm + 2*cfg.margin_mm), fill='none', stroke='black', stroke_width=1))
    
    # LED holes grid (centered with margins)
    start_x = cfg.margin_mm
    start_y = cfg.margin_mm
    for i in range(rows):
        for j in range(cols):
            cx = start_x + j * cfg.led_spacing_mm
            cy = start_y + i * cfg.led_spacing_mm
            dwg.add(dwg.circle(center=(cx, cy), r=cfg.led_diameter_mm / 2, fill='none', stroke='red', stroke_width=1))
    
    # Mounting holes and wiring cutouts (as before, but using config margins)
    mount_dia = 4
    dwg.add(dwg.circle(center=(cfg.margin_mm / 2, cfg.margin_mm / 2), r=mount_dia / 2, fill='none', stroke='blue', stroke_width=1))
    dwg.add(dwg.circle(center=(cfg.physical_size_mm + 1.5*cfg.margin_mm, cfg.margin_mm / 2), r=mount_dia / 2, fill='none', stroke='blue', stroke_width=1))
    dwg.add(dwg.circle(center=(cfg.margin_mm / 2, cfg.physical_size_mm + 1.5*cfg.margin_mm), r=mount_dia / 2, fill='none', stroke='blue', stroke_width=1))
    dwg.add(dwg.circle(center=(cfg.physical_size_mm + 1.5*cfg.margin_mm, cfg.physical_size_mm + 1.5*cfg.margin_mm), r=mount_dia / 2, fill='none', stroke='blue', stroke_width=1))
    
    slot_width = 10
    slot_height = 20
    dwg.add(dwg.rect(insert=((cfg.physical_size_mm + 2*cfg.margin_mm) / 2 - slot_width / 2, 0), size=(slot_width, slot_height), fill='none', stroke='green', stroke_width=1))
    dwg.add(dwg.rect(insert=((cfg.physical_size_mm + 2*cfg.margin_mm) / 2 - slot_width / 2, cfg.physical_size_mm + 2*cfg.margin_mm - slot_height), size=(slot_width, slot_height), fill='none', stroke='green', stroke_width=1))
    
    dwg.save()
    print(f'SVG file "{filename}" generated for CNC LED holder using shared config.')

def generate_led_holder_png(filename='led_holder_visual.png'):
    # Calculate rows/cols based on shared config (if using; otherwise hardcode as in your script)
    # Assuming vars from generate_led_holder_svg: rows, cols, led_diameter, led_spacing, material_size, margin
    # For standalone: Define them here if not global
    rows = cols = 20  # Example; replace with your calculation
    led_diameter = 5
    led_spacing = 15
    material_size = 400
    margin = 50
    
    # Setup plot canvas (mirroring kepler style)
    fig, ax = plt.subplots(figsize=(9, 9))
    ax.set_xlim(0, material_size)
    ax.set_ylim(0, material_size)
    ax.set_aspect('equal')
    ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.5, color='gray')

    # Outer rectangle (black stroke)
    ax.add_patch(plt.Rectangle((0, 0), material_size, material_size, fill=None, edgecolor='black', linewidth=1))

    # LED holes grid (red circles)
    start_x = margin
    start_y = margin
    for i in range(rows):
        for j in range(cols):
            cx = start_x + j * led_spacing
            cy = start_y + i * led_spacing
            ax.add_patch(plt.Circle((cx, cy), led_diameter / 2, fill=None, edgecolor='red', linewidth=1))

    # Mounting holes (blue circles)
    mount_dia = 4
    ax.add_patch(plt.Circle((margin / 2, margin / 2), mount_dia / 2, fill=None, edgecolor='blue', linewidth=1))
    ax.add_patch(plt.Circle((material_size - margin / 2, margin / 2), mount_dia / 2, fill=None, edgecolor='blue', linewidth=1))
    ax.add_patch(plt.Circle((margin / 2, material_size - margin / 2), mount_dia / 2, fill=None, edgecolor='blue', linewidth=1))
    ax.add_patch(plt.Circle((material_size - margin / 2, material_size - margin / 2), mount_dia / 2, fill=None, edgecolor='blue', linewidth=1))

    # Wiring cutouts (green rectangles)
    slot_width = 10
    slot_height = 20
    ax.add_patch(plt.Rectangle((material_size / 2 - slot_width / 2, 0), slot_width, slot_height, fill=None, edgecolor='green', linewidth=1))
    ax.add_patch(plt.Rectangle((material_size / 2 - slot_width / 2, material_size - slot_height), slot_width, slot_height, fill=None, edgecolor='green', linewidth=1))

    # Legend and title (mirroring kepler)
    ax.legend(handles=[
        plt.Line2D([0], [0], color='red', lw=2, label='LED Holes'),
        plt.Line2D([0], [0], color='blue', lw=2, label='Mounting Holes'),
        plt.Line2D([0], [0], color='green', lw=2, label='Wiring Cutouts')
    ], loc='upper right')
    ax.set_title('LED Holder Design Visual\n(Mirrored Style to Kepler Grid, Units in mm)')

    # Save as PNG
    plt.savefig(filename, dpi=300)
    plt.show()
    print(f'PNG file "{filename}" generated for LED holder visual.')

# Call both functions in main (add this at the end of your script)
if __name__ == '__main__':
    generate_led_holder_svg()
    generate_led_holder_png()