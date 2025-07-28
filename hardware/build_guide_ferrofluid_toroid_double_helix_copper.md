Build Guide for Ferrofluid Toroid with Double Helix Copper



Date: July 28, 2025



Subject: Detailed Build Instructions for Ferrofluid Toroid Setup



Overview and Functions

The toroid setup forms a closed-loop tube filled with ferrofluid, wrapped in a double helix coil for confined multipole magnetic fields. Electrodes enable electrical measurements. Functions include advanced magnetism/permeability via tunable fields (Hall sensors/inductance) and resistance/capacitance/permittivity/dielectricity, with circulatory ferrofluid for dynamic perturbations. It complements solenoid's axial fields and ferrocell's optics for full calibration.



Components (from V2.4 BOM)

1 Silicone Tubing (Item 16).

2 Enameled Copper Wire Spools (Item 17).

2 Barbed Tube Fittings (Item 18).

Ferrofluid (shared from Item 2; ~50-100 ml).

Copper Foil Strips (Qty 2 from Item 4 for electrodes).

Epoxy Sealant (Already Owned; Item 10).

Syringe (Item 15).

Shared: Raspberry Pi 4 B+ (Already Owned; Item 6), Power Supply (Item 5), LCR Meter (Item 7), Hall Sensor (1 from Item 8), Breadboard/Jumpers (Already Owned; Item 9), etc.

Dependencies

Tools: Wire cutters (Item 12), pliers for bending tubing.

Power: Shared DC supply for coil (1-3A per helix).

Integration: Raspberry Pi for control.

Safety: Gloves for ferrofluid/wire handling.

Order of Installation/Operations

Form Toroid (Prep Phase): Cut silicone tubing (Item 16) to length (~1-2m), bend into circular loop (10-20 cm diameter).

Insert Electrodes and Connect (Assembly Phase): Thread copper foil strips (from Item 4) inside tubing as electrodes, with leads exiting. Connect ends with barbed fittings (Item 18), seal joints with epoxy (Already Owned; Item 10).

Fill with Ferrofluid (Assembly Phase): Use syringe (Item 15) to inject ferrofluid (from Item 2) into loop, filling ~50-100% while expelling air. Seal fully.

Wind Double Helix Coil (Fabrication Phase): Use enameled wire spools (Item 17) to wind two intertwined helices around toroid (100-200 turns each, one clockwise/one counterclockwise for multipole effects). Secure with tape or epoxy.

Integrate Electronics (Integration Phase): Connect coil leads to power supply (Item 5) and electrode leads to breadboard (Already Owned; Item 9). Place Hall sensor (from Item 8) near tube. Wire to Raspberry Pi (Already Owned; Item 6).

Test and Calibrate (Testing Phase): Apply currents (e.g., opposing for dipole fields), measure with LCR (Item 7) and Hall sensor. Calibrate against solenoid/ferrocell.

Expected Build Time: 4-6 hours. Risks: Uneven winding (use jig if possible), leaks at fittings (test pressure).

