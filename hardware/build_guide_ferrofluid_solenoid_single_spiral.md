Build Guide for Ferrofluid Solenoid with Single Spiral Copper



Date: July 28, 2025



Subject: Detailed Build Instructions for Ferrofluid Solenoid Setup



Overview and Functions

The solenoid setup uses a pre-wound air-core coil filled with ferrofluid to generate uniform axial magnetic fields for perturbations, with integrated electrodes for electrical measurements. Functions include magnetism/permeability testing via field strength (Hall sensors) and inductance (LCR meter), plus resistance/capacitance/permittivity/dielectricity via electrodes. It serves as a baseline for cross-calibration with ferrocell and toroid.



Components (from V2.4 BOM)

1 Air-Core Solenoid (Item 1).

Ferrofluid (shared from Item 2; ~60-100 ml).

2 Rubber Stoppers (Item 3).

Copper Foil Strips (Qty 2 from Item 4 for electrodes).

Epoxy Sealant (Already Owned; Item 10).

Syringe (Item 15).

Shared: Raspberry Pi 4 B+ (Already Owned; Item 6), Power Supply (Item 5), LCR Meter (Item 7), Hall Sensor (1 from Item 8), Breadboard/Jumpers (Already Owned; Item 9), etc.

Dependencies

Power: Shared DC supply for coil activation (1-5A).

Tools: Syringe for filling, epoxy for sealing.

Integration: Raspberry Pi for sensor readings.

Safety: Gloves for ferrofluid handling.

Order of Installation/Operations

Prepare Solenoid (Prep Phase): Inspect air-core solenoid (Item 1) for open ends and uniformity.

Insert Electrodes (Assembly Phase): Cut and insert copper foil strips (from Item 4) inside tube as parallel electrodes, with leads exiting ends. Secure with epoxy (Already Owned; Item 10) if needed.

Fill with Ferrofluid (Assembly Phase): Use syringe (Item 15) to inject ferrofluid (from Item 2) into tube, filling ~50-100% while avoiding bubbles.

Seal Ends (Assembly Phase): Plug ends with rubber stoppers (Item 3), seal with epoxy (Already Owned; Item 10) for leak-proofing. Cure for 1-2 hours.

Integrate Electronics (Integration Phase): Connect coil leads to power supply (Item 5) and electrode leads to breadboard (Already Owned; Item 9). Attach Hall sensor (from Item 8) near/inside tube. Wire to Raspberry Pi (Already Owned; Item 6) for control.

Test and Calibrate (Testing Phase): Apply current (e.g., 1A) via power supply, measure field with Hall sensor/LCR (Item 7), and test electrical properties. Calibrate against ferrocell/toroid.

Expected Build Time: 2-4 hours (excluding curing). Risks: Ferrofluid leaks (test seals), overheating coil (limit current).

