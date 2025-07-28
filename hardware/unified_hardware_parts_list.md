Unified Parts List V1.0 for Raspberry Pi AI Server and Ferrofluid Setups



This V1.0 unifies the locked V4 Raspberry Pi AI server list with the provided V2.5 Ferrofluid Solenoid, Toroidal Tube, and Ferrocell Setups BOM. Items are grouped into categories for clarity (AI Server Core, Shared Power/Connectivity/Tools, Ferrofluid Specific, Scalability Add-Ons, Optional/Advanced). Overlaps (e.g., Raspberry Pi 4 B+ owned, breadboard/jumpers from Elegoo, DC power supply) are merged as unique entries with cross-references. Ownership reflects your inventory (e.g., Elegoo for resistors/breadboard, docks for connectivity, abundant cables). Prices updated from 2025 sources (web searches; averages used, e.g., Amazon/eBay/Arbor). Sub-notes follow V4 format.



Total estimated cost for non-owned: ~$600-750 (AI server ~$340, ferrofluid ~$260; bundles save ~$100).



AI Server Core Components



Raspberry Pi 5 Board (16GB RAM Variant)

Quantity Needed: 1 (base; scale to 2+ for clusters).

Quality/Dependency Requirements: Official Raspberry Pi board; ARM64 architecture, compatible with Ubuntu 24.04+ and Hailo AI Kit; requires MicroSD/USB boot.

Brief Description of Use/Function: Main single-board computer for AI processing, running OCR agents, clustering, and inference tasks; 16GB RAM for multi-tasking LLMs/agents.

Estimated Lifecycle: 5-7 years (durable, but tech advances may obsolete in 3-5 for cutting-edge AI).

Price: $120.

Owned: No.



Raspberry Pi AI Kit (with Hailo-8L Accelerator)

Quantity Needed: 1 (per Pi 5; add for clusters).

Quality/Dependency Requirements: Official kit; M.2 HAT+ with Hailo-8L (13 TOPS); requires Pi 5 PCIe slot and compatible OS (Ubuntu/Raspberry Pi OS).

Brief Description of Use/Function: Accelerates neural networks for efficient OCR/math equation processing and future AI research (e.g., inference at 1-2s/page).

Estimated Lifecycle: 4-6 years (AI chips evolve quickly; firmware updates extend).

Price: $70.

Owned: No.



Raspberry Pi 4 Model B+ (as Controller Substitute)

Quantity Needed: 1 (shared for ferrofluid data acquisition).

Quality/Dependency Requirements: 1.5GHz quad-core, 1GB+ RAM; GPIO for sensors, compatible with Arduino shields via adapters.

Brief Description of Use/Function: Central controller for sensor data/logging in ferrofluid setups; offloads from Pi 5 in hybrid AI/ferrofluid rig.

Estimated Lifecycle: 4-6 years (reliable for I/O tasks).

Price: $0 (owned).

Owned: Yes (your Pi 4 B+).



Shared Power/Connectivity/Tools



Adjustable DC Power Supply (0-12V, 5A Output)

Quantity Needed: 1 (shared across AI/ferrofluid).

Quality/Dependency Requirements: Variable 0-12V DC, 5A max; stable for coils/electrodes/LEDs.

Brief Description of Use/Function: Powers coils, electrodes, LEDs for magnetic/electrical perturbations in ferrofluid; DC for AI peripherals if needed.

Estimated Lifecycle: 5-7 years (robust electronics).

Price: $20.

Owned: No.



Official 27W USB-C Power Supply (PoE-Enabled Variant for Clusters)

Quantity Needed: 1 (per Pi; PoE HAT optional for networking).

Quality/Dependency Requirements: Official Raspberry Pi PD supply; 5V/5A stable, PoE support for clustered power over Ethernet.

Brief Description of Use/Function: Provides reliable power for Pi 5/AI Kit under high loads; PoE enables cable-free clustering in production setups.

Estimated Lifecycle: 5-7 years (robust; overvoltage protection).

Price: $15-35.

Owned: Partially (laptop chargers/adapters may substitute if 27W+ USB-C; test for stability—XP400 UPS/PV375 inverter/solar controller enhance).



UPS/Battery HAT or Adapter (Scalable for Multi-Pi)

Quantity Needed: 1 (system-wide; expandable).

Quality/Dependency Requirements: GPIO-stacking HAT with LiPo/18650 support or equivalent; seamless switching, >10 min runtime at 20W.

