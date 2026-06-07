# SoilGuard Portal Compliance & Regulatory Framework Guide

This document maps SoilGuard Portal's soil telemetry, local reasoning, and nutrient logging outputs to the key New Zealand environmental compliance and regulatory frameworks.

---

## 1. Primary Environmental Legislation

### Resource Management Act 1991 (RMA)
The RMA is the foundation of New Zealand's resource management framework. 
* **Transition Path:** In December 2025, the Government introduced the draft *Natural Environment Bill* and *Planning Bill* to replace the RMA (public consultation closed February 2026). SoilGuard's sovereign data logging architecture is engineered to dynamically adapt to the transitioning rules under the incoming Natural Environment Bill.
* **Permitted Activities:** Land use and soil discharge activities are governed by regional plans (authorized under the RMA). SoilGuard helps landowners demonstrate compliance with permitted activity rules by providing verified, continuous local telemetry records.

---

## 2. National Environmental Standards for Freshwater (NES-F 2020)

The **Resource Management (National Environmental Standards for Freshwater) Regulations 2020** impose strict controls on agricultural activities to protect freshwater quality.

### Synthetic Nitrogen Fertiliser Application Cap
* **The Limit:** The NES-F imposes a cap of **190 kg of synthetic nitrogen fertiliser per hectare per year** on pastoral land.
* **Record Keeping:** Dairy and pastoral farming operators must record and report their synthetic nitrogen application rates annually to their regional council.
* **SoilGuard Integration:** The portal's compliance database registers local N-P-K readings and tracks synthetic N fertigation activations (`nutrient_action`). This generates automated, audit-ready reports that cross-reference sensor values against the 190 kg N/ha limit to flag potential over-application risks.

---

## 3. Freshwater Farm Plans (FWFP)

Under the **Resource Management (Freshwater Farm Plans) Regulations 2023**, agricultural operators in designated Freshwater Management Units (FMUs) must prepare and implement certified FWFPs.
* **Rollout Status:** While the nationwide FWFP rollout is paused pending RMA reform (with the notable exception of the active **Southland Region**), the August 2025 Resource Management Amendment Act updated the framework to allow closer alignment with approved industry assurance schemes (e.g. Fonterra, DairyNZ).
* **Soil Erosion & Sediment Runoff:** FWFPs require specific actions to identify and mitigate risks of soil erosion, surface ponding, and nutrient runoff into local streams.
* **SoilGuard Mitigation:** By tracking soil moisture (`moisture_pct`) and electrical conductivity (`electrical_conductivity`), the system disables irrigation lines during saturation periods to prevent ponding and clay soil erosion.

---

## 4. Regional Council Rules

SoilGuard is calibrated to support permitted activity rules for soil discharges and crop irrigation across NZ regional councils:

### Waikato Regional Council
* **Waikato Regional Plan Rule 3.5.5.1:** Governs discharge of farm nutrients and effluent to land. Permitted activity rules dictate that discharges must not lead to surface ponding, runoff into open watercourses, or breaches of local water tables.
* **SoilGuard Rule Enforcement:** The systemd service monitors BCM GPIO relays configured for solenoid valves. If volumetric water content exceeds critical saturation thresholds (e.g. >45% VWC), irrigation is automatically locked out and logged to the master compliance CSV ledger.

### Horizons Regional Council
* **Horizons One Plan Chapter 14:** Restricts intensive land use activities in catchments identified as nutrient-sensitive. Operators must model nutrient losses (e.g. using OverseerFM). SoilGuard logs direct, empirical soil N-P-K data points that can be compared alongside modeled values to ensure absolute accuracy.

---

## 5. Kaitiakitanga & Māori Data Sovereignty (*Te Mana Raraunga*)

In New Zealand, soil (*one*) is considered a *taonga* (treasure) and is deeply connected to catchments and ancestral *whenua* (land).

* **Kaitiakitanga:** The portal supports the practice of environmental guardianship (*kaitiakitanga*) by empowering landowners with local decision-making tools to prevent clay degradation and nitrate leaching.
* **Data Sovereignty:** Under the principles of *Te Mana Raraunga* (Māori Data Sovereignty), data regarding the health and agricultural output of indigenous whenua must remain under the stewardship of the iwi or hapū who manage it. SoilGuard runs entirely offline on local edge hardware (Raspberry Pi 5 + AI HAT+), guaranteeing that data is never uploaded to offshore cloud servers without explicit customary permission.

---

*This compliance document is an operational reference and does not constitute formal legal advice. Operators must check their specific resource consents and regional permitted activity guidelines with their local regional council.*
