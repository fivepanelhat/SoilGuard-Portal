"""
portal_core/hardware_control.py - Hardware Control Module for SoilGaurd Portal.

Manages GPIO/PWM controllers for irrigation, nutrient fertigation injection, and ventilation fans.
Includes full software simulation fallbacks for development/test loops.
"""

import asyncio
import logging
from typing import Optional, List, Dict
from datetime import datetime
from portal_schemas.compliance import IrrigationAction, NutrientAction, FanAction

logger = logging.getLogger(__name__)

# Attempt importing physical GPIO module
try:
    import RPi.GPIO as GPIO  # type: ignore
    ENABLE_GPIO = True
except ImportError:
    ENABLE_GPIO = False
    logger.warning("RPi.GPIO is unavailable; hardware control will operate in simulation mode.")


class HardwareControl:
    """
    Manages GPIO states for:
    - Irrigation flow (PWM duty cycles)
    - Nutrient fertigation injection pump (PWM duty cycles)
    - Ventilation fan speed (PWM duty cycles)
    - Alert Relay / Warning Siren (digital high/low)
    """

    def __init__(
        self,
        irrigation_gpio_pin: Optional[int] = None,
        nutrient_gpio_pin: Optional[int] = None,
        fan_gpio_pin: Optional[int] = None,
        alert_gpio_pin: Optional[int] = None,
        enable_hardware_control: bool = False,
    ):
        self.irrigation_gpio_pin = irrigation_gpio_pin
        self.nutrient_gpio_pin = nutrient_gpio_pin
        self.fan_gpio_pin = fan_gpio_pin
        self.alert_gpio_pin = alert_gpio_pin

        # Enforce simulation mode if GPIO libraries are missing
        self.simulation_mode = not enable_hardware_control or not ENABLE_GPIO

        # Active state registers
        self.irrigation_state = IrrigationAction.OFF
        self.irrigation_duty_cycle = 0
        self.nutrient_state = NutrientAction.OFF
        self.nutrient_duty_cycle = 0
        self.fan_state = FanAction.OFF
        self.fan_duty_cycle = 0

        # PWM references
        self.irrigation_pwm = None
        self.nutrient_pwm = None
        self.fan_pwm = None

        # Auditing log trail
        self.action_history: List[Dict] = []

        logger.info(
            f"Hardware Control configured: irrigation_pin={irrigation_gpio_pin}, nutrient_pin={nutrient_gpio_pin}, "
            f"fan_pin={fan_gpio_pin}, alert_pin={alert_gpio_pin}, simulation={self.simulation_mode}"
        )

    async def setup(self):
        """Initialise hardware pins and default low signals."""
        if self.simulation_mode:
            logger.info("Hardware Control setup finished in simulation mode.")
            return

        try:
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)

            if self.irrigation_gpio_pin:
                GPIO.setup(self.irrigation_gpio_pin, GPIO.OUT)
                self.irrigation_pwm = GPIO.PWM(self.irrigation_gpio_pin, 1000)
                self.irrigation_pwm.start(0)
                logger.info(f"Irrigation GPIO pin {self.irrigation_gpio_pin} setup with PWM.")

            if self.nutrient_gpio_pin:
                GPIO.setup(self.nutrient_gpio_pin, GPIO.OUT)
                self.nutrient_pwm = GPIO.PWM(self.nutrient_gpio_pin, 1000)
                self.nutrient_pwm.start(0)
                logger.info(f"Nutrient fertigation GPIO pin {self.nutrient_gpio_pin} setup with PWM.")

            if self.fan_gpio_pin:
                GPIO.setup(self.fan_gpio_pin, GPIO.OUT)
                self.fan_pwm = GPIO.PWM(self.fan_gpio_pin, 1000)
                self.fan_pwm.start(0)
                logger.info(f"Ventilation fan GPIO pin {self.fan_gpio_pin} setup with PWM.")

            if self.alert_gpio_pin:
                GPIO.setup(self.alert_gpio_pin, GPIO.OUT)
                GPIO.output(self.alert_gpio_pin, GPIO.LOW)
                logger.info(f"Alert GPIO pin {self.alert_gpio_pin} setup.")

            logger.info("✓ Hardware Control Setup successfully.")
        except Exception as e:
            logger.error(f"✗ Failed setting up GPIO pins: {e}. Enabling simulation fallback.")
            self.simulation_mode = True

    async def cleanup(self):
        """Reset pin outputs and shutdown PWM clocks."""
        if self.simulation_mode or not ENABLE_GPIO:
            return

        try:
            if self.irrigation_pwm:
                self.irrigation_pwm.stop()
            if self.nutrient_pwm:
                self.nutrient_pwm.stop()
            if self.fan_pwm:
                self.fan_pwm.stop()
            GPIO.cleanup()
            logger.info("GPIO cleanup finished successfully.")
        except Exception as e:
            logger.error(f"Error executing GPIO cleanup: {e}")

    async def set_irrigation(self, state: IrrigationAction) -> bool:
        try:
            duty_map = {
                IrrigationAction.OFF: 0,
                IrrigationAction.LOW: 30,
                IrrigationAction.MEDIUM: 60,
                IrrigationAction.HIGH: 100
            }
            dc = duty_map.get(state, 0)
            self.irrigation_state = state
            self.irrigation_duty_cycle = dc

            if self.simulation_mode:
                logger.info(f"[SIM] Irrigation state -> {state.value} (PWM {dc}%)")
            else:
                if self.irrigation_pwm:
                    self.irrigation_pwm.ChangeDutyCycle(dc)
                    logger.info(f"Irrigation state -> {state.value} (PWM {dc}%)")

            self._record_action("irrigation", state.value, dc)
            return True
        except Exception as e:
            logger.error(f"Error setting irrigation output: {e}")
            return False

    async def set_nutrient(self, state: NutrientAction) -> bool:
        try:
            duty_map = {
                NutrientAction.OFF: 0,
                NutrientAction.LOW: 33,
                NutrientAction.MEDIUM: 66,
                NutrientAction.HIGH: 100
            }
            dc = duty_map.get(state, 0)
            self.nutrient_state = state
            self.nutrient_duty_cycle = dc

            if self.simulation_mode:
                logger.info(f"[SIM] Nutrient pump state -> {state.value} (PWM {dc}%)")
            else:
                if self.nutrient_pwm:
                    self.nutrient_pwm.ChangeDutyCycle(dc)
                    logger.info(f"Nutrient pump state -> {state.value} (PWM {dc}%)")

            self._record_action("nutrient", state.value, dc)
            return True
        except Exception as e:
            logger.error(f"Error setting nutrient pump output: {e}")
            return False

    async def set_fan(self, state: FanAction) -> bool:
        try:
            duty_map = {
                FanAction.OFF: 0,
                FanAction.LOW: 33,
                FanAction.MEDIUM: 66,
                FanAction.HIGH: 100
            }
            dc = duty_map.get(state, 0)
            self.fan_state = state
            self.fan_duty_cycle = dc

            if self.simulation_mode:
                logger.info(f"[SIM] Ventilation Fan state -> {state.value} (PWM {dc}%)")
            else:
                if self.fan_pwm:
                    self.fan_pwm.ChangeDutyCycle(dc)
                    logger.info(f"Ventilation Fan state -> {state.value} (PWM {dc}%)")

            self._record_action("fan", state.value, val=dc)
            return True
        except Exception as e:
            logger.error(f"Error setting ventilation fan output: {e}")
            return False

    async def trigger_alert(self, duration_ms: int = 500):
        try:
            if self.simulation_mode:
                logger.warning(f"[SIM] Alert relay triggered for {duration_ms}ms.")
            else:
                if self.alert_gpio_pin:
                    GPIO.output(self.alert_gpio_pin, GPIO.HIGH)
                    await asyncio.sleep(duration_ms / 1000.0)
                    GPIO.output(self.alert_gpio_pin, GPIO.LOW)
                    logger.warning(f"Alert relay triggered for {duration_ms}ms.")

            self._record_action("alert", "triggered", duration_ms)
        except Exception as e:
            logger.error(f"Error triggering alert pin: {e}")

    async def enforce_plan(self, plan: dict) -> bool:
        """
        Translates a Pydantic-validated SoilOptimizationPlan dict into pin signals.
        """
        try:
            logger.info(f"Enforcing action plan: {plan.get('plan_id', 'unknown')}")
            
            irrigation_action = plan.get("irrigation_action")
            nutrient_action = plan.get("nutrient_action")
            fan_action = plan.get("fan_action")

            success = True

            if irrigation_action:
                state = IrrigationAction(irrigation_action.lower() if isinstance(irrigation_action, str) else irrigation_action)
                ok = await self.set_irrigation(state)
                success = success and ok

            if nutrient_action:
                state = NutrientAction(nutrient_action.lower() if isinstance(nutrient_action, str) else nutrient_action)
                ok = await self.set_nutrient(state)
                success = success and ok

            if fan_action:
                state = FanAction(fan_action.lower() if isinstance(fan_action, str) else fan_action)
                ok = await self.set_fan(state)
                success = success and ok

            if plan.get("requires_human_review"):
                await self.trigger_alert(1000)

            logger.info(f"Plan enforcement concluded with status: {success}")
            return success
        except Exception as e:
            logger.error(f"Error executing plan enforcement: {e}")
            return False

    def _record_action(self, device: str, action: str, val: int):
        self.action_history.append({
            "timestamp": datetime.now().isoformat(),
            "device": device,
            "action": action,
            "value": val
        })
        if len(self.action_history) > 1000:
            self.action_history.pop(0)

    def get_status(self) -> dict:
        return {
            "irrigation": {
                "state": self.irrigation_state.value,
                "duty_cycle_pct": self.irrigation_duty_cycle
            },
            "nutrient": {
                "state": self.nutrient_state.value,
                "duty_cycle_pct": self.nutrient_duty_cycle
            },
            "fan": {
                "state": self.fan_state.value,
                "duty_cycle_pct": self.fan_duty_cycle
            },
            "simulation_mode": self.simulation_mode,
            "timestamp": datetime.now().isoformat()
        }

    async def health_check(self) -> bool:
        if not self.simulation_mode:
            return bool(self.irrigation_gpio_pin or self.nutrient_gpio_pin or self.fan_gpio_pin)
        return True
