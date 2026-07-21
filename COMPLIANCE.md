# COMPLIANCE.md

**Coastal Alpine Tech Limited** | **Product:** SoilGuard Portal
Last updated: 19 July 2026

## Privacy / Security / Governance (fleet mandatory)

| Pillar | Standard |
| --- | --- |
| **Privacy** | Local-first default; purpose-limited collection; Privacy Act 2020; Te Mana Raraunga spirit; third-party processing only when opt-in and disclosed |
| **Security** | No silent exfil; owner-controlled credentials; least privilege; SecOps / red-team cadence where CI is present |
| **Governance** | HITL for high-stakes; agents draft only; humans sign / send / pay |

Last reviewed (fleet block): 2026-07-21

> Super Grok compliance briefing (19 July 2026). This is **alignment evidence**, not a compliance certificate or legal advice.

## Regulatory Mapping

### New Zealand
- Privacy Act 2020 + **IPP 3A** (Privacy Amendment Act 2025) - effective **1 May 2026**  
  Notification required when personal information is collected indirectly.
- Biometric Processing Privacy Code 2025  
  New biometric processing: 3 November 2025  
  Existing biometric processing: 3 August 2026
- Health Information Privacy Code (applies where health / wellbeing data is processed)
- Te Mana Raraunga principles - primary data sovereignty framework

### European Union
- **EU AI Act** - Annex III high-risk obligations enforceable **2 August 2026**
- Relevant high-risk categories:
  - Health decision support
  - Biometrics (remote identification, categorisation, emotion recognition)
  - Critical infrastructure / essential services
- Required: risk management, data governance, technical documentation, human oversight, logging, transparency, post-market monitoring

### International Standards
- **ISO/IEC 42001** - AI Management System (AIMS)  
  Covers AI policy, risk assessment, data governance, human oversight, monitoring, continual improvement
- **SOC 2** - Security, Availability, Confidentiality, Processing Integrity, Privacy  
  Priority for multi-tenant / customer-facing components

### Core Technical Controls (Mandatory)
- Local-first / offline-native processing by default
- Owner-controlled encryption keys
- No silent data exfiltration
- Explicit Human-in-the-Loop (HITL) gates for high-impact and culturally sensitive decisions
- Data residency under New Zealand control

### Scope Notes
- Current systems prioritise offline-native operation and data minimisation.
- Any future multi-tenant or customer-facing features will be assessed against SOC 2 and EU AI Act high-risk requirements before release.

### Limitations
- Not legal advice; not a certification claim.
- Confirm statute application with NZ counsel before commercial shipping claims.
- Agents inform / draft / prepare only; humans advise / sign / file / send / pay.

---

## Product-specific mapping

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

## 5. Kaitiakitanga & Maori Data Sovereignty (*Te Mana Raraunga*)

In New Zealand, soil (*one*) is considered a *taonga* (treasure) and is deeply connected to catchments and ancestral *whenua* (land).

* **Kaitiakitanga:** The portal supports the practice of environmental guardianship (*kaitiakitanga*) by empowering landowners with local decision-making tools to prevent clay degradation and nitrate leaching.
* **Data Sovereignty:** Under the principles of *Te Mana Raraunga* (Maori Data Sovereignty), data regarding the health and agricultural output of indigenous whenua must remain under the stewardship of the iwi or hapu who manage it. SoilGuard runs entirely offline on local edge hardware (Raspberry Pi 5 + AI HAT+), guaranteeing that data is never uploaded to offshore cloud servers without explicit customary permission.

---

*This compliance document is an operational reference and does not constitute formal legal advice. Operators must check their specific resource consents and regional permitted activity guidelines with their local regional council.*
