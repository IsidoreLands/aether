V2.5 Parts List: Ferrofluid Solenoid, Toroidal Tube, and Ferrocell Setups



This formal V2.5 parts list is based on V2.4, with no updates for the owned AV equipment (RCA DSB772WE AV multimedia switcher and RadioShack 15-1244 RF Power Modulator). These are audio/video signal devices (e.g., for switching AV inputs or modulating signals to RF for TVs), not suitable substitutes for the adjustable DC power supply (Item 5: variable 0-12V, 5A DC output for precise control of coils/electrodes/LEDs) or any other BOM items (e.g., no DC output, low power ~4.5-5W, fixed voltage). They could potentially be repurposed for non-critical AV monitoring if the system evolves (e.g., video output from Raspberry Pi), but they don't cover current needs. Prices for needed items remain approximate; totals exclude shipping/taxes and reflect deductions for previously owned parts. Sources are primarily Amazon, Arduino Store, and scientific suppliers for reliability. Quantities assume a single integrated prototype system.



Bill of Materials (BOM)



Item #	Quantity	Description	Part Number/Example	Source	Approx. Price (USD)	Status	Notes

1	1	Air-Core Solenoid (710 turns, 13 cm length, 3.15 cm inner diameter, 5A max)	P8-8000	Arbor Scientific (arborsci.com)	$49.00	Needed	Hollow plastic tube for ferrofluid filling; provides uniform axial magnetic field. Used in solenoid setup.

2	1	Ferrofluid (EFH-1, educational grade, 150 ml bottle)	EFH1	Ferrotec (ferrofluid.ferrotec.com) or Amazon (Applied Magnets)	$50.00	Needed	Oil-based magnetic nanofluid; increased volume for filling all setups. Shared across all setups.

3	2	Rubber Stoppers (size to fit 3.15 cm diameter tube, tapered)	Generic (e.g., size 6-7)	Amazon or Fisher Scientific	$5.00 (pack)	Needed	Seals solenoid ends to contain ferrofluid; non-magnetic material. Used in solenoid setup.

4	6	Copper Foil Strips (for electrodes, 2-3 cm wide, 10-20 cm long, conductive)	Generic foil tape (e.g., ELK Copper Foil Tape 1” x 66ft)	Amazon	$10.00	Needed	Inserted in tubes/plates for electrical measurements; Qty 2 per setup. Shared material but separate pieces.

5	1	Adjustable DC Power Supply (0-12V, 5A output)	Generic (e.g., 60W variable adapter)	Amazon	$20.00	Needed	Powers coils, electrodes, and LEDs for perturbations; shared across all setups.

6	1	Raspberry Pi 4 Model B+ (as substitute for Arduino Uno; 1.5GHz quad-core, 1GB RAM)	Raspberry Pi 4 B+	Raspberry Pi Foundation (raspberrypi.com) or CanaKit (via Amazon)	$0.00	Already Owned	Central controller for sensor data acquisition and logging; shared across all setups via GPIO/interchangeable wiring. Substitutes for Arduino Uno; owned Pi 4 B+ provides equivalent (or superior) functionality.

7	1	Handheld LCR Meter (capacitance, inductance, resistance; e.g., UT603 model)	UT603	Amazon or TME	$40.00	Needed	Measures electrical properties; shared across all setups.

8	3	Hall Effect Sensor Module (linear, Arduino-compatible; e.g., SS49E)	SS49E	Amazon or ElectroPeak	$3.00 each ($9.00 total)	Needed	Measures magnetic field strength; one per setup for independent placement, but can share if swapping during tests.

9	1	Breadboard and Jumper Wires Kit (830-point breadboard + assorted wires)	Generic kit	Amazon	$0.00	Already Owned	Prototyping connections; shared across all setups. Provided in Elegoo kit (includes 830-point breadboard and jumper wires).

10	1	Epoxy Sealant (tube, for sealing electrodes/wires)	Generic (e.g., two-part epoxy)	Amazon	$0.00	Already Owned	Secures and seals components; shared across all setups. User has cabinets full of epoxy (and silicone rubber as alternative).

11	1	Soldering Iron Kit (for electronics, with stand and solder)	Generic kit	Amazon	$20.00	Needed	Solders wires, electrodes, and connections; shared across all setups.

12	1	Wire Cutters/Strippers Tool	Generic pliers	Amazon	$10.00	Needed	Cuts and strips wires for assembly; shared across all setups.

13	1 pack	Assorted Resistors (e.g., 10-1kΩ, for voltage dividers/circuits)	Generic pack	Amazon	$0.00	Already Owned	Builds simple circuits; shared across all setups. Provided in Elegoo kit (assorted resistor pack).

