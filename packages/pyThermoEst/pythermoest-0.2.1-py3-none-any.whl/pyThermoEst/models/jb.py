# import libs
from typing import Optional, Dict, TypedDict, Callable
from pydantic import BaseModel, Field, ConfigDict

# local
from .ref import GroupUnit

# SECTION: Joback Group Contributions


class JobackGroupContributions(BaseModel):
    """Joback group contribution identifiers and their corresponding contributions to thermodynamic properties."""
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

    methyl: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0),
        description="Methyl group contribution.",
        alias="-CH3",
        json_schema_extra={
            "category": "non-ring increments", "group": "-CH3", "type": "normal", "id": "NR1", "Tc": 0.0141, "Pc": -0.0012, "Vc": 65.0, "Tb": 23.58, "Tf": -5.1, "EnFo_IG": -76.45, "GiEnFo_IG": -43.96, "a": 19.5, "b": -0.00808, "c": 0.000153, "d": -9.67e-08, "EnFus": 0.908, "EnVap": 2.373, "ηa": 548.29, "ηb": -1.719
        }
    )
    methylene: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0),
        description="Methylene group contribution.",
        alias="-CH2- @non-ring",
        json_schema_extra={
            "category": "non-ring increments", "group": "-CH2- @non-ring", "type": "normal", "id": "NR2", "Tc": 0.0189, "Pc": 0.0, "Vc": 56.0, "Tb": 22.88, "Tf": 11.27, "EnFo_IG": -20.64, "GiEnFo_IG": 8.42, "a": -0.909, "b": 0.095, "c": -5.44e-05, "d": 1.19e-08, "EnFus": 2.59, "EnVap": 2.226, "ηa": 94.16, "ηb": -0.199
        }
    )
    tertiary_CH: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0),
        description="Tertiary CH group contribution.",
        alias=">CH- @non-ring",
        json_schema_extra={
            "category": "non-ring increments", "group": ">CH- @non-ring", "type": "normal", "id": "NR3", "Tc": 0.0164, "Pc": 0.002, "Vc": 41.0, "Tb": 21.74, "Tf": 12.64, "EnFo_IG": 29.89, "GiEnFo_IG": 58.36, "a": -23.0, "b": 0.204, "c": -0.000265, "d": 1.2e-07, "EnFus": 0.749, "EnVap": 1.691, "ηa": -322.15, "ηb": 1.187
        }
    )
    quaternary_C: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0),
        description="Quaternary C group contribution.",
        alias=">C< @non-ring",
        json_schema_extra={
            "category": "non-ring increments", "group": ">C< @non-ring", "type": "normal", "id": "NR4", "Tc": 0.0067, "Pc": 0.0043, "Vc": 27.0, "Tb": 18.25, "Tf": 46.43, "EnFo_IG": 82.23, "GiEnFo_IG": 116.02, "a": -66.2, "b": 0.427, "c": -0.000641, "d": 3.01e-07, "EnFus": -1.46, "EnVap": 0.636, "ηa": -573.56, "ηb": 2.307
        }
    )
    vinyl_CH2: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0),
        description="Vinyl CH2 group contribution.",
        alias="=CH2",
        json_schema_extra={
            "category": "non-ring increments", "group": "=CH2", "type": "normal", "id": "NR5", "Tc": 0.0113, "Pc": -0.0028, "Vc": 56.0, "Tb": 18.18, "Tf": -4.32, "EnFo_IG": -9.63, "GiEnFo_IG": 3.77, "a": 23.6, "b": -0.0381, "c": 0.000172, "d": -1.03e-07, "EnFus": -0.473, "EnVap": 1.724, "ηa": 495.01, "ηb": -1.539
        }
    )
    vinyl_CH: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0),
        description="Vinyl CH group contribution.",
        alias="=CH- @non-ring",
        json_schema_extra={
            "category": "non-ring increments", "group": "=CH- @non-ring", "type": "normal", "id": "NR6", "Tc": 0.0129, "Pc": -0.0006, "Vc": 46.0, "Tb": 24.96, "Tf": 8.73, "EnFo_IG": 37.97, "GiEnFo_IG": 48.53, "a": -8.0, "b": 0.105, "c": -9.63e-05, "d": 3.56e-08, "EnFus": 2.691, "EnVap": 2.205, "ηa": 82.28, "ηb": -0.242
        }
    )
    vinyl_C: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0),
        description="Vinyl C group contribution.",
        alias="=C< @non-ring",
        json_schema_extra={
            "category": "non-ring increments", "group": "=C< @non-ring", "type": "normal", "id": "NR7", "Tc": 0.0117, "Pc": 0.0011, "Vc": 38.0, "Tb": 24.14, "Tf": 11.14, "EnFo_IG": 83.99, "GiEnFo_IG": 92.36, "a": -28.1, "b": 0.208, "c": -0.000306, "d": 1.46e-07, "EnFus": 3.063, "EnVap": 2.138, "ηa": 0.0, "ηb": 0.0
        }
    )
    allene: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0),
        description="Allene group contribution.",
        alias="=C=",
        json_schema_extra={
            "category": "non-ring increments", "group": "=C=", "type": "normal", "id": "NR8", "Tc": 0.0026, "Pc": 0.0028, "Vc": 36.0, "Tb": 26.15, "Tf": 17.78, "EnFo_IG": 142.14, "GiEnFo_IG": 136.7, "a": 27.4, "b": -0.0557, "c": 0.000101, "d": -5.02e-08, "EnFus": 4.72, "EnVap": 2.661, "ηa": 0.0, "ηb": 0.0
        }
    )
    alkyne_CH: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0),
        description="Alkyne CH group contribution.",
        alias="#CH",
        json_schema_extra={
            "category": "non-ring increments", "group": "#CH", "type": "normal", "id": "NR9", "Tc": 0.0027, "Pc": -0.0008, "Vc": 46.0, "Tb": 9.2, "Tf": -11.18, "EnFo_IG": 79.3, "GiEnFo_IG": 77.71, "a": 24.5, "b": -0.0271, "c": 0.000111, "d": -6.78e-08, "EnFus": 2.322, "EnVap": 1.155, "ηa": 0.0, "ηb": 0.0
        }
    )
    alkyne_C: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0),
        description="Alkyne C group contribution.",
        alias="#C-",
        json_schema_extra={
            "category": "non-ring increments", "group": "#C-", "type": "normal", "id": "NR10", "Tc": 0.002, "Pc": 0.0016, "Vc": 37.0, "Tb": 27.38, "Tf": 64.32, "EnFo_IG": 115.51, "GiEnFo_IG": 109.82, "a": 7.87, "b": 0.0201, "c": -8.33e-06, "d": 1.39e-09, "EnFus": 4.151, "EnVap": 3.302, "ηa": 0.0, "ηb": 0.0
        }
    )
    methylene_ring: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0),
        description="Methylene group contribution in ring.",
        alias="-CH2- @ring",
        json_schema_extra={
            "category": "ring increments", "group": "-CH2- @ring", "type": "normal", "id": "R1", "Tc": 0.01, "Pc": 0.0025, "Vc": 48.0, "Tb": 27.15, "Tf": 7.75, "EnFo_IG": -26.8, "GiEnFo_IG": -3.68, "a": -6.03, "b": 0.0854, "c": -8e-06, "d": -1.8e-08, "EnFus": 0.49, "EnVap": 2.398, "ηa": 307.53, "ηb": -0.798
        }
    )
    tertiary_CH_ring: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0),
        description="Tertiary CH group contribution in ring.",
        alias=">CH- @ring",
        json_schema_extra={
            "category": "ring increments", "group": ">CH- @ring", "type": "normal", "id": "R2", "Tc": 0.0122, "Pc": 0.0004, "Vc": 38.0, "Tb": 21.78, "Tf": 19.88, "EnFo_IG": 8.67, "GiEnFo_IG": 40.99, "a": -20.5, "b": 0.162, "c": -0.00016, "d": 6.24e-08, "EnFus": 3.243, "EnVap": 1.942, "ηa": -394.29, "ηb": 1.251
        }
    )
    quaternary_C_ring: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0),
        description="Quaternary C group contribution in ring.",
        alias=">C< @ring",
        json_schema_extra={
            "category": "ring increments", "group": ">C< @ring", "type": "normal", "id": "R3", "Tc": 0.0042, "Pc": 0.0061, "Vc": 27.0, "Tb": 21.32, "Tf": 60.15, "EnFo_IG": 79.72, "GiEnFo_IG": 87.88, "a": -90.9, "b": 0.557, "c": -0.0009, "d": 4.69e-07, "EnFus": -1.373, "EnVap": 0.644, "ηa": 0.0, "ηb": 0.0
        }
    )
    vinyl_CH_ring: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0),
        description="Vinyl CH group contribution in ring.",
        alias="=CH- @ring",
        json_schema_extra={
            "category": "ring increments", "group": "=CH- @ring", "type": "normal", "id": "R4", "Tc": 0.0082, "Pc": 0.0011, "Vc": 41.0, "Tb": 26.73, "Tf": 8.13, "EnFo_IG": 2.09, "GiEnFo_IG": 11.3, "a": -2.14, "b": 0.0574, "c": -1.64e-06, "d": -1.59e-08, "EnFus": 1.101, "EnVap": 2.544, "ηa": 259.65, "ηb": -0.702
        }
    )
    vinyl_C_ring: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0),
        description="Vinyl C group contribution in ring.",
        alias="=C< @ring",
        json_schema_extra={
            "category": "ring increments", "group": "=C< @ring", "type": "normal", "id": "R5", "Tc": 0.0143, "Pc": 0.0008, "Vc": 32.0, "Tb": 31.01, "Tf": 37.02, "EnFo_IG": 46.43, "GiEnFo_IG": 54.05, "a": -8.25, "b": 0.101, "c": -0.000142, "d": 6.78e-08, "EnFus": 2.394, "EnVap": 3.059, "ηa": -245.74, "ηb": 0.912
        }
    )
    fluorine: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0),
        description="Fluorine group contribution.",
        alias="-F",
        json_schema_extra={
            "category": "hologen increments", "group": "-F", "type": "normal", "id": "H1", "Tc": 0.0111, "Pc": -0.0057, "Vc": 27.0, "Tb": -0.03, "Tf": -15.78, "EnFo_IG": -251.92, "GiEnFo_IG": -247.19, "a": 26.5, "b": -0.0913, "c": 0.000191, "d": -1.03e-07, "EnFus": 1.398, "EnVap": -0.67, "ηa": 0.0, "ηb": 0.0
        }
    )
    chlorine: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0),
        description="Chlorine group contribution.",
        alias="-Cl",
        json_schema_extra={
            "category": "hologen increments", "group": "-Cl", "type": "normal", "id": "H2", "Tc": 0.0105, "Pc": -0.0049, "Vc": 58.0, "Tb": 38.13, "Tf": 13.55, "EnFo_IG": -71.55, "GiEnFo_IG": -64.31, "a": 33.3, "b": -0.0963, "c": 0.000187, "d": -9.96e-08, "EnFus": 2.515, "EnVap": 4.532, "ηa": 625.45, "ηb": -1.814
        }
    )
    bromine: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0),
        description="Bromine group contribution.",
        alias="-Br",
        json_schema_extra={
            "category": "hologen increments", "group": "-Br", "type": "normal", "id": "H3", "Tc": 0.0133, "Pc": 0.0057, "Vc": 71.0, "Tb": 66.86, "Tf": 43.43, "EnFo_IG": -29.48, "GiEnFo_IG": -38.06, "a": 28.6, "b": -0.0649, "c": 0.000136, "d": -7.45e-08, "EnFus": 3.603, "EnVap": 6.582, "ηa": 738.91, "ηb": -2.038
        }
    )
    iodine: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0),
        description="Iodine group contribution.",
        alias="-I",
        json_schema_extra={
            "category": "hologen increments", "group": "-I", "type": "normal", "id": "H4", "Tc": 0.0068, "Pc": -0.0034, "Vc": 97.0, "Tb": 93.84, "Tf": 41.69, "EnFo_IG": 21.06, "GiEnFo_IG": 5.74, "a": 32.1, "b": -0.0641, "c": 0.000126, "d": -6.87e-08, "EnFus": 2.724, "EnVap": 9.52, "ηa": 809.55, "ηb": -2.224
        }
    )
    alcohol_OH: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0),
        description="Alcohol OH group contribution.",
        alias="-OH @alcohol",
        json_schema_extra={
            "category": "oxygen increments", "group": "-OH @alcohol", "type": "alcohol", "id": "O1", "Tc": 0.0741, "Pc": 0.0112, "Vc": 28.0, "Tb": 92.88, "Tf": 44.45, "EnFo_IG": -208.04, "GiEnFo_IG": -189.2, "a": 25.7, "b": -0.0691, "c": 0.000177, "d": -9.88e-08, "EnFus": 2.406, "EnVap": 16.826, "ηa": 2173.72, "ηb": -5.057
        }
    )
    phenol_OH: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0),
        description="Phenol OH group contribution.",
        alias="-OH @phenol",
        json_schema_extra={
            "category": "oxygen increments", "group": "-OH @phenol", "type": "phenol", "id": "O2", "Tc": 0.024, "Pc": 0.0184, "Vc": -25.0, "Tb": 76.34, "Tf": 82.83, "EnFo_IG": -221.65, "GiEnFo_IG": -197.37, "a": -2.81, "b": 0.111, "c": -0.000116, "d": 4.94e-08, "EnFus": 4.49, "EnVap": 12.499, "ηa": 3018.17, "ηb": -7.314
        }
    )
    ether_non_ring: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0),
        description="Ether O (non-ring) group contribution.",
        alias="-O- @non-ring",
        json_schema_extra={
            "category": "oxygen increments", "group": "-O- @non-ring", "type": "non-ring", "id": "O3", "Tc": 0.0168, "Pc": 0.0015, "Vc": 18.0, "Tb": 22.42, "Tf": 22.23, "EnFo_IG": -132.22, "GiEnFo_IG": -105.0, "a": 25.5, "b": -0.0632, "c": 0.000111, "d": -5.48e-08, "EnFus": 1.188, "EnVap": 2.41, "ηa": 122.09, "ηb": -0.386
        }
    )
    ether_ring: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0),
        description="Ether O (ring) group contribution.",
        alias="-O- @ring",
        json_schema_extra={
            "category": "oxygen increments", "group": "-O- @ring", "type": "ring", "id": "O4", "Tc": 0.0098, "Pc": 0.0048, "Vc": 13.0, "Tb": 31.22, "Tf": 23.05, "EnFo_IG": -138.16, "GiEnFo_IG": -98.22, "a": 12.2, "b": -0.0126, "c": 6.03e-05, "d": -3.86e-08, "EnFus": 5.879, "EnVap": 4.682, "ηa": 440.24, "ηb": -0.953
        }
    )
    carbonyl_non_ring: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0),
        description="Carbonyl C=O (non-ring) group contribution.",
        alias=">C=O @non-ring",
        json_schema_extra={
            "category": "oxygen increments", "group": ">C=O @non-ring", "type": "non-ring", "id": "O5", "Tc": 0.038, "Pc": 0.0031, "Vc": 62.0, "Tb": 76.75, "Tf": 61.2, "EnFo_IG": -133.22, "GiEnFo_IG": -120.5, "a": 6.45, "b": 0.067, "c": -3.57e-05, "d": 2.86e-09, "EnFus": 4.189, "EnVap": 8.972, "ηa": 340.35, "ηb": -0.35
        }
    )
    carbonyl_ring: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0),
        description="Carbonyl C=O (ring) group contribution.",
        alias=">C=O @ring",
        json_schema_extra={
            "category": "oxygen increments", "group": ">C=O @ring", "type": "ring", "id": "O6", "Tc": 0.0284, "Pc": 0.0028, "Vc": 55.0, "Tb": 94.97, "Tf": 75.97, "EnFo_IG": -164.5, "GiEnFo_IG": -126.27, "a": 30.4, "b": -0.0829, "c": 0.000236, "d": -1.31e-07, "EnFus": 0.0, "EnVap": 6.645, "ηa": 0.0, "ηb": 0.0
        }
    )
    aldehyde: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0),
        description="Aldehyde O=CH- group contribution.",
        alias="O=CH-",
        json_schema_extra={
            "category": "oxygen increments", "group": "O=CH- @aldehyde", "type": "aldehyde", "id": "O7", "Tc": 0.0379, "Pc": 0.003, "Vc": 82.0, "Tb": 72.24, "Tf": 36.9, "EnFo_IG": -162.03, "GiEnFo_IG": -143.48, "a": 30.9, "b": -0.0336, "c": 0.00016, "d": -9.88e-08, "EnFus": 3.197, "EnVap": 9.093, "ηa": 740.92, "ηb": -1.713
        }
    )
    carboxylic_acid: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0),
        description="Carboxylic acid COOH group contribution.",
        alias="-COOH",
        json_schema_extra={
            "category": "oxygen increments", "group": "-COOH @acid", "type": "acid", "id": "O8", "Tc": 0.0791, "Pc": 0.0077, "Vc": 89.0, "Tb": 169.09, "Tf": 155.5, "EnFo_IG": -426.72, "GiEnFo_IG": -387.87, "a": 24.1, "b": 0.0427, "c": 8.04e-05, "d": -6.87e-08, "EnFus": 11.051, "EnVap": 19.537, "ηa": 1317.23, "ηb": -2.578
        }
    )
    ester: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0),
        description="Ester COO- group contribution.",
        alias="-COO-",
        json_schema_extra={
            "category": "oxygen increments", "group": "-COO- @ester", "type": "ester", "id": "O9", "Tc": 0.0481, "Pc": 0.0005, "Vc": 82.0, "Tb": 81.1, "Tf": 53.6, "EnFo_IG": -337.92, "GiEnFo_IG": -301.95, "a": 24.5, "b": 0.0402, "c": 4.02e-05, "d": -4.52e-08, "EnFus": 6.959, "EnVap": 9.633, "ηa": 483.88, "ηb": -0.966
        }
    )
    carbonyl_other: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0),
        description="Carbonyl =O (other) group contribution.",
        alias="=O @expect as above",
        json_schema_extra={
            "category": "oxygen increments", "group": "=O", "type": "expect as above", "id": "O10", "Tc": 0.0143, "Pc": 0.0101, "Vc": 36.0, "Tb": -10.5, "Tf": 2.08, "EnFo_IG": -247.61, "GiEnFo_IG": -250.83, "a": 6.82, "b": 0.0196, "c": 1.27e-05, "d": -1.78e-08, "EnFus": 3.624, "EnVap": 5.909, "ηa": 675.24, "ηb": -1.34
        }
    )
    primary_amine: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0),
        description="Primary amine NH2 group contribution.",
        alias="-NH2",
        json_schema_extra={
            "category": "nitrogen increments", "group": "-NH2", "type": "normal", "id": "N1", "Tc": 0.0243, "Pc": 0.0109, "Vc": 38.0, "Tb": 73.23, "Tf": 66.89, "EnFo_IG": -22.02, "GiEnFo_IG": 14.07, "a": 26.9, "b": -0.0412, "c": 0.000164, "d": -9.76e-08, "EnFus": 3.515, "EnVap": 10.788, "ηa": 0.0, "ηb": 0.0
        }
    )
    secondary_amine_non_ring: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0),
        description="Secondary amine >NH (non-ring) group contribution.",
        alias=">NH @non-ring",
        json_schema_extra={
            "category": "nitrogen increments", "group": ">NH @non-ring", "type": "non-ring", "id": "N2", "Tc": 0.0295, "Pc": 0.0077, "Vc": 35.0, "Tb": 50.17, "Tf": 52.66, "EnFo_IG": 53.47, "GiEnFo_IG": 89.39, "a": -1.21, "b": 0.0762, "c": -4.86e-05, "d": 1.05e-08, "EnFus": 5.099, "EnVap": 6.436, "ηa": 0.0, "ηb": 0.0
        }
    )
    secondary_amine_ring: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0),
        description="Secondary amine >NH (ring) group contribution.",
        alias=">NH @ring",
        json_schema_extra={
            "category": "nitrogen increments", "group": ">NH @ring", "type": "ring", "id": "N3", "Tc": 0.013, "Pc": 0.0114, "Vc": 29.0, "Tb": 52.82, "Tf": 101.51, "EnFo_IG": 31.65, "GiEnFo_IG": 75.61, "a": 11.8, "b": -0.023, "c": 0.000107, "d": -6.28e-08, "EnFus": 7.49, "EnVap": 6.93, "ηa": 0.0, "ηb": 0.0
        }
    )
    tertiary_amine_non_ring: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0),
        description="Tertiary amine >N- (non-ring) group contribution.",
        alias=">N- @non-ring",
        json_schema_extra={
            "category": "nitrogen increments", "group": ">N- @non-ring", "type": "non-ring", "id": "N4", "Tc": 0.0169, "Pc": 0.0074, "Vc": 9.0, "Tb": 11.74, "Tf": 48.84, "EnFo_IG": 123.34, "GiEnFo_IG": 163.16, "a": -31.1, "b": 0.227, "c": -0.00032, "d": 1.46e-07, "EnFus": 4.703, "EnVap": 1.896, "ηa": 0.0, "ηb": 0.0
        }
    )
    imine_non_ring: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0),
        description="Imine -N= (non-ring) group contribution.",
        alias="-N= @non-ring",
        json_schema_extra={
            "category": "nitrogen increments", "group": "-N= @non-ring", "type": "non-ring", "id": "N5", "Tc": 0.0255, "Pc": -0.0099, "Vc": 0.0, "Tb": 74.6, "Tf": 0.0, "EnFo_IG": 23.61, "GiEnFo_IG": 0.0, "a": 0.0, "b": 0.0, "c": 0.0, "d": 0.0, "EnFus": 0.0, "EnVap": 3.335, "ηa": 0.0, "ηb": 0.0
        }
    )
    imine_ring: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0),
        description="Imine -N= (ring) group contribution.",
        alias="-N= @ring",
        json_schema_extra={
            "category": "nitrogen increments", "group": "-N= @ring", "type": "ring", "id": "N6", "Tc": 0.0085, "Pc": 0.0076, "Vc": 34.0, "Tb": 57.55, "Tf": 68.4, "EnFo_IG": 55.52, "GiEnFo_IG": 79.93, "a": 8.83, "b": -0.00384, "c": 4.35e-05, "d": -2.6e-08, "EnFus": 3.649, "EnVap": 6.528, "ηa": 0.0, "ηb": 0.0
        }
    )
    imine_secondary: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0),
        description="Secondary imine =NH group contribution.",
        alias="=NH",
        json_schema_extra={
            "category": "nitrogen increments", "group": "=NH", "type": "normal", "id": "N7", "Tc": 0.0, "Pc": 0.0, "Vc": 0.0, "Tb": 83.08, "Tf": 68.91, "EnFo_IG": 93.7, "GiEnFo_IG": 119.66, "a": 5.69, "b": -0.00412, "c": 0.000128, "d": -8.88e-08, "EnFus": 0.0, "EnVap": 12.169, "ηa": 0.0, "ηb": 0.0
        }
    )
    nitrile: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0),
        description="Nitrile CN group contribution.",
        alias="-CN",
        json_schema_extra={
            "category": "nitrogen increments", "group": "-CN", "type": "normal", "id": "N8", "Tc": 0.0496, "Pc": -0.0101, "Vc": 91.0, "Tb": 125.66, "Tf": 59.89, "EnFo_IG": 88.43, "GiEnFo_IG": 89.22, "a": 36.5, "b": -0.0733, "c": 0.000184, "d": -1.03e-07, "EnFus": 2.414, "EnVap": 12.851, "ηa": 0.0, "ηb": 0.0
        }
    )
    nitro: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0),
        description="Nitro NO2 group contribution.",
        alias="-NO2",
        json_schema_extra={
            "category": "nitrogen increments", "group": "-NO2", "type": "normal", "id": "N9", "Tc": 0.0437, "Pc": 0.0064, "Vc": 91.0, "Tb": 152.54, "Tf": 127.24, "EnFo_IG": -66.57, "GiEnFo_IG": -16.83, "a": 25.9, "b": -0.00374, "c": 0.000129, "d": -8.88e-08, "EnFus": 9.679, "EnVap": 16.738, "ηa": 0.0, "ηb": 0.0
        }
    )
    thiol: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0),
        description="Thiol SH group contribution.",
        alias="-SH",
        json_schema_extra={
            "category": "sulfur increments", "group": "-SH", "type": "normal", "id": "S1", "Tc": 0.0031, "Pc": 0.0084, "Vc": 63.0, "Tb": 63.56, "Tf": 20.09, "EnFo_IG": -17.33, "GiEnFo_IG": -22.99, "a": 35.3, "b": -0.0758, "c": 0.000185, "d": -1.03e-07, "EnFus": 2.36, "EnVap": 6.884, "ηa": 0.0, "ηb": 0.0
        }
    )
    thioether_non_ring: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0),
        description="Thioether -S- (non-ring) group contribution.",
        alias="-S- @non-ring",
        json_schema_extra={
            "category": "sulfur increments", "group": "-S- @non-ring", "type": "non-ring", "id": "S2", "Tc": 0.0119, "Pc": 0.0049, "Vc": 54.0, "Tb": 68.78, "Tf": 34.4, "EnFo_IG": 41.87, "GiEnFo_IG": 33.12, "a": 19.6, "b": -0.00561, "c": 4.02e-05, "d": -2.76e-08, "EnFus": 4.13, "EnVap": 6.817, "ηa": 0.0, "ηb": 0.0
        }
    )
    thioether_ring: Optional[GroupUnit] = Field(
        default_factory=lambda: GroupUnit(value=0),
        description="Thioether -S- (ring) group contribution.",
        alias="-S- @ring",
        json_schema_extra={
            "category": "sulfur increments", "group": "-S- @ring", "type": "ring", "id": "S3", "Tc": 0.0019, "Pc": 0.0051, "Vc": 38.0, "Tb": 52.1, "Tf": 79.93, "EnFo_IG": 39.1, "GiEnFo_IG": 27.76, "a": 16.7, "b": 0.00481, "c": 2.77e-05, "d": -2.11e-08, "EnFus": 1.557, "EnVap": 5.984, "ηa": 0.0, "ηb": 0.0
        }
    )


class JobackGroupData(BaseModel):
    """A class to represent a Joback group with its name and contribution data."""
    id: str
    name: str
    count: float
    data: Dict[str, str]


class JobackHeatCapacity(BaseModel):
    a: float = Field(..., description="Cp correlation parameter a")
    b: float = Field(..., description="Cp correlation parameter b")
    c: float = Field(..., description="Cp correlation parameter c")
    d: float = Field(..., description="Cp correlation parameter d")

    # optional: make parameters immutable after creation
    model_config = ConfigDict(frozen=True)

    def __call__(self, T: float) -> float:
        """
        Evaluate Cp at temperature T (K).
        """
        return (
            self.a - 37.93 +
            (self.b + 0.210) * T +
            (self.c - 3.91e-4) * T**2 +
            (self.d + 2.06e-7) * T**3
        )

    def Cp(self, T: float) -> float:
        """
        Alias method if you prefer Cp(T) instead of obj(T).
        """
        return self(T)


class JobackProp(TypedDict):
    value: float | None
    unit: str
    symbol: str


class JobackCalcProp(TypedDict):
    value: Callable[[float], float] | None
    unit: str
    symbol: str