Brief Description of Use/Function: Battery backup for outages during AI tasks; integrates with solar/inverter for off-grid research.

Estimated Lifecycle: 3-5 years (battery degradation; replaceable cells).

Price: $30-50.

Owned: Yes (XP400 UPS provides full backup; PV375 inverter and Renogy solar controller add scalability/off-grid).



Breadboard and Jumper Wires Kit (830-point + Assorted Wires)

Quantity Needed: 1 (shared for prototyping).

Quality/Dependency Requirements: 830-point breadboard; male-male/female-male jumpers; compatible with Pi GPIO/Arduino.

Brief Description of Use/Function: Prototyping connections for sensors/electrodes in ferrofluid; GPIO expansions in AI rig.

Estimated Lifecycle: 3-5 years (wear from use).

Price: $10.

Owned: Yes (Elegoo kit provides).



USB Cable (Type-A to Type-B, for Arduino/Pi Connections)

Quantity Needed: 1 (shared).

Quality/Dependency Requirements: USB 2.0+; 1-2m length for flexibility.

Brief Description of Use/Function: Connects Pi/Arduino to computer for programming/data transfer in setups.

Estimated Lifecycle: 3-5 years (cable wear).

Price: $5.

Owned: Yes (your drawers/Elegoo kit cover).



Assorted Resistors Pack (10-1kΩ, for Circuits)

Quantity Needed: 1 pack (shared).

Quality/Dependency Requirements: 1/4W or 1/2W; 5-10% tolerance; assorted values for voltage dividers.

Brief Description of Use/Function: Builds circuits for sensors/LEDs in ferrofluid; voltage regulation in AI peripherals.

Estimated Lifecycle: 5+ years (durable components).

Price: $5.

Owned: Yes (Elegoo pack covers).



Soldering Iron Kit (with Stand and Solder)

Quantity Needed: 1 (shared).

Quality/Dependency Requirements: 60W+ adjustable; fine tip for electronics.

Brief Description of Use/Function: Solders wires/electrodes/connections in ferrofluid; GPIO mods in AI rig.

Estimated Lifecycle: 4-6 years (tip wear; replaceable).

Price: $20.

Owned: No.



Wire Cutters/Strippers Tool

Quantity Needed: 1 (shared).

Quality/Dependency Requirements: Insulated handles; precision for 26 AWG wire.

Brief Description of Use/Function: Cuts/strips wires for assembly in ferrofluid/AI setups.

Estimated Lifecycle: 5-7 years (blade dulling).

Price: $10.

Owned: Yes.



Epoxy Sealant (Tube, for Sealing)

Quantity Needed: 1 (shared).

Quality/Dependency Requirements: Two-part epoxy; waterproof, non-conductive.

Brief Description of Use/Function: Seals electrodes/wires in ferrofluid tubes; secures components in AI rig.

Estimated Lifecycle: 2-3 years (shelf life once opened).

Price: $9.

Owned: Yes (your cabinets full of epoxy/silicone).



Ferrofluid Specific Components

Air-Core Solenoid (710 turns, 13 cm length, 3.15 cm inner diameter, 5A max)

Quantity Needed: 1.

Quality/Dependency Requirements: Hollow plastic tube for ferrofluid; uniform magnetic field.

Brief Description of Use/Function: Provides axial magnetic field in solenoid setup for ferrofluid visualization.

Estimated Lifecycle: 5-7 years (coil durability).

Price: $49.

Owned: No.



Ferrofluid (EFH-1, educational grade, 150 ml bottle)

Quantity Needed: 1.

Quality/Dependency Requirements: Oil-based magnetic nanofluid; safe for educational use.

Brief Description of Use/Function: Magnetic fluid shared across solenoid/toroid/ferrocell for experiments.

Estimated Lifecycle: 2-4 years (settling if not stirred).

Price: $60 (scaled from 60ml ~$25).

Owned: No.



Rubber Stoppers (size 6-7, tapered)

Quantity Needed: 2.

Quality/Dependency Requirements: Fit 3.15 cm tube; non-magnetic.

Brief Description of Use/Function: Seals solenoid ends to contain ferrofluid.

Estimated Lifecycle: 3-5 years (rubber degradation).

Price: $5 (pack).

Owned: No.



Copper Foil Strips (for electrodes, 2-3 cm wide, 10-20 cm long, conductive)

Quantity Needed: 6.

Quality/Dependency Requirements: Conductive tape; self-adhesive.

Brief Description of Use/Function: Electrodes for electrical measurements in tubes/plates.

