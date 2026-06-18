"""
SoilGuard Portal - AI Agent with Full Data Flywheel Integration

Integrated with Coastal Alpine Core SecurityGuard, TelemetryTracker, and DataFlywheel.
"""

import asyncio
import json
import logging
import re
from typing import Optional
from datetime import datetime
import uuid

from coastal_alpine_core import SovereignOllamaClient
from coastal_alpine_core.security import SecurityGuard, SecurityResult
from coastal_alpine_core.telemetry import TelemetryTracker
from coastal_alpine_core.flywheel import DataFlywheel, Trajectory

logger = logging.getLogger(__name__)
security_guard = SecurityGuard()


class AIAgent:
    def __init__(self, ollama_host: str = "http://localhost:11434", model: str = "gemma4:e4b", flywheel: Optional[DataFlywheel] = None):
        self.ollama_host = ollama_host
        self.model = model
        self.client = SovereignOllamaClient(host=ollama_host, default_model=model)
        self.flywheel = flywheel or DataFlywheel(storage_path="flywheel_soilguard.jsonl")
        logger.info("SoilGuard AI Agent initialized with full Data Flywheel support")

    async def generate_optimization_plan(self, sensor_analysis: dict, visual_analysis: dict, audio_analysis: dict) -> dict:
        inputs_str = f"Sensors: {sensor_analysis}, Vision: {visual_analysis}, Audio: {audio_analysis}"
        sec_result: SecurityResult = security_guard.check_prompt(inputs_str)
        if not sec_result.is_safe:
            logger.warning(f"Blocked by SecurityGuard: {sec_result.reason}")
            return self._generate_default_plan()

        measurement = TelemetryTracker.measure_latency("generate_optimization_plan")

        try:
            prompt = f"""SoilGuard Controller: Formulate a hardware actuation plan based on this state.
Sensors Analysis: {str(sensor_analysis)}
Canopy Visuals Ingestion: {str(visual_analysis)}
Acoustic Watchdog: {str(audio_analysis)}

Respond ONLY with a JSON object fitting this schema:
{{
  "plan_id": "opt-soil-YYYYMMDD-count",
  "irrigation_action": "off|low|medium|high",
  "nutrient_action": "off|low|medium|high",
  "fan_action": "off|low|medium|high",
  "confidence_score": 0.9,
  "logistical_notes": "operational reasoning",
  "execution_window_minutes": 15,
  "requires_human_review": false
}}"""
            response = await asyncio.wait_for(
                asyncio.to_thread(self.client.generate, prompt, model=self.model),
                timeout=60.0,
            )

            text = response.get("response", "").strip()
            json_match = re.search(r"\{.*\}", text, re.DOTALL)
            
            if json_match:
                plan_data = json.loads(json_match.group())
                
                from portal_schemas.compliance import SoilOptimizationPlan, IrrigationAction, NutrientAction, FanAction
                
                # Check actions match allowed Enums
                irrigation = plan_data.get("irrigation_action", "off").lower()
                if irrigation not in ["off", "low", "medium", "high"]:
                    irrigation = "off"
                plan_data["irrigation_action"] = IrrigationAction(irrigation)

                nutrient = plan_data.get("nutrient_action", "off").lower()
                if nutrient not in ["off", "low", "medium", "high"]:
                    nutrient = "off"
                plan_data["nutrient_action"] = NutrientAction(nutrient)

                fan = plan_data.get("fan_action", "off").lower()
                if fan not in ["off", "low", "medium", "high"]:
                    fan = "off"
                plan_data["fan_action"] = FanAction(fan)

                # Validate with Pydantic SoilOptimizationPlan
                validated = SoilOptimizationPlan(**plan_data)
                plan = validated.dict()
            else:
                logger.warning("AI optimization plan did not return structured JSON. Reverting to safe defaults.")
                return self._generate_default_plan()

            # === FULL FLYWHEEL INTEGRATION ===
            try:
                traj = Trajectory(
                    trajectory_id=str(uuid.uuid4()),
                    timestamp=datetime.now().isoformat(),
                    action="generate_optimization_plan",
                    input_summary=str(sensor_analysis)[:200],
                    output_summary=str(plan)[:300],
                    outcome="success",
                    latency_seconds=0.0,
                    estimated_energy_joules=0.0,
                    metadata={
                        "plan_id": plan.get("plan_id"),
                        "requires_human_review": plan.get("requires_human_review", False)
                    }
                )
                self.flywheel.record_trajectory(traj)
            except Exception as e:
                logger.warning(f"Flywheel recording failed: {e}")

            TelemetryTracker.complete_measurement(measurement, include_system_metrics=True)
            return plan

        except Exception as e:
            logger.error(f"Error generating optimization plan: {e}")
            return self._generate_default_plan()

    def record_hardware_result(self, plan_id: str, action: str, success: bool, **kwargs):
        """Call this after hardware enforcement (irrigation, nutrient, fan, etc.)."""
        self.flywheel.record_hardware_outcome(plan_id, action, success, **kwargs)

    def _generate_default_plan(self) -> dict:
        from portal_schemas.compliance import SoilOptimizationPlan, IrrigationAction, NutrientAction, FanAction
        default_plan = SoilOptimizationPlan(
            plan_id=f"opt-soil-default-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            irrigation_action=IrrigationAction.MEDIUM,
            nutrient_action=NutrientAction.OFF,
            fan_action=FanAction.MEDIUM,
            confidence_score=0.5,
            logistical_notes="Safe fallback parameters applied due to system exception or prompt blocking.",
            execution_window_minutes=30,
            requires_human_review=True
        )
        return default_plan.dict()
