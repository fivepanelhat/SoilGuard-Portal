"""
portal_schemas - Exports schemas for SoilGuard Portal.
"""

from .compliance import (
    IrrigationAction,
    NutrientAction,
    FanAction,
    SoilSensorReading,
    SoilAnalysisResult,
    SoilOptimizationPlan,
    ComplianceRecord,
)

__all__ = [
    "IrrigationAction",
    "NutrientAction",
    "FanAction",
    "SoilSensorReading",
    "SoilAnalysisResult",
    "SoilOptimizationPlan",
    "ComplianceRecord",
]
