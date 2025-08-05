import svgwrite
import shared_config as cfg  # Import shared config
import matplotlib.pyplot as plt
import numpy as np

def generate_led_holder_svg(filename='led_holder_design.svg'):
    # Calculate rows/cols based on config
    effective_size = cfg.physical_size_mm  # Grid size for LED coverage
    rows = cols = int(effective_size / cfg.led_spacing_mm) + 1  # e.g., ~30 for 15mm spacing on 457.2mm
    
    full_size = cfg.physical_size_mm + 2 * cfg.margin_mm  # Total plate size (20" = 508mm)
    
    # Create SVG drawing
    dwg = svgwrite.Drawing(filename, profile='full', size=(f'{full_size}mm', f'{full_size}mm'))
    
    # Outer rectangle (material outline)
    dwg.add(dwg.rect(insert=(0, 0), size=(full_size, full_size), fill='none', stroke='black', stroke_width=1))
    
    # LED holes grid (centered with margins)
    start_x = cfg.margin_mm
    start_y = cfg.margin_mm
    for i in range(rows):
        for j in range(cols):
            cx = start_x + j * cfg.led_spacing_mm
            cy = start_y + i * cfg.led_spacing_mm
            dwg.add(dwg.circle(center=(cx, cy), r=cfg.led_diameter_mm / 2, fill='none', stroke='red', stroke_width=1))
    
    # Mounting holes and wiring cutouts (as before)
    mount_dia = 4
    dwg.add(dwg.circle(center=(cfg.margin_mm / 2, cfg.margin_mm / 2), r=mount_dia / 2, fill='none', stroke='blue', stroke_width=1))
    dwg.add(dwg.circle(center=(full_size - cfg.margin_mm / 2, cfg.margin_mm / 2), r=mount_dia / 2, fill='none', stroke='blue', stroke_width=1))
    dwg.add(dwg.circle(center=(cfg.margin_mm / 2, full_size - cfg.margin_mm / 2), r=mount_dia / 2, fill='none', stroke='blue', stroke_width=1))
    dwg.add(dwg.circle(center=(full_size - cfg.margin_mm / 2, full_size - cfg.margin_mm / 2), r=mount_dia / 2, fill='none', stroke='blue', stroke_width=1))
    
    slot_width = 10
    slot_height = 20
    dwg.add(dwg.rect(insert=((full_size) / 2 - slot_width / 2, 0), size=(slot_width, slot_height), fill='none', stroke='green', stroke_width=1))
    dwg.add(dwg.rect(insert=((full_size) / 2 - slot_width / 2, full_size - slot_height), size=(slot_width, slot_height), fill='none', stroke='green', stroke_width=1))
    
    dwg.save()
    print(f'SVG file "{filename}" generated for CNC LED holder using shared config.')

def generate_led_holder_png(filename='led_holder_visual.png'):
    effective_size = cfg.physical_size_mm  # Grid size for LED coverage
    rows = cols = int(effective_size / cfg.led_spacing_mm) + 1
    full_size = cfg.physical_size_mm + 2 * cfg.margin_mm  # Total plate size
    
    fig, ax = plt.subplots(figsize=(9, 9))
    ax.set_xlim(0, full_size)
    ax.set_ylim(0, full_size)
    ax.set_aspect('equal')
    ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.5, color='gray')

    ax.add_patch(plt.Rectangle((0, 0), full_size, full_size, fill=None, edgecolor='black', linewidth=1))

    start_x = cfg.margin_mm
    start_y = cfg.margin_mm
    for i in range(rows):
        for j in range(cols):
            cx = start_x + j * cfg.led_spacing_mm
            cy = start_y + i * cfg.led_spacing_mm
            ax.add_patch(plt.Circle((cx, cy), cfg.led_diameter_mm / 2, fill=None, edgecolor='red', linewidth=1))

    mount_dia = 4
    ax.add_patch(plt.Circle((cfg.margin_mm / 2, cfg.margin_mm / 2), mount_dia / 2, fill=None, edgecolor='blue', linewidth=1))
    ax.add_patch(plt.Circle((full_size - cfg.margin_mm / 2, cfg.margin_mm / 2), mount_dia / 2, fill=None, edgecolor='blue', linewidth=1))
    ax.add_patch(plt.Circle((cfg.margin_mm / 2, full_size - cfg.margin_mm / 2), mount_dia / 2, fill=None, edgecolor='blue', linewidth=1))
    ax.add_patch(plt.Circle((full_size - cfg.margin_mm / 2, full_size - cfg.margin_mm / 2), mount_dia / 2, fill=None, edgecolor='blue', linewidth=1))

    slot_width = 10
    slot_height = 20
    ax.add_patch(plt.Rectangle((full_size / 2 - slot_width / 2, 0), slot_width, slot_height, fill=None, edgecolor='green', linewidth=1))
    ax.add_patch(plt.Rectangle((full_size / 2 - slot_width / 2, full_size - slot_height), slot_width, slot_height, fill=None, edgecolor='green', linewidth=1))

    ax.legend(handles=[
        plt.Line2D([0], [0], color='red', lw=2, label='LED Holes'),
        plt.Line2D([0], [0], color='blue', lw=2, label='Mounting Holes'),
        plt.Line2D([0], [0], color='green', lw=2, label='Wiring Cutouts')
    ], loc='upper left', bbox_to_anchor=(1.05, 1), borderaxespad=0.)

    ax.set_title('LED Holder Design Visual\n(Matched to 18" Kepler Grid, Units in mm)')

    plt.savefig(filename, dpi=300)
    plt.close()
    print(f'PNG file "{filename}" generated for LED holder visual.')

if __name__ == '__main__':
    generate_led_holder_svg()
    generate_led_holder_png()