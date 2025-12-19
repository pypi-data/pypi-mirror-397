# import libs
from typing import Optional, Dict
from pydantic import BaseModel, Field, ConfigDict
# local
from .ref import GroupUnit

# SECTION: Zabransky-Ruzicka Group Contributions


class ZabranskyRuzickaGroupContributions(BaseModel):
    """Zabransky-Ruzicka group contribution identifiers and their corresponding contributions to thermodynamic properties."""
    model_config = ConfigDict(populate_by_name=True, extra='forbid')

    C_H_3_C: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0),
        alias="C-(H)3(C)"
    )
    C_H_2_C_2: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(H)2(C)2")
    C_H_C_3: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(H)(C)3")
    C_C_4: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(C)4")
    Cd_H_2: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="Cd-(H)2")
    Cd_H_C: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="Cd-(H)(C)")
    Cd_C_2: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="Cd-(C)2")
    Cd_H_Cd: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="Cd-(H)(Cd)")
    Cd_C_Cd: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="Cd-(C)(Cd)")
    C_H_2_C_Cd: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(H)2(C)(Cd)")
    C_H_2_Cd_2: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(H)2(Cd)2")
    C_H_C_2_Cd: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(H)(C)2(Cd)")
    C_C_3_Cd: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(C)3(Cd)")
    Ct_H: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="Ct-(H)")
    Ct_C: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="Ct-(C)")
    Ct_CB: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="Ct-(CB)")
    Ca: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="Ca")
    CB_H: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="CB-(H)")
    CB_C: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="CB-(C)")
    CB_Cd: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="CB-(Cd)")
    CB_CB: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="CB-(CB)")
    C_H_2_C_CB: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(H)2(C)(CB)")
    C_H_2_CB_2: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(H)2(CB)2")
    C_H_C_2_CB: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(H)(C)2(CB)")
    C_H_CB_3: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(H)(CB)3")
    C_C_3_CB: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(C)3(CB)")
    CBF_CBF_CB_2: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="CBF-(CBF)(CB)2")
    CBF_CBF_2_CB: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="CBF-(CBF)2(CB)")
    CBF_CBF_3: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="CBF-(CBF)3")
    C_H_3_O: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(H)3(O)")
    C_H_2_O_2: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(H)2(O)2")
    C_H_2_C_O: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(H)2(C)(O)")
    C_H_2_C_CO: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(H)2(C)(CO)")
    C_H_2_CO_2: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(H)2(CO)2")
    C_H_2_CB_O: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(H)2(CB)(O)")
    C_H_C_2_O: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(H)(C)2(O)")
    C_H_C_2_O_v2: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(H)(C)2(O)")
    C_H_C_2_CO: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(H)(C)2(CO)")
    C_C_2_O_2: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(C)2(O)2")
    C_C_3_O_ether: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(C)3(O)-ether")
    C_C_3_O_alcohol: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(C)3(O)-alcohol")
    C_C_3_CO: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(C)3(CO)")
    Cd_H_CO: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="Cd-(H)(CO)")
    Cd_C_CO: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="Cd-(C)(CO)")
    CB_CB_2_O: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="CB-(CB)2(O)")
    CB_CB_2_CO: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="CB-(CB)2(CO)")
    CO_H_C: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="CO-(H)(C)")
    CO_H_Cd: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="CO-(H)(Cd)")
    CO_C_2: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="CO-(C)2")
    CO_C_Cd: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="CO-(C)(Cd)")
    CO_C_CB: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="CO-(C)(CB)")
    CO_H_O: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="CO-(H)(O)")
    CO_C_O: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="CO-(C)(O)")
    CO_Cd_O: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="CO-(Cd)(O)")
    CO_CB_O: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="CO-(CB)(O)")
    CO_O_CO: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="CO-(O)(CO)")
    CO_O_2: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="CO-(O)2")
    O_H_C: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="O-(H)(C)")
    O_H_C_diol: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="O-(H)(C)-diol")
    O_H_CB: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="O-(H)(CB)")
    O_H_CO: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="O-(H)(CO)")
    O_C_2: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="O-(C)2")
    O_C_2_alcohol: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="O-(C)2-alcohol")
    O_C_Cd: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="O-(C)(Cd)")
    O_C_CB: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="O-(C)(CB)")
    O_CB_2: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="O-(CB)2")
    O_C_CO: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="O-(C)(CO)")
    O_Cd_CO: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="O-(Cd)(CO)")
    C_H_3_N: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(H)3(N)")
    C_H_2_C_N: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(H)2(C)(N)")
    C_H_C_2_N: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(H)(C)2(N)")
    C_C_3_N: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(C)3(N)")
    CB_CB_2_N: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="CB-(CB)2(N)")
    N_H_2_C: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="N-(H)2(C)")
    N_H_2_N: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="N-(H)2(N)")
    N_H_C_2: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="N-(H)(C)2")
    N_H_C_CB: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="N-(H)(C)(CB)")
    N_H_C_N: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="N-(H)(C)(N)")
    N_H_CB_N: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="N-(H)(CB)(N)")
    N_H_CB_2_pyrrole: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="N-(H)(CB)2-pyrrole")
    N_C_3: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="N-(C)3")
    N_C_2_CB: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="N-(C)2(CB)")
    N_C_2_N: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="N-(C)2(N)")
    NB_CB_2: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="NB-(CB)2")
    C_H_2_C_CN: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(H)2(C)(CN)")
    C_C_3_CN: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(C)3(CN)")
    Cd_H_CN: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="Cd-(H)(CN)")
    CB_CB_2_CN: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="CB-(CB)2(CN)")
    CB_NCO_isocyanate: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="CB-(NCO)-isocyanate")
    CB_CB_2_NO2: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="CB-(CB)2(NO2)")
    C_H_2_C_NO2: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(H)2(C)(NO2)")
    O_C_NO2: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="O-(C)(NO2)")
    C_H_2_C_Br: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(H)2(C)(Br)")
    C_H_2_C_Cl: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(H)2(C)(C1)")
    C_H_2_CB_Cl: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(H)2(CB)(C1)")
    C_H_2_C_F: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(H)2(C)(F)")
    C_H_2_C_I: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(H)2(C)(I)")
    C_H_C_2_Br: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(H)(C)2(Br)")
    C_H_C_2_Cl: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(H)(C)2(C1)")
    C_H_C_Cl_2: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(H)(C)(C1)2")
    C_H_C_Cl_F: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(H)(C)(C1)(F)")
    C_H_C_F_2: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(H)(C)(F)2")
    C_C_Br_F_2: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(C)(Br)(F)2")
    C_C_3_Cl: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(C)3(C1)")
    C_C_2_Cl_2: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(C)2(C1)2")
    C_C_Cl_3: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(C)(C1)3")
    C_C_Cl_F_2: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(C)(C1)(F)2")
    C_C_Cl_2_F: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(C)(C1)2(F)")
    C_C_2_F_2: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(C)2(F)2")
    C_C_F_3: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(C)(F)3")
    C_CB_F_3: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(CB)(F)3")
    Cd_H_Cl: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="Cd-(H)(C1)")
    Cd_Cl_F: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="Cd-(C1)(F)")
    Cd_Cl_2: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="Cd-(C1)2")
    Cd_F_2: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="Cd-(F)2")
    CB_CB_2_Br: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="CB-(CB)2(Br)")
    CB_CB_2_Cl: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="CB(CB)2(C1)")
    CB_CB_2_F: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="CB-(CB)2(F)")
    CB_CB_2_I: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="CB-(CB)2(I)")
    C_H_3_S: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(H)3(S)")
    C_H_2_C_S: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(H)2(C)(S)")
    C_H_C_2_S: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(H)(C)2(S)")
    C_C_3_S: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="C-(C)3(S)")
    CB_CB_2_S: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="CB-(CB)2(S)")
    S_H_C: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="S-(H)(C)")
    S_C_2: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="S-(C)2")
    S_CB_C: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="S-(CB)(C)")
    S_CB_2_thiophene: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="S-(CB)2-thiophene")
    S_C_S: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="S-(C)(S)")


