# import libs
import logging
from typing import List, Tuple
# locals
from ..models import (
    ZabranskyRuzickaGroupContributions,
    ZabranskyRuzickaGroupContributionsCorrections,
)

# NOTE: logger
logger = logging.getLogger(__name__)


def zabransky_ruzicka_group_contribution_info() -> Tuple[List[str], List[str]]:
    """
    Get the list of Zabransky-Ruzicka group contribution.

    Returns
    -------
    Tuple[List[str],List[str]]
        A tuple containing two lists: field names and their corresponding aliases.
    """
    try:
        # NOTE: ids
        group_ids = []
        group_names = []

        # NOTE: alias
        for filed_name, field_info in ZabranskyRuzickaGroupContributions.model_fields.items():
            # get alias
            alias = field_info.alias

            # >> store alias
            if alias is not None:
                group_ids.append(alias)

            # >> also store field names
            group_names.append(filed_name)

        return group_names, group_ids
    except Exception as e:
        logger.error(
            f"Error retrieving Zabransky-Ruzicka group contribution IDs: {e}")
        return [], []


def zabransky_ruzicka_group_contribution_names() -> List[str]:
    """
    Get the list of Zabransky-Ruzicka group contribution names.

    Returns
    -------
    List[str]
        A list of Zabransky-Ruzicka group contribution IDs.
    """
    try:
        # NOTE: keys
        group_ids = list(
            ZabranskyRuzickaGroupContributions.model_fields.keys())
        return group_ids
    except Exception as e:
        logger.error(
            f"Error retrieving Zabransky-Ruzicka group contribution IDs: {e}")
        return []


def zabransky_ruzicka_group_contribution_ids() -> List[str]:
    """
    Get the list of Zabransky-Ruzicka group contribution IDs.

    Returns
    -------
    List[str]
        A list of Zabransky-Ruzicka group contribution IDs.
    """
    try:
        # NOTE: alias
        group_ids = []
        for filed_name, field_info in ZabranskyRuzickaGroupContributions.model_fields.items():
            # get alias
            alias = field_info.alias

            # >> store alias
            if alias is not None:
                group_ids.append(alias)

        return group_ids
    except Exception as e:
        logger.error(
            f"Error retrieving Zabransky-Ruzicka group contribution IDs: {e}")
        return []


def zabransky_ruzicka_group_correction_ids() -> List[str]:
    """
    Get the list of Zabransky-Ruzicka group contribution correction IDs.

    Returns
    -------
    List[str]
        A list of Zabransky-Ruzicka group contribution correction IDs.
    """
    try:
        # NOTE: alias
        group_ids = []
        for filed_name, field_info in ZabranskyRuzickaGroupContributionsCorrections.model_fields.items():
            # get alias
            alias = field_info.alias

            # >> store alias
            if alias is not None:
                group_ids.append(alias)

        return group_ids
    except Exception as e:
        logger.error(
            f"Error retrieving Zabransky-Ruzicka group contribution correction IDs: {e}")
        return []


def zabransky_ruzicka_group_correction_names() -> List[str]:
    """
    Get the list of Zabransky-Ruzicka group contribution correction names.

    Returns
    -------
    List[str]
        A list of Zabransky-Ruzicka group contribution correction IDs.
    """
    try:
        # NOTE: keys
        group_ids = list(
            ZabranskyRuzickaGroupContributionsCorrections.model_fields.keys())
        return group_ids
    except Exception as e:
        logger.error(
            f"Error retrieving Zabransky-Ruzicka group contribution correction IDs: {e}")
        return []


def zabransky_ruzicka_group_correction_info() -> Tuple[List[str], List[str]]:
    """
    Get the list of Zabransky-Ruzicka group contribution corrections.

    Returns
    -------
    Tuple[List[str],List[str]]
        A tuple containing two lists: field names and their corresponding aliases.
    """
    try:
        # NOTE: ids
        group_ids = []
        group_names = []

        # NOTE: alias
        for filed_name, field_info in ZabranskyRuzickaGroupContributionsCorrections.model_fields.items():
            # get alias
            alias = field_info.alias

            # >> store alias
            if alias is not None:
                group_ids.append(alias)

            # >> also store field names
            group_names.append(filed_name)

        return group_names, group_ids
    except Exception as e:
        logger.error(
            f"Error retrieving Zabransky-Ruzicka group contribution correction IDs: {e}")
        return [], []
