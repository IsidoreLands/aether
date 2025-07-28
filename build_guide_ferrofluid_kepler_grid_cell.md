Build Guide for Ferrocell with Kepler Triangle Copper Grid



Date: July 28, 2025



Subject: Detailed Build Instructions for Ferrocell Setup



Overview and Functions

The ferrocell setup consists of a thin layer of ferrofluid sandwiched between two acrylic plates, with a custom-etched Kepler triangle copper grid for electrical measurements (resistance, capacitance, permittivity, dielectricity), an LED matrix array for wavelength-shifting backlighting (e.g., blue-red for enhanced magneto-optical contrast), and a camera for capturing patterns to analyze magnetism and permeability. The Kepler triangle grid (based on golden ratio proportions) provides a structured electrode array for uniform field distribution. This setup functions as a magneto-optical visualizer and electrical probe, allowing perturbations via applied voltages/currents and optical/electrical outputs for cross-calibration with solenoid and toroid setups.



Components (from V2.4 BOM)

2 Clear Acrylic Sheets (20x20" x 1/8" thick; Item 19).

1 Copper Clad FR4 PCB Board (18x18"; Item 20).

Ferrofluid (shared from Item 2; ~10-20 ml for thin layer).

1 pack WS2812B LED Matrix Panel (~18x18" coverage; Item 21).

1 Arducam Camera Module (Item 22).

1 pack Photo Paper for Toner Transfer (Item 23).

1 Ferric Chloride PCB Etchant (Item 24).

Hobby Mini Drill Press (Already Owned; Item 25).

4 Photoresistor Modules (Already Owned; Item 26).

1 pack Spacers/Stand-offs (Item 27).

Epoxy Sealant (Already Owned; Item 10).

Copper Foil Strips (Qty 2 from Item 4 for additional solder points).

Shared: Raspberry Pi 4 B+ (Already Owned; Item 6), Power Supply (Item 5), Breadboard/Jumpers (Already Owned; Item 9), etc.

Dependencies

Software: Design tool (e.g., KiCad or Inkscape) for Kepler triangle grid pattern (triangular lattice with sides in golden ratio ~1:1.618).

External Service: Staples for printing grid on photo paper.

Safety Gear: Gloves, ventilation (for etchant), eye protection (for drilling).

Power: Shared DC supply for LEDs/camera.

Integration: Raspberry Pi for camera control and data logging.

Order of Installation/Operations

Design and Print Grid (Prep Phase): Create Kepler triangle grid pattern (18x18") digitally, ensuring external solder points around edges. Print at Staples on photo paper (Item 23) using toner-based printer for transfer.

Etch Copper Grid (Fabrication Phase): Apply toner transfer to copper clad board (Item 20): Iron printed pattern onto board, etch with ferric chloride (Item 24) in a ventilated area (~30-60 min), rinse, and drill vias/holes if needed for connections. Clean and test continuity.

Prepare LED Holder (Fabrication Phase): Use drill press (Already Owned; Item 25) to drill holes in one acrylic sheet (Item 19) or separate board for LED matrix placement (Item 21). Space holes to match LED array for uniform backlighting.

Assemble Ferrocell (Assembly Phase): Place spacers (Item 27) on bottom acrylic sheet. Position etched grid on top, add copper foil strips (from Item 4) for solder points. Inject ferrofluid (from Item 2) evenly (~0.1-0.5 mm layer). Seal top sheet with epoxy (Already Owned; Item 10). Cure for 24 hours.

Integrate Electronics (Integration Phase): Mount LED matrix behind holder, connect to power supply (Item 5) and Raspberry Pi GPIO (Already Owned; Item 6) for control. Attach camera (Item 22) above ferrocell. Wire photoresistors (Already Owned; Item 26) around edges for light detection. Connect grid solder points to breadboard (Already Owned; Item 9) for electrical inputs.

Test and Calibrate (Testing Phase): Power on LEDs for backlighting, apply test voltages via power supply, capture images with camera, and measure outputs using LCR meter (Item 7) and Hall sensors (Item 8). Calibrate against solenoid/toroid data.

Expected Build Time: 8-12 hours (excluding curing/etching wait times). Risks: Etchant spills (use tray), uneven ferrofluid distribution (use syringe carefully).

