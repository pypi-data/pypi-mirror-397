# import libs
import logging
from typing import Dict, Any, Literal, Optional
from math import pow
import os
# locals
from ..models import (
    GroupUnit,
    ZabranskyRuzickaGroupContributions,
    ZabranskyRuzickaGroupContributionsCorrections,
    ZabranskyRuzickaGroupData,
    EstimatedProp
)
from ..util import ReferenceLoader
from ..configs import (
    ZABRANSKY_RUZICKA_DATA_FILE_1,
    ZABRANSKY_RUZICKA_DATA_FILE_2,
    ZABRANSKY_RUZICKA_TABLE_COLUMN_GROUP,
    ZABRANSKY_RUZICKA_REFERENCE
)

# NOTE: logger
logger = logging.getLogger(__name__)


class ZabranskyRuzicka:
    '''
    Zabransky-Ruzicka method to estimate thermodynamic properties.

    A second-order group additivity approach for estimating the temperature-dependent heat capacity of pure organic liquids in the range from melting point to normal boiling point.
    '''

    def __init__(
        self,
        group_contributions: ZabranskyRuzickaGroupContributions | Dict[str, float] | Dict[str, int],
        group_corrections:  Optional[
            ZabranskyRuzickaGroupContributionsCorrections |
            Dict[str, float] |
            Dict[str, int]
        ] = None
    ):
        '''
        Initializes the Zabransky-Ruzicka method.

        Parameters
        ----------
        group_contributions : ZabranskyRuzickaGroupContributions | Dict[str, float] | Dict[str, int]
            Group contributions for the compound.
        group_corrections : ZabranskyRuzickaGroupContributionsCorrections | Dict[
            str, float] | Dict[str, int] | None
            Group corrections for the compound.
        '''
        # NOTE: group contributions
        self.group_contributions = group_contributions
        self.group_corrections = group_corrections if group_corrections else {}

        # SECTION: load parameters from reference file
        self.params, self.corrections = self.load_parameters()

        # NOTE: get group contribution (from reference)
        self.group_id = self._get_group_contribution()
        # NOTE: get correction contribution (from reference)
        self.correction_id = self._get_correction_contribution()

        # SECTION: valid groups
        # NOTE: check group contributions
        self.valid_group_contribution = self._check_group_contributions(
            group_x=self.group_contributions,
            group_id=self.group_id
        )
        # NOTE: check group corrections
        self.valid_group_corrections = self._check_group_contributions(
            group_x=self.group_corrections,
            group_id=self.correction_id
        )

        # >> merge valid groups
        self.valid_groups = {
            **self.valid_group_contribution,
            **self.valid_group_corrections
        }

    def __repr__(self) -> str:
        return f"""Zabransky Ruzicka Method: \n
        Group Contributions: {self.group_contributions} \n
        Group Corrections: {self.group_corrections}  \n
        Reference: {ZABRANSKY_RUZICKA_REFERENCE}
        """

    @property
    def group_contribution_idx(self):
        '''
        Returns the group contribution index.

        Returns
        -------
        group_id : dict
            Dictionary of group contributions.
        '''
        return self.group_id

    def load_parameters(
        self,
    ):
        '''
        Loads parameters from reference file.

        Returns
        -------
        params_df, corrections_df : pd.DataFrame, pd.DataFrame
            DataFrames of parameters and corrections.
        '''
        try:
            # load reference file
            ref_loader = ReferenceLoader()

            # current folder
            current_folder = os.path.dirname(os.path.abspath(__file__))
            #  data folder
            data_folder = os.path.join(
                current_folder,
                '..',
                'data',
            )

            # NOTE: load CSV reference
            params_df = ref_loader.load_csv_ref(
                reference_name=ZABRANSKY_RUZICKA_DATA_FILE_1,
                reference_folder=data_folder,
            )

            # NOTE: corrections
            corrections_df = ref_loader.load_csv_ref(
                reference_name=ZABRANSKY_RUZICKA_DATA_FILE_2,
                reference_folder=data_folder,
            )

            # return parameters dataframe
            return params_df, corrections_df
        except Exception as e:
            raise Exception("Loading  parameters failed!, ", e)

    def _get_group_contribution(
        self,
    ):
        '''
        Gets group contribution for a specific group.

        Parameters
        ----------
        None

        Returns
        -------
        contribution : dict
            Dictionary of group contributions for various properties.
        '''
        try:
            # filter  parameters for the specific group
            group_data = self.params[
                ZABRANSKY_RUZICKA_TABLE_COLUMN_GROUP
            ]

            # extract contributions
            contribution = group_data.to_dict()

            return contribution
        except Exception as e:
            raise Exception(f"Getting contribution for group failed!, ", e)

    def _get_correction_contribution(
        self,
    ):
        '''
        Gets correction contribution for a specific group.

        Parameters
        ----------
        None

        Returns
        -------
        contribution : dict
            Dictionary of correction contributions for various properties.
        '''
        try:
            # filter  corrections for the specific group
            correction_data = self.corrections[
                ZABRANSKY_RUZICKA_TABLE_COLUMN_GROUP
            ]

            # extract contributions
            contribution = correction_data.to_dict()

            return contribution
        except Exception as e:
            raise Exception(
                f"Getting correction contribution for group failed!, ", e)

    def list_available_groups(
        self,
    ):
        '''
        Lists all available  groups.

        Returns
        -------
        groups : list
            List of available  groups.
        '''
        try:
            # get list of available groups
            groups = self.params[ZABRANSKY_RUZICKA_TABLE_COLUMN_GROUP].tolist()

            return groups
        except Exception as e:
            raise Exception("Listing available  groups failed!, ", e)

    def _get_group_x_data(
        self,
        group_name: str,
        group_mode: Literal['contribution', 'correction'] = 'contribution'
    ):
        '''
        Gets contribution data for a specific group.

        Parameters
        ----------
        group_name : str
            Name of the group.
        group_mode : Literal['contribution', 'correction'], optional
            Mode of the group, by default 'contribution'.

        Returns
        -------
        group_data : dict
            Dictionary of contribution data for the group with header names as keys.
        '''
        try:
            # filter  parameters for the specific group
            if group_mode == 'contribution':
                group_data = self.params[
                    self.params[ZABRANSKY_RUZICKA_TABLE_COLUMN_GROUP] == group_name.strip(
                    )
                ]
            elif group_mode == 'correction':
                group_data = self.corrections[
                    self.corrections[ZABRANSKY_RUZICKA_TABLE_COLUMN_GROUP] == group_name.strip(
                    )
                ]
            else:
                return {}

            # convert to Series and then to dictionary with column headers as keys
            return {k: str(v) for k, v in group_data.iloc[0].to_dict().items()} if len(group_data) > 0 else {}
        except Exception as e:
            raise Exception(
                f"Getting contribution data for group {group_name} failed!, ", e)

    def _check_group_contributions(
            self,
            group_x: Dict[str, Any] | ZabranskyRuzickaGroupContributions | ZabranskyRuzickaGroupContributionsCorrections,
            group_id: Dict[str, Any]
    ) -> Dict[str, ZabranskyRuzickaGroupData]:
        """
        Checks the validity of group contributions.

        Parameters
        ----------
        group_x : Dict[str, Any] | ZabranskyRuzickaGroupContributions | ZabranskyRuzickaGroupContributionsCorrections
            Dictionary or dataclass of group contributions.
        group_id : Dict[str, Any]
            Dictionary of group contributions.
        """
        try:
            # NOTE: count occurrences
            valid_groups = {}

            # count each group
            if isinstance(group_x, dict):
                # ! dictionary type
                # iterate over group contributions
                for group_name, group_value in group_x.items():
                    # check if group exists in  parameters
                    if group_name in group_id.values():
                        # add to count dictionary
                        res_ = ZabranskyRuzickaGroupData(
                            id=group_name,
                            name=group_name,
                            count=float(group_value),
                            data=self._get_group_x_data(
                                group_name=group_name,
                                group_mode='contribution' if group_name in self.group_id.values() else 'correction'
                            )
                        )
                        # append
                        valid_groups[group_name] = res_
            elif isinstance(
                group_x,
                ZabranskyRuzickaGroupContributions,
            ):
                # ! dataclass type
                # iterate over dataclass fields
                for field_name, field_info in ZabranskyRuzickaGroupContributions.model_fields.items():
                    # get field alias ( group name)
                    alias = field_info.alias

                    # check if field is None
                    if alias is None:
                        continue

                    # value stored in the model instance = use field_name
                    group_unit: GroupUnit = getattr(
                        group_x,
                        field_name
                    )

                    # check if group value is greater than 0
                    if group_unit.value > 0:
                        # check if group exists in  parameters
                        if alias in group_id.values():
                            # add to count dictionary
                            res_ = ZabranskyRuzickaGroupData(
                                id=alias,
                                name=field_name,
                                count=float(group_unit.value),
                                data=self._get_group_x_data(
                                    group_name=alias,
                                    group_mode='contribution'
                                )
                            )
                            # append
                            valid_groups[alias] = res_
            elif isinstance(
                group_x,
                ZabranskyRuzickaGroupContributionsCorrections,
            ):
                # ! dataclass type
                # iterate over dataclass fields
                for field_name, field_info in ZabranskyRuzickaGroupContributionsCorrections.model_fields.items():
                    # get field alias ( group name)
                    alias = field_info.alias

                    # check if field is None
                    if alias is None:
                        continue

                    # value stored in the model instance = use field_name
                    group_unit: GroupUnit = getattr(
                        group_x,
                        field_name
                    )

                    # check if group value is greater than 0
                    if group_unit.value > 0:
                        # check if group exists in  parameters
                        if alias in group_id.values():
                            # add to count dictionary
                            res_ = ZabranskyRuzickaGroupData(
                                id=alias,
                                name=field_name,
                                count=float(group_unit.value),
                                data=self._get_group_x_data(
                                    group_name=alias,
                                    group_mode='correction'
                                )
                            )
                            # append
                            valid_groups[alias] = res_
            else:
                logger.error("Invalid type for group contributions!")
                return valid_groups

            return valid_groups
        except Exception as e:
            raise Exception("Checking group contributions failed!, ", e)

    def _build_delta_c(
            self,
    ):
        '''
        Calculates delta C.

        Parameters
        ----------
        temperature : float
            Temperature in Kelvin.
        '''
        try:
            # SECTION: calculate sigma
            # initialize critical temperature
            sigma = {}

            # iterate over valid groups
            for group_name, group_info in self.valid_groups.items():
                # get group count
                group_count = group_info.count
                # get contribution data
                contribution_data = group_info.data
                # get contribution
                val_a_i = contribution_data.get('a_i', 0)
                val_b_i = contribution_data.get('b_i', 0)
                val_d_i = contribution_data.get('d_i', 0)

                # accumulate to sigma
                sigma[group_name] = {
                    'a_i': float(val_a_i),
                    'b_i': float(val_b_i),
                    'd_i': float(val_d_i),
                    'count': group_count
                }

            return sigma
        except Exception as e:
            raise Exception("Calculating critical temperature failed!, ", e)

    def _calc_sigma_delta_c(
            self,
            delta_c: Dict[str, Dict[str, float]],
            temperature: float
    ):
        '''
        Calculates sigma delta C.

        Parameters
        ----------
        delta_c : Dict[str, Dict[str, float]]
            Delta C contributions.
        temperature : float
            Temperature in Kelvin.
        '''
        try:
            # SECTION: calculate sigma
            # initialize critical temperature
            sigma = {}

            # iterate over valid groups
            for group_name, data in delta_c.items():
                # get group count
                group_count = data.get('count', 0)
                # get contribution
                val_a_i = data.get('a_i', 0)
                val_b_i = data.get('b_i', 0)
                val_d_i = data.get('d_i', 0)

                # calculate delta C for the group
                delta_c_i = (
                    float(val_a_i) +
                    float(val_b_i) * (temperature/100) +
                    float(val_d_i) * pow(temperature/100, 2)
                ) * group_count

                # accumulate to sigma
                sigma[group_name] = delta_c_i

            return sigma
        except Exception as e:
            raise Exception("Calculating critical temperature failed!, ", e)

    def _calc(
        self
    ) -> EstimatedProp:
        '''
        Calculates properties using  method.

        Returns
        -------
        EstimatedProp
            Calculated thermodynamic properties.
        '''
        try:
            # SECTION: create function
            def Cp_LIQ(T: float) -> float:
                '''
                Calculates liquid heat capacity at temperature T.

                Parameters
                ----------
                T : float
                    Temperature in Kelvin.

                Returns
                -------
                Cp_LIQ : float
                    Liquid heat capacity in J/mol·K.
                '''
                # create sigma delta C
                delta_c = self._build_delta_c()

                # calculate sigma delta C
                sigma_delta_c = self._calc_sigma_delta_c(delta_c, T)

                # sum over all groups
                Cp_LIQ_value = sum(sigma_delta_c.values())
                # times 8.314472
                Cp_LIQ_value *= 8.314472

                return Cp_LIQ_value

            # return
            return EstimatedProp(
                value=Cp_LIQ,
                unit="J/mol·K",
                symbol="Cp_LIQ"
            )
        except Exception as e:
            raise Exception("Calculating properties failed!, ", e)
