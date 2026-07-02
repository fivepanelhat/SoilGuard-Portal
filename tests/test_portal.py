"""
tests/test_portal.py - Unit tests for SoilGuard Portal.

Tests configuration ranges, schema structures, compliance exporters, and actuator mapping.
"""

import sys
import shutil
import pytest
import json
import csv
from pathlib import Path
from datetime import datetime

# Add portal root to import path
sys.path.insert(0, str(Path(__file__).parent.parent))

from coastal_alpine_core.portal_core.config import load_soilguard_config, SoilGuardConfig
from coastal_alpine_core.portal_core.compliance_exporter import ComplianceExporter
from portal_schemas.compliance import (
    SoilSensorReading,
    SoilAnalysisResult,
    SoilOptimizationPlan,
    ComplianceRecord,
    IrrigationAction,
    NutrientAction,
    FanAction,
)


@pytest.fixture
def temp_compliance_dir(tmp_path):
    """Temporary folder for testing compliance logs."""
    d = tmp_path / "compliance"
    d.mkdir()
    yield d
    shutil.rmtree(tmp_path)


def test_config_load():
    """Verify config structures and default ranges."""
    config = load_soilguard_config()
    assert isinstance(config, SoilGuardConfig)
    assert config.thresholds.moisture_min < config.thresholds.moisture_max
    assert config.thresholds.temp_max > 0
    assert config.thresholds.ec_max > 0
    assert config.thresholds.ph_min < config.thresholds.ph_max


def test_sensor_reading_schema():
    """Verify SoilSensorReading Pydantic validations."""
    reading = SoilSensorReading(
        sensor_id="soil_probe_1",
        sensor_type="moisture",
        value=28.5,
        unit="%VWC",
        timestamp=datetime.now(),
    )
    assert reading.value == 28.5
    assert reading.sensor_id == "soil_probe_1"


def test_analysis_result_schema():
    """Verify SoilAnalysisResult Pydantic validations."""
    res = SoilAnalysisResult(
        analysis_id="an-12345",
        status="healthy",
        moisture_trend="stable",
        temperature_trend="stable",
        ec_trend="stable",
        ph_trend="stable",
        nutrient_status="optimal",
        visual_observations="Canopy is green and healthy.",
        timestamp=datetime.now(),
    )
    assert res.status == "healthy"
    assert res.nutrient_status == "optimal"


def test_optimization_plan_schema():
    """Verify SoilOptimizationPlan parsing and actions."""
    plan = SoilOptimizationPlan(
        plan_id="opt-9988",
        irrigation_action=IrrigationAction.HIGH,
        nutrient_action=NutrientAction.LOW,
        fan_action=FanAction.OFF,
        confidence_score=0.92,
        logistical_notes="Soil moisture drops, boosting flow.",
        execution_window_minutes=15,
        requires_human_review=False,
    )
    assert plan.irrigation_action == IrrigationAction.HIGH
    assert plan.nutrient_action == NutrientAction.LOW
    assert plan.fan_action == FanAction.OFF
    assert not plan.requires_human_review


@pytest.mark.asyncio
async def test_compliance_record_export(temp_compliance_dir):
    """Verify ComplianceExporter writes JSON audits and appends to CSV ledgers."""
    exporter = ComplianceExporter(compliance_dir=str(temp_compliance_dir))

    record = ComplianceRecord(
        audit_id="aud-112233",
        timestamp=datetime.now(),
        regional_council="Waikato Regional Council",
        consent_id="CONSENT-2026-TEST",
        status="compliant",
        metrics={
            "moisture": 26.2,
            "temperature": 18.0,
            "electrical_conductivity": 0.52,
            "pH": 6.3,
            "nitrogen": 12.0,
            "phosphorus": 18.0,
            "potassium": 110.0,
        },
        actions_taken=["irrigation: low", "nutrient: off", "fan: medium"],
        operator_notes="Validation test execution loop.",
    )

    success = await exporter.export_record(record)
    assert success

    # Verify JSON file exists
    json_files = list(temp_compliance_dir.glob("*.json"))
    assert len(json_files) == 1
    with open(json_files[0], "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["audit_id"] == "aud-112233"
    assert data["status"] == "compliant"

    # Verify CSV ledger exists and has headers and record row
    csv_files = list(temp_compliance_dir.glob("*.csv"))
    assert len(csv_files) == 1
    assert csv_files[0].name == "compliance_ledger_CONSENT-2026-TEST.csv"

    with open(csv_files[0], "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 1
    assert rows[0]["audit_id"] == "aud-112233"
    assert rows[0]["regional_council"] == "Waikato Regional Council"
    assert float(rows[0]["metric_moisture_pct"]) == 26.2
    assert float(rows[0]["metric_EC_dS_m"]) == 0.52
    assert (
        rows[0]["actions_executed"]
        == "irrigation: low; nutrient: off; fan: medium"
    )
