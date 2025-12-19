# import libs
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List, Any
import numpy as np


class AntoineFitResult(BaseModel):
    A: Optional[float] = None
    B: Optional[float] = None
    C: Optional[float] = None
    base: Optional[str] = None
    p_unit: str = "pa"
    T_unit_internal: str = "K"
    fit_in_log_space: bool = False
    success: bool = False
    message: str = ""
    cost: Optional[float] = None
    rmse_logP: Optional[float] = None
    mae_logP: Optional[float] = None
    r2_logP: Optional[float] = None
    rmse_P: Optional[float] = None
    mae_P: Optional[float] = None
    cov: Optional[Any] = None
    warnings: List[str] = Field(default_factory=list)
    Tmin_K: Optional[float] = None
    Tmax_K: Optional[float] = None
    loss: Optional[Any] = None
    f_scale: Optional[float] = None

    @field_validator("*", mode="before")
    def _convert_numpy_types(cls, v):
        if isinstance(v, (np.floating, np.integer)):
            return v.item()
        if isinstance(v, np.ndarray):
            return v.tolist()
        return v

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="allow",
        from_attributes=True,
    )
