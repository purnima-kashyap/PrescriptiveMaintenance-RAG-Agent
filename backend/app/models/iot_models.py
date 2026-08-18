
from pydantic import BaseModel, Field, field_validator

class IoTAlert(BaseModel):
    # Using 'examples' instead of 'example' to comply with Pydantic V2 standards
    machine_id: str = Field(..., description="Unique identifier for the machine", examples=["PUMP-01"])
    error_code: str = Field(..., description="Standardized factory error code", examples=["E-404"])
    temperature: float = Field(..., description="Current temperature reading in Celsius", examples=[105.0])
    vibration: float = Field(..., description="Current vibration reading in mm/s", examples=[7.5])
    pressure: float = Field(..., description="Current pressure reading in psi", examples=[120.0])
    severity: str = Field(..., description="Alert severity level (e.g., Low, Medium, High)", examples=["High"])

    @field_validator('temperature')
    @classmethod
    def validate_temperature_bounds(cls, v: float) -> float:
        """
        Ensures the temperature is within realistic physical bounds for a machine.
        Prevents malfunctioning sensors from crashing the downstream logic.
        """
        # Adjust these thresholds based on the specific factory machinery wich are simulating
        if v < -50 or v > 1000:
            raise ValueError(f"Temperature reading {v}°C is outside realistic operational bounds. Check sensor.")
        return v

    @field_validator('error_code')
    @classmethod
    def validate_error_code_format(cls, v: str) -> str:
        """
        Ensures the error code follows the required hyphenated format.
        Automatically standardizes lowercase inputs to uppercase.
        """
        if "-" not in v:
            raise ValueError("Invalid error_code format. Expected a hyphenated code (e.g., 'E-404').")
        
        # This automatically cleans the data 
        return v.upper()