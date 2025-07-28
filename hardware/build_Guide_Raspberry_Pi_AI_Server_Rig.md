Subject: Preparation and Build Guide for Raspberry Pi AI Home Server Rig



Date: July 28, 2025



Purpose

This memo provides a comprehensive overview of the Raspberry Pi 5-based AI home server rig, designed for AI research and production tasks with an initial focus on math-heavy OCR processing (e.g., 91-page PDFs). The rig is future-proofed for scalability, including clustering, external GPUs, and off-grid operation. It leverages your owned inventory (e.g., Pi 4 B+, docks, hubs, UPS/inverter, cables, Elegoo kit) to minimize costs while preparing for expansions like mid-range GPUs ($50-100) via modular design and pre-configured software. Total estimated build cost for non-owned items: ~$700-900 (unified with ferrofluid, but AI rig portion ~$340 core). The build emphasizes safety, modularity, and testing to ensure reliability.



Key Components and Functions

The rig's components are drawn from the locked Unified Parts List V1.0 (AI server focus). Each serves a specific role in computation, power, connectivity, and scalability:



Raspberry Pi 5 Board (16GB RAM Variant): Core SBC for running AI models (e.g., Texify/Pix2tex for OCR), agents (CrewAI), and OS (Ubuntu). Function: Processes data, orchestrates tasks; 16GB enables multi-tasking without swaps.

Raspberry Pi AI Kit (with Hailo-8L Accelerator): M.2 HAT with 13 TOPS NPU. Function: Accelerates neural inference (e.g., 5-10x faster OCR), offloading CPU for efficiency.

Compatible Case/Enclosure (e.g., Argon THRML): Aluminum housing. Function: Protects components, aids heat dissipation, supports HAT/GPIO access for expansions.

Active Cooling System (e.g., Official Raspberry Pi Active Cooler): Heatsink/fan. Function: Maintains <70°C temps during loads, preventing throttling.

Official 27W USB-C Power Supply (PoE-Enabled): PD supply with PoE HAT option. Function: Stable power for Pi/AI Kit; PoE preps for networked clusters.

UPS/Battery HAT or Adapter: Owned XP400 UPS/inverter/solar. Function: Backup during outages; enables off-grid AI (e.g., with PV375 for DC sources).

MicroSD Card (128GB+ Class 10/A2): Boot media. Function: Stores OS/configs; quick swaps for testing.

Powered USB Hub (7+ Ports, USB 3.0): Owned hub. Function: Expands ports for HDDs/peripherals; RAID-capable for data storage.

Ethernet Adapter (2.5G/5G USB): Owned docks' Gigabit. Function: High-speed networking for clusters; WiFi backup.

USB Cables (Type-A to Type-C/Micro-USB): Owned assortment. Function: Connects all peripherals.

Cluster HAT v2.5: GPIO HAT. Function: Stacks Pis for distributed compute (e.g., parallel OCR).

PCIe Adapter Kit (M.2 to OCuLink): Cable/splitter. Function: Enables external GPUs; preps for plug-in upgrades.

External GPU (Used AMD RX 460 or Equivalent): 2x low-power cards. Function: Boosts AI (e.g., faster inference); added sequentially.

HDMI Cable (Mini-HDMI to HDMI): Owned. Function: Monitor connection for debugging.

GPIO Extension Kit or Breakout Board: Owned Elegoo. Function: Sensor/Arduino integration for IoT/AI extensions.

External HDD Enclosures (USB 3.0): 2x. Function: Houses HDDs for secure/RAID storage.

RTC Module: Owned Elegoo DS1307. Function: Timekeeping during outages.

Owned items (e.g., Pi 4 B+ for offload, docks for Ethernet/USB, UPS for power) integrate seamlessly, reducing build complexity.



Order of Installation / Operations

Follow this step-by-step build order for safety and efficiency (time: ~2-4 hours; tools: screwdriver, owned cables). Test at each stage.



Preparation (30 min): Gather parts; update Pi firmware via owned MicroSD (if available) or download Ubuntu to a temp card. Install monitoring software (e.g., lm-sensors, htop) on Pi 4 B+ for baseline testing. Assemble IKEA Lack rack for organization (shelves for Pi, docks, UPS).

Base Assembly (45 min): Insert MicroSD (item 7) into Pi 5 (item 1). Attach AI Kit (item 2) to PCIe slot. Mount active cooler (item 4) to Pi. Place in enclosure (item 3), securing with screws—ensure GPIO/ports accessible.

Power and Connectivity Setup (30 min): Connect power supply (item 5) to Pi. Wire UPS (item 6) for backup (plug Pi/docks into battery outlets). Attach USB hub (item 8) to Pi USB 3.0 port; connect Ethernet from dock/adapter (item 9). Use cables (item 10) for HDD enclosures (item 16) if ready. Attach RTC (item 17) and GPIO kit (item 15) to Pi pins.

Scalability Prep (45 min): Install Cluster HAT (item 11) on GPIO if clustering Pi 4. Connect PCIe adapter (item 12) to M.2 slot (test empty first). For GPUs (item 13), plug into OCuLink (initially leave disconnected; prep kernel with amdgpu patches via sudo apt install linux-headers-rpi \&\& make modules).

Software Operations / Testing (60 min): Boot Pi 5 to Ubuntu; configure via HDMI (item 14) on monitor. Install Docker/K3s for agents/clustering (e.g., curl -sfL https://get.k3s.io | sh). Join Pi 4 as node. Test OCR pipeline (Texify on AI Kit) with sample PDF. Monitor temps/power with vcgencmd measure\_temp and htop. Add owned solar/inverter for off-grid sim.

Maintenance/Expansion Prep: Schedule cron jobs for backups/logs. For future GPUs: Reboot after plug-in, install ROCm/amdgpu drivers. Use Lack rack space for additions.

This build preps for seamless upgrades (e.g., GPUs via PCIe, clustering via HAT)—contact for troubleshooting!

