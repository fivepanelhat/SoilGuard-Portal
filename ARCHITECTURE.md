# SoilGaurd Portal System Architecture

SoilGaurd Portal is an edge-native soil quality and agricultural monitoring system designed for full offline operation in New Zealand's remote farm environments.

---

## 1. System Topology

```mermaid
flowchart TD
    A[Soil IoT Telemetry] --> B[MQTT Sensors<br/>Moisture, Temp, EC, N-P-K]
    C[Crop Cameras] --> D[OpenCV Video Frame Ingest]
    E[Sound Watchdog] --> F[PyAudio Noise Monitor]

    B & D & F --> G[Edge Integration Layer]
    G --> H[Gemma 4 Instruct via Ollama<br/>gemma4:e4b — Multimodal SLM]
    H --> I[LangGraph Reasoning / Orchestration]

    I --> J[Deterministic Plan Enforcement]
    J --> K[Actuator GPIO Pins<br/>Irrigation, Fertigation, Fans]
    
    I --> L[Local Storage & compliance Logging]
    L --> M[Structured JSON/CSV Audit Logs]

    subgraph "Sovereign Edge Boundary"
        G
        H
        I
        L
        M
    end

    style I fill:#f97316,stroke:#ea580c,color:#fff
    style M fill:#3b82f6,stroke:#2563eb,color:#fff
```

---

## 2. Core Subsystems

### Ingestion Layer (`portal_core/mqtt_client.py`)
* Operates an asynchronous Paho MQTT subscriber loop.
* Ingests local agricultural soil probes tracking Volumetric Water Content (`%VWC`), Temperature (`°C`), Salinity/EC (`dS/m`), and dry-soil Nitrogen/Phosphorus/Potassium (`mg/kg`).

### Sensor Capture Layer (`portal_core/av_capture.py`)
* Captures high-resolution video frames of crop foliage using local USB/CSI cameras (allowing visual assessment of leaf chlorosis or nutrient deficiencies).
* Ingests acoustic signals from farm machinery or water irrigation pumps to identify mechanical leaks or cavitation anomalies.

### Edge Inference Layer (`portal_core/ai_agent.py`)
* Connects to local Ollama server executing the optimized `gemma4:e4b` model (Google's Gemma 4 4B Instruct model).
* Leverages multimodal capabilities to reason over both telemetry metrics and camera frames.
* Evaluates prompts against input safety guards (`input_guard_check` from `coastal-alpine-core`) to block malicious patterns or prompt injections.

### Actuator Control Layer (`portal_core/hardware_control.py`)
* Translates plan commands to GPIO BCM pins:
  * **Irrigation (Valves/Pumps):** PWM duty cycle control representing low/medium/high/off states.
  * **Nutrient Fertigation Relays:** Fertigation injection pump controls.
  * **Ventilation/Circulation Fans:** Ventilation fan relays for crop aeration.
* Safely runs in mock simulation mode when physical hardware interfaces are unavailable.

### Auditing & Exporter Layer (`portal_core/compliance_exporter.py`)
* Writes detailed, hourly audit events as standalone JSON records.
* Appends summary data to `compliance_ledger_CONSENT-XXX.csv` conforming to Waikato Regional Council permitted activity guidelines.
* Working directory disk space is protected by `portal_core/media_pruner.py` which cleans old frames/audio while preserving all CSV/JSON compliance records.

---

## 3. Data Flow Sequencing

```mermaid
sequenceDiagram
    autonumber
    participant Sensors as MQTT/Camera/Mic Probes
    participant Daemon as main.py (Orchestrator)
    participant Agent as ai_agent.py (Gemma 4)
    participant HW as hardware_control.py (Actuators)
    participant Exporter as compliance_exporter.py

    loop Every 15 Seconds
        Sensors->>Daemon: Telemetry payloads, camera frames & audio chunks
        Daemon->>Agent: Request state analysis and crop review
        Agent-->>Daemon: Deterministic JSON Optimization Plan
        Daemon->>HW: Enforce action levels (Irrigation, Fertigation, Fans)
        HW-->>Daemon: Actuation confirmation status
        Daemon->>Exporter: Export structured ComplianceRecord
        Exporter->>Exporter: Write CSV/JSON ledger audit trail to disk
    end
```
