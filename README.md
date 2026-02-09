# 🚦 Pametni Semafor - Multi-Agent Traffic Management System

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![SPADE](https://img.shields.io/badge/SPADE-3.3.2-green.svg)
![FIPA](https://img.shields.io/badge/FIPA-ACL-orange.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

> **Inteligentni sustav za upravljanje prometnom signalizacijom baziran na multi-agentnoj arhitekturi sa FIPA ACL komunikacijom**

## 🎯 Ključne Karakteristike

### 🤖 Multi-Agent Architecture
- **Autonomni agenti** - svaki semafor i vozilo je nezavisan SPADE agent
- **FIPA ACL protokol** - standardizirana komunikacija (REQUEST, AGREE, INFORM, REFUSE)
- **XMPP messaging** - robusna, skalabilna komunikacija preko Prosody/ejabberd servera
- **Distribuirana inteligencija** - nema centralnog kontrolera

### 🧠 Adaptive Intelligence
- **Real-time adaptacija** - semafor prilagođava timinge na temelju trenutnog prometa
- **Queue-aware logic** - prati redove čekanja po smjerovima
- **Bus compensation** - autobus se računa kao 3 vozila (duži, sporiji)
- **Dynamic phase switching** - skraćuje/produljuje faze prema potrebi

### 🌊 Green Wave Coordination
- **Inter-agent communication** - semafori razmjenjuju informacije o stanjima
- **ETA calculation** - računa vrijeme dolaska vozila do susjednog raskrižja
- **Proactive phase adjustment** - priprema zeleno svjetlo prije dolaska vozila
- **Smooth traffic flow** - vozila prolaze kroz više raskrižja bez zaustavljanja

### 🚑 Emergency Vehicle Priority
- **Instant green light** - hitna vozila dobivaju odmah zeleno
- **Global emergency mode** - svi semafori se koordiniraju
- **Yield mechanism** - obična vozila automatski usporavaju
- **Priority hierarchy** - AMBULANCE (1) > FIRE (2) > POLICE (3)

### 📊 Knowledge Base & Learning
- **Traffic history** - prati zadnjih 100 vozila
- **Hourly statistics** - analiza prometa po satima dana
- **Phase change logging** - zapisuje razloge promjena faza
- **Neighbor state tracking** - prati stanja susjednih raskrižja
- **Performance metrics** - avg/max wait time, throughput, success rate

### 🎨 Real-time Visualization
- **60 FPS rendering** - smooth pygame vizualizacija
- **Live statistics** - real-time prikaz metrika
- **Color-coded vehicles** - različite boje za tipove vozila
- **Traffic light timers** - preostalo vrijeme prikazano uz svaki semafor
- **Emergency indicators** - magenta highlight za emergency mode

---

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.8+
python --version

# XMPP Server (Prosody ili ejabberd)
# Ubuntu/Debian:
sudo apt-get install prosody

# macOS:
brew install prosody

# Start server:
sudo systemctl start prosody
```

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/pametni-semafor.git
cd pametni-semafor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

```bash
# Configure Prosody XMPP server
sudo nano /etc/prosody/prosody.cfg.lua

# Add users (ili koristi in-band registration):
sudo prosodyctl adduser semafor_a@localhost
sudo prosodyctl adduser semafor_b@localhost
```

### Run Simulation

```bash
# Run main simulation
python simulation.py

# Controls:
# SPACE - Spawn car
# B - Spawn bus
# 1 - Spawn ambulance
# 2 - Spawn fire truck
# 3 - Spawn police
# F11 - Toggle fullscreen
# ESC - Exit
```

### Run Benchmark

```bash
# Test with 100 vehicles
python benchmark.py 100

# Test with 500 vehicles (longer test)
python benchmark.py 500

# Results will be saved as benchmark_results.png
```

---

## 🎮 Usage Examples

### Manual Vehicle Spawning

```python
# Interactive spawning process:
1. Press SPACE (for car) / B (for bus) / 1,2,3 (for emergency)
2. Select intersection: A or B
3. Select direction: N (North), S (South), W (West), E (East)
4. Vehicle spawns and starts moving

# Example: Spawn ambulance going North through intersection A
```

---

## 👨‍💻 Author

**Antonio Brković**