14	1	USB Cable (Type-A to Type-B, for Arduino)	Generic	Amazon	$0.00	Already Owned	Connects Arduino to computer; shared across all setups. Provided in Elegoo kit.

15	1	Syringe (10-20 ml, for injecting ferrofluid)	Generic disposable	Amazon or pharmacy	$2.00	Needed	Fills tubes/plates; shared across all setups.

16	1	Silicone Tubing (1/4" ID x 3/8" OD, 10 ft length, transparent, food-grade)	Generic (e.g., S SYDIEN 1/4" ID Silicone Tubing)	Amazon	$15.00	Needed	Flexible tube bent into toroidal loop; used in toroid setup.

17	2	Enameled Copper Wire Spool (26 AWG, 1 lb / ~1300 ft each, for double helix)	BNTECHGO 26 AWG	Amazon	$15.00 each ($30.00 total)	Needed	One spool per helix for intertwined windings; used in toroid setup.

18	2	Barbed Tube Fittings (1/4" barb x 1/4" NPT, brass or plastic)	SUNGATOR 1/4'' NPT Brass Hose Barb Fittings	Amazon	$5.00 (pack of 2)	Needed	Connects and seals tube ends; used in toroid setup.

19	2	Clear Acrylic Sheets (20x20" x 1/8" thick, cast plexiglass)	Generic (e.g., 2 Pack Plexiglass Transparent Square Panels)	Amazon	$30.00 (pack)	Needed	Plates for ferrocell sandwich (one for front, one for back with LED holder); large enough for 18x18" grid + solder points. Used in ferrocell setup.

20	1	Copper Clad FR4 PCB Board (18x18", double-sided, 1 oz copper)	Generic (e.g., Double Sided FR4 Board Material 18"x18")	T-Tech (t-tech.com) or eBay (pcblaminatescopperclad)	$112.00	Needed	Base for etching Kepler triangle copper grid; custom pattern printed and etched. Used in ferrocell setup.

21	1 pack	WS2812B LED Matrix Panel (flexible, individually addressable, e.g., 5050 SMD RGB, 0.24ft x 0.96ft or larger array to cover ~18x18")	BTF-LIGHTING WS2812B RGB 5050SMD	Amazon	$30.00	Needed	Backlighting array for blue-red shifting; drill holes in holder for LED placement. Used in ferrocell setup; flexible for custom matrix.

22	1	Arducam Camera Module (2MP OV2640 SPI, Arduino-compatible)	Arducam Mini Module Camera Shield OV2640	Amazon or Arducam (arducam.com)	$30.00	Needed	Captures images of ferrocell patterns for optical analysis; dedicated to ferrocell but shareable.

23	1 pack	Photo Paper for Toner Transfer (A4 sheets, 20 pcs, heat-resistant)	Ximimark 20Pcs A4 Sheet PCB Heat Toner Transfer Paper	Amazon	$10.00	Needed	Printed at Staples with Kepler triangle grid pattern for toner transfer etching of copper board. Used in ferrocell setup.

24	1	Ferric Chloride PCB Etchant (100ml bottle, ready-to-use)	Generic Ferric Chloride Etchant 100ml	Amazon	$10.00	Needed	Etches copper board after toner transfer for custom Kepler grid. Used in ferrocell setup; handle with care.

25	1	Hobby Mini Drill Press (benchtop, variable speed, for PCB/LED drilling)	Generic Mini Drill Press (e.g., with 7-Speed CNC 795 Motor)	Amazon	$0.00	Already Owned	Drills holes in LED holder (acrylic or board) for matrix placement. Used in ferrocell setup; includes bits for precision. Matches owned benchtop mini drill press.

26	4	Photoresistor Modules (LDR sensors, Arduino-compatible, for light output detection)	Generic LDR Module	Amazon	$0.00	Already Owned	Additional sensors for optical output (e.g., light transmission changes in ferrocell); place around edges. Used in ferrocell setup, but shareable. Provided in Elegoo kit (multiple LDR/photoresistors included).

27	1 pack	Spacers/Stand-offs (1/16" thick, for ferrofluid layer between plates)	Generic nylon spacers (assorted pack)	Amazon	$5.00	Needed	Maintains thin ferrofluid gap (~0.1-0.5 mm) between acrylic plates. Used in ferrocell setup.

Totals

Estimated Total Cost: $373.00 (V2.3 base unchanged, no new owned items; core build ~$280, tools ~$40, accessories ~$53).

Substitutions: If 18x18" copper clad unavailable, use smaller boards tiled (~$50 total). For LED matrix, use strips if panel too costly. Raspberry Pi 4 B+ replaces Arduino Uno; may require GPIO adapters if not compatible with Arduino shields, but standard for sensor use.

Safety Notes: Gloves and ventilation for ferrofluid/etchant; eye protection for drill press. Shared components minimize redundancy for the integrated system.