Estimated Lifecycle: 4-6 years (adhesive wear).

Price: $10.

Owned: No.



Hall Effect Sensor Module (linear, Arduino-compatible; e.g., SS49E)

Quantity Needed: 3.

Quality/Dependency Requirements: Linear output; 3.3-5V.

Brief Description of Use/Function: Measures magnetic fields in setups.

Estimated Lifecycle: 5-7 years (sensor stability).

Price: $3 each ($9 total).

Owned: No.



Syringe (10-20 ml, for injecting ferrofluid)

Quantity Needed: 1.

Quality/Dependency Requirements: Disposable/plastic; precise.

Brief Description of Use/Function: Fills tubes/plates with ferrofluid.

Estimated Lifecycle: 1-2 years (reusable if cleaned).

Price: $2.

Owned: No.



Silicone Tubing (1/4” ID x 3/8” OD, 10 ft length, transparent, food-grade)

Quantity Needed: 1.

Quality/Dependency Requirements: Flexible; heat-resistant.

Brief Description of Use/Function: Bent into toroidal loop for ferrofluid flow.

Estimated Lifecycle: 3-5 years (flexibility loss).

Price: $15.

Owned: No.



Enameled Copper Wire Spool (26 AWG, 1 lb / ~1300 ft each, for double helix)

Quantity Needed: 2.

Quality/Dependency Requirements: Insulated; solderable.

Brief Description of Use/Function: Windings for toroid helix.

Estimated Lifecycle: 5+ years (wire durability).

Price: $15 each ($30 total).

Owned: No.



Barbed Tube Fittings (1/4” barb x 1/4” NPT, brass or plastic)

Quantity Needed: 2.

Quality/Dependency Requirements: Leak-proof; compatible with tubing.

Brief Description of Use/Function: Seals/connects toroid tube ends.

Estimated Lifecycle: 4-6 years (corrosion if brass).

Price: $5 (pack).

Owned: No.



Clear Acrylic Sheets (20x20” x 1/8” thick, cast plexiglass)

Quantity Needed: 3.

Quality/Dependency Requirements: Transparent; drillable.

Brief Description of Use/Function: Plates for ferrocell sandwich.

Estimated Lifecycle: 5-10 years (scratch-resistant).

Price: $30 (pack).

Owned: No.



Copper Clad FR4 PCB Board (18x18”, double-sided, 1 oz copper)

Quantity Needed: 1.

Quality/Dependency Requirements: Etchable; FR4 material.

Brief Description of Use/Function: Base for Kepler triangle grid etching in ferrocell.

Estimated Lifecycle: 5-7 years (board durability).

Price: $112.

Owned: No.



WS2812B LED Matrix Panel (flexible, individually addressable, e.g., 5050 SMD RGB, 0.24ft x 0.96ft or larger)

Quantity Needed: 1.

Quality/Dependency Requirements: Addressable; 5V.

Brief Description of Use/Function: Backlighting for blue-red shifting in ferrocell.

Estimated Lifecycle: 4-6 years (LED burnout).

Price: $30.

Owned: No.



Arducam Camera Module (2MP OV2640 SPI, Arduino-compatible)

Quantity Needed: 1.

Quality/Dependency Requirements: 2MP; SPI interface.

Brief Description of Use/Function: Captures ferrocell patterns for analysis.

Estimated Lifecycle: 3-5 years (sensor wear).

Price: $30.

Owned: No.



Photo Paper for Toner Transfer (A4 sheets, 20 pcs, heat-resistant)

Quantity Needed: 1 pack.

Quality/Dependency Requirements: Toner-compatible; glossy.

Brief Description of Use/Function: Prints grid pattern for PCB etching in ferrocell.

Estimated Lifecycle: Single-use per print.

Price: $10.

Owned: No.



Ferric Chloride PCB Etchant (100ml bottle, ready-to-use)

Quantity Needed: 1.

Quality/Dependency Requirements: Concentrated; safe handling.

Brief Description of Use/Function: Etches copper board for ferrocell grid.

Estimated Lifecycle: Single-use batch.

Price: $10.

Owned: No.



Hobby Mini Drill Press (benchtop, variable speed, for PCB/LED drilling)

Quantity Needed: 1.

Quality/Dependency Requirements: 7-speed; B10 chuck.

Brief Description of Use/Function: Drills holes in acrylic/boards for LEDs in ferrocell.

Estimated Lifecycle: 5-7 years (motor wear).

Price: $40.

