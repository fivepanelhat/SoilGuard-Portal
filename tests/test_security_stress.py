"""
tests/test_security_stress.py - Security and Stress tests for SoilGuard Portal.

Verifies input bounds, Pydantic type safety checks, and disk pruner data retention guarantees.
"""

import os
import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError

from portal_schemas.compliance import (
 SoilOptimizationPlan,
 IrrigationAction,
 NutrientAction,
 FanAction,
)
from coastal_alpine_core.portal_core.media_pruner import MediaPruner


def test_plan_confidence_score_boundaries():
 """Verify that confidence_score must reside strictly within [0.0, 1.0]."""
 # Healthy case
 plan = SoilOptimizationPlan(
 plan_id="opt-ok-123",
 irrigation_action=IrrigationAction.LOW,
 nutrient_action=NutrientAction.OFF,
 fan_action=FanAction.MEDIUM,
 confidence_score=0.95,
 logistical_notes="Normal confidence",
 execution_window_minutes=15,
 requires_human_review=False,
 )
 assert plan.confidence_score == 0.95

 # Out of bounds too high
 with pytest.raises(ValidationError):
 SoilOptimizationPlan(
 plan_id="opt-bad-1",
 irrigation_action=IrrigationAction.LOW,
 nutrient_action=NutrientAction.OFF,
 fan_action=FanAction.MEDIUM,
 confidence_score=1.05,
 execution_window_minutes=15,
 )

 # Out of bounds too low
 with pytest.raises(ValidationError):
 SoilOptimizationPlan(
 plan_id="opt-bad-2",
 irrigation_action=IrrigationAction.LOW,
 nutrient_action=NutrientAction.OFF,
 fan_action=FanAction.MEDIUM,
 confidence_score=-0.1,
 execution_window_minutes=15,
 )


def test_invalid_actions_are_blocked():
 """Verify that invalid strings for actions raise ValidationErrors."""
 with pytest.raises(ValidationError):
 SoilOptimizationPlan(
 plan_id="opt-bad-3",
 irrigation_action="super_high", # Invalid action state
 nutrient_action=NutrientAction.OFF,
 fan_action=FanAction.MEDIUM,
 confidence_score=0.8,
 execution_window_minutes=15,
 )


@pytest.mark.asyncio
async def test_pruner_stress_retains_compliance(tmp_path):
 """
 Stress test for MediaPruner disk retention guarantees.
 Verifies that transient images/audio are successfully pruned on limit breaches
 while critical compliance files are ALWAYS retained.
 """
 media_dir = tmp_path / "media"
 logs_dir = tmp_path / "sensor_logs"
 compliance_dir = tmp_path / "compliance"

 media_dir.mkdir()
 logs_dir.mkdir()
 compliance_dir.mkdir()

 # 1. Create expired transient media files (older than 48 hours)
 expired_time = datetime.now() - timedelta(hours=50)
 for i in range(10):
 # Image
 p = media_dir / f"frame_{i}.jpg"
 p.write_bytes(b"MOCK_JPEG_CONTENT")
 os.utime(p, (expired_time.timestamp(), expired_time.timestamp()))

 # Audio
 a = media_dir / f"audio_{i}.wav"
 a.write_bytes(b"MOCK_WAV_CONTENT")
 os.utime(a, (expired_time.timestamp(), expired_time.timestamp()))

 # 2. Create fresh transient media files (younger than 48 hours)
 for i in range(5):
 p = media_dir / f"frame_fresh_{i}.jpg"
 p.write_bytes(b"MOCK_JPEG_CONTENT")

 # 3. Create compliance record files inside compliance_dir (also older than 48 hours)
 # These MUST survive pruning regardless of timestamps
 for i in range(10):
 j = compliance_dir / f"audit_record_{i}.json"
 j.write_text('{"audit_id": "test"}', encoding="utf-8")
 os.utime(j, (expired_time.timestamp(), expired_time.timestamp()))

 c = compliance_dir / f"compliance_ledger_{i}.csv"
 c.write_text("timestamp,audit_id,status\n", encoding="utf-8")
 os.utime(c, (expired_time.timestamp(), expired_time.timestamp()))

 # Initialize pruner
 pruner = MediaPruner(
 media_dir=str(media_dir),
 sensor_logs_dir=str(logs_dir),
 compliance_dir=str(compliance_dir),
 retention_hours=48,
 critical_disk_usage_pct=85.0,
 )

 # Execute pruning cycle
 deleted_media = await pruner.prune_old_media()

 # Assertions
 # 10 JPEGs + 10 WAVs should be pruned
 assert deleted_media == 20

 # Check remaining media: only fresh files should exist
 remaining_media = [f.name for f in media_dir.glob("*")]
 assert len(remaining_media) == 5
 for f in remaining_media:
 assert "fresh" in f

 # Check compliance files: all 10 JSONs + 10 CSVs must remain fully intact!
 remaining_compliance = [f.name for f in compliance_dir.glob("*")]
 assert len(remaining_compliance) == 20
