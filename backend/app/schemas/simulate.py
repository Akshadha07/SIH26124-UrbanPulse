from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class ScenarioTriggerRequest(BaseModel):
    intensity: Optional[float] = Field(default=1.0, ge=0.1, le=5.0, description="Multiplier for scenario severity/traffic")
    corridor: Optional[str] = Field(default=None, description="Optional target corridor (e.g. 'Akota Underpass', 'Sayajigunj')")

class ScenarioResponse(BaseModel):
    status: str = "activated"
    scenario_name: str
    active: bool
    description: str
    simulation_run_id: str
    affected_corridors: List[str]
    parameters: Dict[str, Any]

class ResetResponse(BaseModel):
    status: str = "reset_complete"
    previous_simulation_run_id: Optional[str]
    new_simulation_run_id: str
    archived_simulated_events_count: int
    archived_simulated_telemetry_count: int
    active_buses_count: int
    message: str = "Simulation environment reset successfully. Non-simulated records preserved."

class SimulationStatusResponse(BaseModel):
    simulation_run_id: str
    is_running: bool
    bus_count: int
    interval_seconds: float
    active_scenario: Optional[str]
    seed: int
    total_ticks: int
