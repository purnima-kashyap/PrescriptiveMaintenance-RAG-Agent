from pydantic import BaseModel, Field


class IoTAlert(BaseModel):
    machine_id: str = Field(..., example="PUMP-01")
    error_code: str = Field(..., example="E-404")
    temperature: float = Field(..., example=105)