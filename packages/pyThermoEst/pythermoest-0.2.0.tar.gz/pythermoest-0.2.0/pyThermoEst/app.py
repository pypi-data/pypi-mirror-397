# import libs
import logging
from typing import Dict, Optional
# locals
from .models import (
    JobackGroupContributions,
    ZabranskyRuzickaGroupContributions,
    ZabranskyRuzickaGroupContributionsCorrections,
    EstimatedProp,
    JobackProp,
    JobackCalcProp
)
from .core import Joback, ZabranskyRuzicka


# NOTE: logger
logger = logging.getLogger(__name__)


# SECTION: Joback Group Contributions

def joback_calc(
    groups: JobackGroupContributions | Dict[str, int] | Dict[str, float],
    total_atoms_number: int
) -> Optional[Dict[str, EstimatedProp]]:
    """
    Using Joback method to calculate thermodynamic properties including

    Parameters
    ----------
    groups : JobackGroupContributions | Dict[str, float] | Dict[str, int]
        Group contributions for Joback method.
    total_atoms_number : int
        Total number of atoms in the molecule.

    Returns
    -------
    Dict[str, EstimatedProp] | None
        A dictionary containing calculated thermodynamic properties.

    Notes
    -----
    You can use either the field names or their aliases to specify group contributions. For example:
    - methyl has alias '-CH3'
    - methylene has alias '-CH2- @non-ring'
    - imine_non_ring has alias '-N= @non-ring'
    - imine_ring has alias '-N= @ring'
    """
    try:
        # SECTION: initialize Joback method
        Joback_ = Joback(
            group_contributions=groups,
            total_atoms_number=total_atoms_number
        )

        # NOTE: calculate properties
        return Joback_._calc()
    except Exception as e:
        logger.error(f"Error in Joback calculation: {e}")
        return None


def joback_prop_calc(
    groups: JobackGroupContributions | Dict[str, int] | Dict[str, float],
    total_atoms_number: int,
) -> Optional[Dict[str, JobackProp]]:
    """
    Using Joback method to calculate a only thermodynamic property.

    Parameters
    ----------
    groups : JobackGroupContributions | Dict[str, float] | Dict[str, int]
        Group contributions for Joback method.
    total_atoms_number : int
        Total number of atoms in the molecule.

    Returns
    -------
    Dict[str, JobackProp] | None
        A dictionary containing the calculated thermodynamic property.

    Notes
    -----
    You can use either the field names or their aliases to specify group contributions.
    """
    try:
        # SECTION: initialize Joback method
        joback_calc_ = joback_calc(
            groups=groups,
            total_atoms_number=total_atoms_number
        )

        # SECTION: return property (not callable ones in value)
        # NOTE: initialize result
        prop_result: Dict[str, JobackProp] = {}

        # NOTE: iterate over calculated properties
        if joback_calc_:
            for prop_name, prop_data in joback_calc_.items():
                value = prop_data['value']
                if callable(value):
                    continue

                # >> add to result
                prop_result[prop_name] = JobackProp(
                    value=value,
                    unit=prop_data['unit'],
                    symbol=prop_data['symbol']
                )

        return prop_result
    except Exception as e:
        logger.error(f"Error in Joback property calculation: {e}")
        return None


def joback_heat_capacity_calc(
    groups: JobackGroupContributions | Dict[str, int] | Dict[str, float],
    total_atoms_number: int,
) -> Optional[JobackCalcProp]:
    """
    Using Joback method to retrieve heat capacity equation (function of temperature [K]).

    Parameters
    ----------
    groups : JobackGroupContributions | Dict[str, float] | Dict[str, int]
        Group contributions for Joback method.
    total_atoms_number : int
        Total number of atoms in the molecule.

    Returns
    -------
    JobackCalcProp | None
        A dictionary containing calculated heat capacity property as:
        - value: equation to calculate heat capacity.
        - units: units of the heat capacity (J/mol.K).
        - symbol: symbol representing heat capacity (Cp_LIQ).

    Notes
    -----
    You can use either the field names or their aliases to specify group contributions.
    """
    try:
        # SECTION: initialize Joback method
        joback_calc_ = joback_calc(
            groups=groups,
            total_atoms_number=total_atoms_number
        )

        # SECTION: return heat capacity property
        if joback_calc_ and 'heat_capacity' in joback_calc_:
            heat_capacity_data = joback_calc_['heat_capacity']

            # check type
            if not callable(heat_capacity_data['value']):
                return None

            # >> return heat capacity
            return JobackCalcProp(
                value=heat_capacity_data['value'],
                unit=heat_capacity_data['unit'],
                symbol=heat_capacity_data['symbol']
            )

        return None
    except Exception as e:
        logger.error(f"Error in Joback heat capacity calculation: {e}")
        return None


# SECTION: Zabransky-Ruzicka Group Contributions


def zabransky_ruzicka_calc(
    group_contributions: ZabranskyRuzickaGroupContributions | Dict[str, float] | Dict[str, int],
    group_corrections: Optional[
        ZabranskyRuzickaGroupContributionsCorrections |
        Dict[str, float] |
        Dict[str, int]
    ] = None
) -> Optional[EstimatedProp]:
    """
    Using Zabransky-Ruzicka method to calculate thermodynamic properties including

    Parameters
    ----------
    group_contributions : ZabranskyRuzickaGroupContributions | Dict[str, float] | Dict[str, int]
        Group contributions for Zabransky-Ruzicka method.
    group_corrections : Optional[ZabranskyRuzickaGroupContributionsCorrections | Dict[str, float] | Dict[str, int]]
        Group correction contributions for Zabransky-Ruzicka method.

    Returns
    -------
    EstimatedProp | None
        A dictionary containing calculated thermodynamic properties as:
        - value: equation to calculate heat capacity.
        - units: units of the heat capacity (J/mol.K).
        - symbol: symbol representing heat capacity (Cp_LIQ).

    Notes
    -----
    You can use either the field names or their aliases to specify group contributions. For example:
    - C-(H)3(C)
    - C-(H)2(C)2
    - C-(H)(C)3

    """
    try:
        # SECTION: initialize Zabransky-Ruzicka method
        ZabranskyRuzicka_ = ZabranskyRuzicka(
            group_contributions=group_contributions,
            group_corrections=group_corrections
        )

        # NOTE: calculate properties
        return ZabranskyRuzicka_._calc()
    except Exception as e:
        logger.error(f"Error in Zabransky-Ruzicka calculation: {e}")
        return None
