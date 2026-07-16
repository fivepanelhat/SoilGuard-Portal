"""
main.py - SoilGuard Portal with Full Data Flywheel Integration

Hardware outcomes are now recorded to the flywheel after every enforcement.
"""

import asyncio
import logging
import signal
import uuid
from datetime import datetime

from coastal_alpine_core.portal_core.config import load_soilguard_config, print_config
from coastal_alpine_core.portal_core.ai_agent import AIAgent
from coastal_alpine_core.portal_core.mqtt_client import MQTTClient
from coastal_alpine_core.portal_core.av_capture import AVCapture
from coastal_alpine_core.portal_core.hardware_control import HardwareController
from coastal_alpine_core.portal_core.media_pruner import MediaPruner
from coastal_alpine_core.portal_core.compliance_exporter import ComplianceExporter
from portal_schemas.compliance import ComplianceRecord

from coastal_alpine_core import DataFlywheel

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("SoilGuardPortal.Orchestrator")


class SoilGuardPortal:
    def __init__(self, config):
        self.config = config

        # Initialize DataFlywheel
        self.flywheel = DataFlywheel(storage_path="flywheel_soilguard.jsonl")

        self.ai_agent = AIAgent(
            ollama_host=config.ollama.host,
            model=config.ollama.model,
            flywheel=self.flywheel,
        )
        self.mqtt_client = MQTTClient(
            broker_host=config.mqtt.broker,
            broker_port=config.mqtt.port,
            topic_prefix=config.mqtt.topic_prefix,
            username=config.mqtt.username,
            password=config.mqtt.password,
        )
        self.av_capture = AVCapture(
            camera_index=config.camera.device_index,
            video_fps=config.camera.fps,
            audio_sample_rate=config.audio.sample_rate,
            audio_chunk_size=config.audio.chunk_size,
        )
        self.hardware_control = HardwareController(
            irrigation_gpio_pin=config.hardware.irrigation_gpio_pin,
            nutrient_gpio_pin=config.hardware.nutrient_gpio_pin,
            fan_gpio_pin=config.hardware.fan_gpio_pin,
            alert_gpio_pin=config.hardware.alert_gpio_pin,
            enable_hardware_control=config.hardware.enable_hardware_control,
        )
        self.media_pruner = MediaPruner(
            media_dir=str(config.storage.media_dir),
            sensor_logs_dir=str(config.storage.sensor_logs_dir),
            compliance_dir=str(config.storage.compliance_dir),
            retention_hours=config.storage.retention_hours,
            critical_disk_usage_pct=config.storage.critical_disk_usage_pct,
        )
        self.compliance_exporter = ComplianceExporter(
            compliance_dir=str(config.storage.compliance_dir)
        )

        self.latest_metrics = {
            "moisture": 25.0, "temperature": 18.0, "electrical_conductivity": 0.8,
            "pH": 6.2, "nitrogen": 15.0, "phosphorus": 22.0, "potassium": 150.0,
        }
        self.is_running = False
        logger.info("SoilGuard Portal initialized with full Data Flywheel support.")

    async def evaluation_control_loop(self):
        while self.is_running:
            try:
                await asyncio.sleep(15)

                sensor_analysis = await self.ai_agent.analyze_sensor_state(self.latest_metrics)
                frame, audio = await asyncio.gather(
                    self.av_capture.capture_frame(),
                    self.av_capture.capture_audio_chunk(),
                )
                visual_analysis, audio_analysis = await asyncio.gather(
                    self.ai_agent.process_visual_feedback(frame),
                    self.ai_agent.process_audio_feedback(audio),
                )

                plan = await self.ai_agent.generate_optimization_plan(
                    sensor_analysis, visual_analysis, audio_analysis
                )

                # Enforce + record to flywheel
                enforcement_ok = await self.hardware_control.enforce_plan(plan)

                if plan:
                    action = plan.get("irrigation_action") or plan.get("nutrient_action") or plan.get("fan_action") or "unknown"
                    self.ai_agent.record_hardware_result(
                        plan_id=plan.get("plan_id", "unknown"),
                        action=action,
                        success=enforcement_ok,
                        metadata=plan
                    )

                if enforcement_ok:
                    logger.info("Enforced optimization plan actions successfully.")
                else:
                    logger.error("Plan actions enforcement failed.")

                # ... compliance recording logic unchanged ...

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in evaluation execution loop: {e}", exc_info=True)

    # ... other methods remain the same ...
