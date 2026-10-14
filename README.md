# 🎵 PyAudioSync for Android

> A Python application for syncing audio playback across multiple devices with real-time equalization and advanced routing configuration.

---

## ✨ Planned Features

- **Multi-device playback** — Route audio to multiple output devices simultaneously
- **Synchronized playback** — Keep all devices in sync using low-latency audio backends (JACK / ASIO)
- **Graphic & parametric EQ** — Per-device equalizer with configurable bands
- **Audio routing matrix** — Flexible routing of outputs
- **Real-time DSP** — Low-latency audio processing powered by `numpy` and `scipy`
- **Device management** — Detect, configure, and manage all connected audio devices
- **Cross-platform** — Windows, Linux, and macOS support planned

---

## 🖥️ Planned Tech Stack

| Component | Library / Tool |
|---|---|
| Audio I/O | `sounddevice` |
| DSP / EQ | `numpy` |
| Low-latency sync | `JACK` (Linux), `ASIO` (Windows) |
| GUI | `CustomTkinter` |

---

# 🗺️ Roadmap

## Phase 1 — Core Audio Engine
- [x] Enumerate and list all available audio devices
- [x] Play audio to a single output device
- [x] Play the same stream to multiple devices simultaneously


## Phase 2 — Sync & Routing
- [ ] Implement clock sync for multi-device playback
- [ ] JACK backend support (Linux)
- [ ] ASIO backend support (Windows)
- [ ] Audio routing matrix (many-to-many)

## Phase 3 — EQ & DSP
- [ ] Graphic EQ (10-band)
- [ ] Parametric EQ (per-device)
- [ ] Real-time filter preview
- [ ] Low-latency DSP pipeline

## Phase 4 — GUI & Polish
- [x] Full GUI
- [ ] EQ visualizer (frequency response curve)
- [ ] Save/load configuration profiles


## Phase 5 - Other not important features
- [ ] Basic volume control per 
- [ ] Installer & packaging

---

