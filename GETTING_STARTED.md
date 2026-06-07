# SoilGuard Portal: Getting Started

This guide extends the Quick Start in README.md with additional configuration detail.

---

## 1. Environment Configuration

Copy `.env.example` to `.env` and configure:

---

## 2. NEMS-SQ Threshold Configuration

Set NEMS-SQ 2025 target range thresholds in `.env` matching your land-use category:

Consult the updated NEMS-SQ 2025 target ranges document from MfE before configuring.

---

## 3. Running as a Systemd Service

```bash
sudo cp soilguard.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable soilguard
sudo systemctl start soilguard
sudo systemctl status soilguard
```

---

## 4. Freshwater Farm Plan Evidence

Compliance exports in `telemetry_data/compliance_exports/` are formatted for use as
Farm Plan audit evidence. Retain all records for the full 5-year plan cycle plus additional
7 years per Privacy Act 2020 recommended retention.
