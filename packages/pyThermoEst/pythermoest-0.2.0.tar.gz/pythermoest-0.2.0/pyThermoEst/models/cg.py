# import libs
from typing import Optional, Dict
from pydantic import BaseModel, Field, ConfigDict
# local
from .ref import GroupUnit

# SECTION: Constantinou-Gani Group Contribution


class ConstantinouGaniGroupContribution(BaseModel):
    """Constantinou-Gani Group Contribution Model Parameters"""

    model_config = ConfigDict(
        title="Constantinou-Gani Group Contribution Model Parameters",
        populate_by_name=True,
        extra="forbid",
    )