Owned: Yes (your benchtop mini drill press matches).



Photoresistor Modules (LDR sensors, Arduino-compatible, for light output detection)

Quantity Needed: 4.

Quality/Dependency Requirements: 3.3-5V; analog output.

Brief Description of Use/Function: Detects light changes in ferrocell.

Estimated Lifecycle: 4-6 years (sensor sensitivity).

Price: $5.

Owned: Yes (Elegoo LDR modules cover).



Spacers/Stand-offs (1/16” thick, for ferrofluid layer between plates)

Quantity Needed: 1 pack.

Quality/Dependency Requirements: Nylon; 0.1-0.5mm thick.

Brief Description of Use/Function: Maintains ferrofluid gap in ferrocell plates.

Estimated Lifecycle: 5+ years (durable plastic).

Price: $5.

Owned: No.



Scalability Add-Ons



Cluster HAT v2.5 (for 4x Pi Zeros/Picos, Expandable)

Quantity Needed: 1 (for initial stacking; add for larger clusters).

Quality/Dependency Requirements: Official Pimoroni; GPIO-compatible, supports Pi 4/5 hybrids.

Brief Description of Use/Function: Stacks multiple Pis for distributed AI (e.g., parallel OCR); scales TOPS/compute.

Estimated Lifecycle: 5-7 years (reusable across Pi generations).

Price: $40-60.

Owned: No.



PCIe Adapter Kit (M.2 to OCuLink for External GPUs)

Quantity Needed: 1 (per Pi for GPU upgrades).

Quality/Dependency Requirements: OCuLink cable + power splitter; ARM-compatible, kernel patches needed.

Brief Description of Use/Function: Enables external GPUs for advanced AI (e.g., faster inference); future-proofs for high-TFLOPS tasks.

Estimated Lifecycle: 4-6 years (tech shifts to newer PCIe).

Price: $50-80.

Owned: No.



External GPU (Used AMD RX 460 or Equivalent Mid-Range)

Quantity Needed: 2 (for dual-GPU setups or redundancy; add sequentially as capital allows).

Quality/Dependency Requirements: Polaris architecture (e.g., RX 460 4GB GDDR5); low-power (~75W TDP), AMD for open-source drivers; requires PCIe adapter and Pi kernel patches (amdgpu).

Brief Description of Use/Function: Significantly boosts AI capabilities (e.g., 5-10x faster inference for OCR/LLMs, ~200 tokens/sec); plug-and-play after initial rig prep (adapter install, kernel config).

Estimated Lifecycle: 3-5 years (used card wear; replace with higher-end as capital grows).

Price: $50-80 each.

Owned: No.



Optional/Advanced Add-Ons

HDMI Cable (Mini-HDMI to HDMI, 1m)

Quantity Needed: 1-2 (for monitors/docks).

Quality/Dependency Requirements: HDMI 2.0; 4K@60Hz support, gold-plated.

Brief Description of Use/Function: Connects Pi to monitors for setup/debugging in multi-display AI workflows.

Estimated Lifecycle: 5-10 years (durable if not bent).

Price: $5-10.

Owned: Yes (your HDMI cords cover).



GPIO Extension Kit or Breakout Board

Quantity Needed: 1 (for prototyping).

Quality/Dependency Requirements: 40-pin ribbon cable + breadboard; compatible with Elegoo sensors.

Brief Description of Use/Function: Extends GPIO for sensors/Arduino integration in AI/IoT expansions.

Estimated Lifecycle: 3-5 years (wear from use).

Price: $10-15.

Owned: Yes (Elegoo kit provides).



External HDD Enclosures (USB 3.0, 3.5-inch Variant)

Quantity Needed: 2 (one per HDD for protection).

Quality/Dependency Requirements: USB 3.0; aluminum for cooling, tool-free assembly.

Brief Description of Use/Function: Houses 2TB/750GB HDDs for secure storage; enables RAID in AI data pipelines.

Estimated Lifecycle: 5-7 years (mechanical; fans replaceable).

Price: $15-25 each.

Owned: No.



RTC Module (Real-Time Clock)

Quantity Needed: 1 (system-wide).

Quality/Dependency Requirements: DS1307/I2C; battery-backed, Pi GPIO compatible.

Brief Description of Use/Function: Maintains time during outages for scheduled AI tasks/logs.

Estimated Lifecycle: 5-7 years (battery ~3 years, replaceable).

Price: $5-10.

Owned: Yes (Elegoo DS1307 covers).

