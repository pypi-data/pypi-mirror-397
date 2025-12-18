# import libs
import logging
from typing import List, Any, Dict, Optional
import pycuc

# NOTE: set up logger
logger = logging.getLogger(__name__)


def normalize_unit(
    data: List[Any],
    to_unit: str,
    valid_from: Optional[List[str]] = None,
) -> Dict:
    '''
    Normalizes a list of units to the specified unit.

    Parameters
    ----------
    data : List[Any]
        List of data with units.
    to_unit : str
        Unit to normalize to.
    valid_from : List[str], optional
        List of valid units to convert from, by default None.

    Returns
    -------
    Dict
        A dictionary containing the normalized data and target unit.
    '''
    try:
        # NOTE: check inputs
        to = to_unit.strip()

        # >> check
        if not to:
            logger.warning("Target unit is empty!")
            return {}

        # >> check
        if not data or not isinstance(data, list):
            logger.warning("Input data is empty or not a list!")
            return {}

        # NOTE: normalize units
        normalized_data: List[float] = []

        # >> loop over data
        for item in data:
            # >> get value and unit
            if hasattr(item, 'value') and hasattr(item, 'unit'):
                value = item.value
                from_unit = item.unit
            else:
                logger.warning(
                    f"Item {item} does not have 'value' and 'unit' attributes!")
                continue

            # >> check valid_from
            if (
                valid_from and
                from_unit not in valid_from
            ):
                logger.warning(f"Unit '{from_unit}' not in valid_from list!")
                continue

            # >> convert unit
            try:
                converted_value = pycuc.convert_from_to(
                    value=value,
                    from_unit=from_unit,
                    to_unit=to
                )
                normalized_data.append(converted_value)
            except Exception as e:
                logger.error(
                    f"Conversion failed for value {value} from '{from_unit}' to '{to}': ", e)
                continue

        return {
            "data": normalized_data,
            "to": to,
        }
    except Exception as e:
        logger.error("Unit normalization failed!, ", e)
        return {}