class ZabranskyRuzickaGroupContributionsCorrections(BaseModel):
    """Zabransky-Ruzicka group contribution correction identifiers and their corresponding corrections to thermodynamic properties."""
    model_config = ConfigDict(populate_by_name=True, extra='forbid')

    CYCLOPROPANEA: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="Cyclopropanea")
    CYCLOBUTANE: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="Cyclobutane")
    CYCLOPENTANE: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="Cyclopentane")
    CYCLOHEXANE: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="Cyclohexane")
    CYCLOHEPTANEA: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="Cycloheptanea")
    CYCLOOCTANEA: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="Cyclooctanea")
    CYCLOPENTENE: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="Cyclopentene")
    CYCLOHEXENE: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="Cyclohexene")
    CYCLOHEXADIENE: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="Cyclohexadiene")
    INDAN: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="Indan")
    G_1H_INDENEA: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="1H-indenea")
    HEXAHYDROINDAN: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="Hexahydroindan")
    TETRAHYDRONAPHTHALENEA: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="Tetrahydronaphthalenea")
    DECAHYDRONAPHTHALENE: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="Decahydronaphthalene")
    ETHYLENEOXIDE: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="Ethyleneoxide")
    G_1_3_DIOXOLANE: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="1,3-Dioxolane")
    FURAN: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="Furan")
    TETRAHYDROFURAN: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="Tetrahydrofuran")
    TETRAHYDROPYRAN: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="Tetrahydropyran")
    PYRROLIDINE: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="Pyrrolidine")
    PIPERIDINE: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="Piperidine")
    THIACYCLOBUTANEA: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="Thiacyclobutanea")
    THIACYCLOPENTANE: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="Thiacyclopentane")
    THIACYCLOHEXANEA: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="Thiacyclohexanea")
    CIS: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="Cis-")
    TRANS: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="Trans-")
    ORTHO: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="Ortho-")
    META: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0), alias="Meta-")


class ZabranskyRuzickaGroupData(BaseModel):
    """A class to represent a Zabransky Ruzicka group with its name and contribution data."""
    id: str
    name: str
    count: float
    data: Dict[str, str]
