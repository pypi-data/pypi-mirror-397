# import libs
import logging
from typing import Dict
from math import pow
import os
# locals
from ..models import (
    JobackGroupContributions,
    GroupUnit,
    JobackGroupData,
    JobackHeatCapacity,
    EstimatedProp
)
from ..util import ReferenceLoader
from ..configs import JOBACK_DATA_FILE, JOBACK_TABLE_COLUMN_GROUP

# NOTE: logger
logger = logging.getLogger(__name__)


class Joback:
    '''
    Joback method implementation.

    - The Joback group contribution method (often called Joback-Reid method) estimates 11 thermodynamic properties of organic compounds, such as boiling point, critical temperature, and heat of formation, by breaking molecules into 41 predefined functional groups and summing their contributions.
    - It assumes no interactions between groups, making it simple but less accurate for complex or aromatic compounds; estimates are generally within 5-15% error for many properties based on tested datasets.
    - To use it, identify and count the functional groups in the molecule (e.g., for ethanol: one -CH₃, one -CH₂-, one -OH @alcohol), then apply the summation formulas for the desired property—research suggests it's most reliable for mid-sized aliphatic organics, with potential inaccuracies for rings or halogens.
    - All 41 groups are categorized into non-ring, ring, halogen, oxygen, nitrogen, and sulfur types, with specific contribution values for each property.
    '''

    def __init__(
        self,
        group_contributions: JobackGroupContributions | Dict[str, float] | Dict[str, int],
        total_atoms_number: int,
    ):
        '''
        Initializes Joback method with group contributions.

        Parameters
        ----------
        group_contributions : JobackGroupContributions | Dict[str, float] | Dict[str, int]
            Group contributions for Joback method.
        '''
        # NOTE: group contributions
        self.group_contributions = group_contributions
        # NOTE: total atoms number
        self.total_atoms_number = total_atoms_number

        # SECTION: load Joback parameters
        self.joback_params = self.load_joback_parameters()

        # SECTION: get group contribution
        self.group_id = self._get_group_contribution()

        # SECTION: valid groups
        self.valid_groups = self._check_group_contributions()

    def __repr__(self) -> str:
        return f"""Joback Method with {len(self.group_id)} groups  \n
        Group Contributions: {self.group_contributions} """

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

    def load_joback_parameters(
        self,
    ):
        '''
        Loads Joback parameters from reference file.

        Returns
        -------
        joback_params : pd.DataFrame
            DataFrame of Joback parameters.
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
            joback_df = ref_loader.load_csv_ref(
                reference_name=JOBACK_DATA_FILE,
                reference_folder=data_folder,
            )

            # return Joback parameters
            return joback_df
        except Exception as e:
            raise Exception("Loading Joback parameters failed!, ", e)

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
            # filter Joback parameters for the specific group
            group_data = self.joback_params[
                JOBACK_TABLE_COLUMN_GROUP
            ]

            # extract contributions
            contribution = group_data.to_dict()

            return contribution
        except Exception as e:
            raise Exception(f"Getting contribution for group failed!, ", e)

    def list_available_groups(
        self,
    ):
        '''
        Lists all available Joback groups.

        Returns
        -------
        groups : list
            List of available Joback groups.
        '''
        try:
            # get list of available groups
            groups = self.joback_params[JOBACK_TABLE_COLUMN_GROUP].tolist()

            return groups
        except Exception as e:
            raise Exception("Listing available Joback groups failed!, ", e)

    def _get_group_contribution_data(
        self,
        group_name: str,
    ):
        '''
        Gets contribution data for a specific group.

        Parameters
        ----------
        group_name : str
            Name of the group.

        Returns
        -------
        group_data : dict
            Dictionary of contribution data for the group with header names as keys.
        '''
        try:
            # filter Joback parameters for the specific group
            group_data = self.joback_params[
                self.joback_params[JOBACK_TABLE_COLUMN_GROUP] == group_name.strip(
                )
            ]

            # convert to Series and then to dictionary with column headers as keys
            return {k: str(v) for k, v in group_data.iloc[0].to_dict().items()} if len(group_data) > 0 else {}
        except Exception as e:
            raise Exception(
                f"Getting contribution data for group {group_name} failed!, ", e)

    def _check_group_contributions(
            self
    ) -> Dict[str, JobackGroupData]:
        """
        Checks the validity of group contributions.
        """
        try:
            # NOTE: count occurrences
            valid_groups = {}

            # count each group
            if isinstance(self.group_contributions, dict):
                # ! dictionary type
                # iterate over group contributions
                for group_name, group_value in self.group_contributions.items():
                    # check if group exists in Joback parameters
                    if group_name in self.group_id.values():
                        # add to count dictionary
                        res_ = JobackGroupData(
                            id=group_name,
                            name=group_name,
                            count=float(group_value),
                            data=self._get_group_contribution_data(group_name)
                        )
                        # append
                        valid_groups[group_name] = res_
            elif isinstance(self.group_contributions, JobackGroupContributions):
                # ! dataclass type
                # iterate over dataclass fields
                for field_name, field_info in JobackGroupContributions.model_fields.items():
                    # get field alias (Joback group name)
                    alias = field_info.alias

                    # check if field is None
                    if alias is None:
                        continue

                    # value stored in the model instance = use field_name
                    group_unit: GroupUnit = getattr(
                        self.group_contributions,
                        field_name
                    )

                    # check if group value is greater than 0
                    if group_unit.value > 0:
                        # check if group exists in Joback parameters
                        if alias in self.group_id.values():
                            # add to count dictionary
                            res_ = JobackGroupData(
                                id=alias,
                                name=field_name,
                                count=float(group_unit.value),
                                data=self._get_group_contribution_data(alias)
                            )
                            # append
                            valid_groups[alias] = res_

            else:
                logger.error("Invalid type for group contributions!")
                return valid_groups

            return valid_groups
        except Exception as e:
            raise Exception("Checking group contributions failed!, ", e)

    def _calc_sigma(
            self
    ):
        '''
        Calculates sigma for all valid groups.

        '''
        try:
            # SECTION: calculate sigma
            # initialize critical temperature
            sigma = {
                'Tc': 0.0,
                'Pc': 0.0,
                'Vc': 0.0,
                'Tb': 0.0,
                'Tf': 0.0,
                'EnFo_IG': 0.0,
                'GiEnFo_IG': 0.0,
                'a': 0.0,
                'b': 0.0,
                'c': 0.0,
                'd': 0.0,
                'EnFus': 0.0,
                'EnVap': 0.0
            }

            # iterate over valid groups
            for group_name, group_info in self.valid_groups.items():
                # get group count
                group_count = group_info.count
                # get contribution data
                contribution_data = group_info.data
                # get contribution
                val_Tc = contribution_data.get('Tc', None)
                val_Pc = contribution_data.get('Pc', None)
                val_Vc = contribution_data.get('Vc', None)
                val_Tb = contribution_data.get('Tb', None)
                val_Tm = contribution_data.get('Tf', None)
                val_EnFo_IG = contribution_data.get('EnFo_IG', None)
                val_GiEnFo_IG = contribution_data.get('GiEnFo_IG', None)
                val_a = contribution_data.get('a', None)
                val_b = contribution_data.get('b', None)
                val_c = contribution_data.get('c', None)
                val_d = contribution_data.get('d', None)
                val_EnFus = contribution_data.get('EnFus', None)
                val_EnVap = contribution_data.get('EnVap', None)

                # check if contribution is valid
                if val_Tc is not None:
                    # update critical temperature
                    sigma['Tc'] += group_count * float(val_Tc)

                if val_Pc is not None:
                    # update critical temperature
                    sigma['Pc'] += group_count * float(val_Pc)

                if val_Vc is not None:
                    # update critical temperature
                    sigma['Vc'] += group_count * float(val_Vc)

                if val_Tb is not None:
                    # update critical temperature
                    sigma['Tb'] += group_count * float(val_Tb)

                if val_Tm is not None:
                    # update critical temperature
                    sigma['Tf'] += group_count * float(val_Tm)

                if val_EnFo_IG is not None:
                    # update critical temperature
                    sigma['EnFo_IG'] += group_count * float(val_EnFo_IG)

                if val_GiEnFo_IG is not None:
                    # update critical temperature
                    sigma['GiEnFo_IG'] += group_count * float(val_GiEnFo_IG)

                if val_a is not None:
                    # update critical temperature
                    sigma['a'] += group_count * float(val_a)

                if val_b is not None:
                    # update critical temperature
                    sigma['b'] += group_count * float(val_b)

                if val_c is not None:
                    # update critical temperature
                    sigma['c'] += group_count * float(val_c)

                if val_d is not None:
                    # update critical temperature
                    sigma['d'] += group_count * float(val_d)

                if val_EnFus is not None:
                    # update critical temperature
                    sigma['EnFus'] += group_count * float(val_EnFus)

                if val_EnVap is not None:
                    sigma['EnVap'] += group_count * float(val_EnVap)

            return sigma
        except Exception as e:
            raise Exception("Calculating critical temperature failed!, ", e)

    def _calc(
            self
    ):
        '''
        Calculates properties using Joback method.

        Returns
        -------
        properties : dict
            Dictionary of calculated properties.
        '''
        try:
            # SECTION: calculate properties
            properties: Dict[str, EstimatedProp] = {}

            # SECTION: calculate sigma
            sigma = self._calc_sigma()

            # NOTE: freezing point temperature
            properties['freezing_point_temperature'] = EstimatedProp(
                **self._calc_freezing_point_temperature(sigma)
            )

            # NOTE: boiling point temperature
            boiling_point_temp = self._calc_boiling_point_temperature(sigma)
            properties['boiling_point_temperature'] = EstimatedProp(
                **boiling_point_temp
            )

            # NOTE: critical temperature
            res_ = \
                self._calc_critical_temperature(
                    sigma,
                    boiling_point_temperature=boiling_point_temp['value'] if boiling_point_temp else None
                )
            properties['critical_temperature'] = EstimatedProp(
                **res_
            )

            # NOTE: critical pressure
            properties['critical_pressure'] = EstimatedProp(
                **self._calc_critical_pressure(sigma)
            )

            # NOTE: critical volume
            properties['critical_volume'] = EstimatedProp(
                **self._calc_critical_volume(sigma)
            )

            # NOTE: standard enthalpy of formation in ideal gas
            properties['standard_enthalpy_of_formation_ideal_gas'] = EstimatedProp(
                **self._calc_standard_enthalpy_of_formation_ideal_gas(sigma)
            )

            # NOTE: standard Gibbs energy of formation in ideal gas
            properties['standard_gibbs_energy_of_formation_ideal_gas'] = EstimatedProp(
                **self._calc_standard_gibbs_energy_of_formation_ideal_gas(sigma)
            )

            # NOTE: standard enthalpy of fusion
            properties['standard_enthalpy_of_fusion'] = EstimatedProp(
                **self._calc_standard_enthalpy_of_fusion(sigma)
            )

            # NOTE: standard enthalpy of vaporization
            properties['standard_enthalpy_of_vaporization'] = EstimatedProp(
                **self._calc_standard_enthalpy_of_vaporization(sigma)
            )

            # NOTE: heat capacity function
            properties['heat_capacity'] = EstimatedProp(
                **self._calc_heat_capacity(sigma)
            )

            return properties
        except Exception as e:
            raise Exception("Calculating properties failed!, ", e)

    def _calc_freezing_point_temperature(
            self,
            sigma: Dict[str, float]
    ):
        """
        Calculates the freezing point temperature using Joback method.

        Parameters
        ----------
        sigma : Dict[str, float]
            Dictionary of sigma values.

        Returns
        -------
        Tf : Dict
            Freezing point temperature (K).
        """
        try:
            # calc
            Tf = 122.5 + sigma['Tf']
            return {
                'value': Tf,
                'unit': 'K',
                'symbol': 'Tf'
            }
        except Exception as e:
            logger.error(
                f"Calculating freezing point temperature failed!, {e}")
            return {'value': None, 'unit': 'K', 'symbol': 'Tf'}

    def _calc_boiling_point_temperature(
            self,
            sigma: Dict[str, float]
    ):
        """
        Calculates the boiling point temperature using Joback method.

        Parameters
        ----------
        sigma : Dict[str, float]
            Dictionary of sigma values.

        Returns
        -------
        Tb : dict
            Boiling point temperature (K).
        """
        try:
            # calc
            Tb = 198.2 + sigma['Tb']
            return {
                'value': Tb,
                'unit': 'K',
                'symbol': 'Tb'
            }
        except Exception as e:
            logger.error(
                f"Calculating boiling point temperature failed!, {e}")
            return {'value': None, 'unit': 'K', 'symbol': 'Tb'}

    def _calc_critical_temperature(
            self,
            sigma: Dict[str, float],
            boiling_point_temperature: float | None
    ):
        """
        Calculates the critical temperature using Joback method.

        Parameters
        ----------
        sigma : Dict[str, float]
            Dictionary of sigma values.
        boiling_point_temperature : float
            Boiling point temperature.

        Returns
        -------
        Tc : dict
            Critical temperature (K).
        """
        try:
            # check
            if boiling_point_temperature is None:
                logger.error(
                    f"Boiling point temperature is required for calculating critical temperature!")
                return {'value': None, 'unit': 'K', 'symbol': 'Tc'}

            # calc
            Tc = boiling_point_temperature / (
                0.584 +
                0.965 * sigma['Tc'] -
                sigma['Tc'] ** 2
            )
            return {
                'value': Tc,
                'unit': 'K',
                'symbol': 'Tc'
            }
        except Exception as e:
            logger.error(
                f"Calculating critical temperature failed!, {e}")
            return {'value': None, 'unit': 'K', 'symbol': 'Tc'}

    def _calc_critical_pressure(
            self,
            sigma: Dict[str, float],
    ):
        """
        Calculates the critical pressure using Joback method.

        Parameters
        ----------
        sigma : Dict[str, float]
            Dictionary of sigma values.

        Returns
        -------
        Pc: dict
            Critical pressure (bar).
        """
        try:
            # calc
            Pc = pow(
                0.113 +
                0.0032 * self.total_atoms_number -
                sigma['Pc'],
                -2
            )
            return {
                'value': Pc,
                'unit': 'bar',
                'symbol': 'Pc'
            }
        except Exception as e:
            logger.error(
                f"Calculating critical pressure failed!, {e}")
            return {'value': None, 'unit': 'bar', 'symbol': 'Pc'}

    def _calc_critical_volume(
            self,
            sigma: Dict[str, float],
    ):
        """
        Calculates the critical volume using Joback method.

        Parameters
        ----------
        sigma : Dict[str, float]
            Dictionary of sigma values.

        Returns
        -------
        Vc : dict
            Critical volume (cm³/mol).
        """
        try:
            # calc
            Vc = 17.5 + sigma['Vc']
            return {
                'value': Vc,
                'unit': 'cm3/mol',
                'symbol': 'Vc'
            }
        except Exception as e:
            logger.error(
                f"Calculating critical volume failed!, {e}")
            return {'value': None, 'unit': 'cm3/mol', 'symbol': 'Vc'}

    def _calc_standard_enthalpy_of_formation_ideal_gas(
            self,
            sigma: Dict[str, float],
    ):
        """
        Calculates the standard enthalpy of formation in ideal gas using Joback method.

        Parameters
        ----------
        sigma : Dict[str, float]
            Dictionary of sigma values.

        Returns
        -------
        EnFo_IG : dict
            Standard enthalpy of formation in ideal gas (kJ/mol).
        """
        try:
            # calc
            EnFo_IG = 68.29 + sigma['EnFo_IG']
            return {
                'value': EnFo_IG,
                'unit': 'kJ/mol',
                'symbol': 'EnFo_IG'
            }
        except Exception as e:
            logger.error(
                f"Calculating standard enthalpy of formation in ideal gas failed!, {e}")
            return {'value': None, 'unit': 'kJ/mol', 'symbol': 'EnFo_IG'}

    def _calc_standard_gibbs_energy_of_formation_ideal_gas(
            self,
            sigma: Dict[str, float],
    ):
        """
        Calculates the standard Gibbs energy of formation in ideal gas using Joback method.

        Parameters
        ----------
        sigma : Dict[str, float]
            Dictionary of sigma values.

        Returns
        -------
        GiEnFo_IG : dict
            Standard Gibbs energy of formation in ideal gas (kJ/mol).
        """
        try:
            # calc
            GiEnFo_IG = 53.88 + sigma['GiEnFo_IG']
            return {
                'value': GiEnFo_IG,
                'unit': 'kJ/mol',
                'symbol': 'GiEnFo_IG'
            }
        except Exception as e:
            logger.error(
                f"Calculating standard Gibbs energy of formation in ideal gas failed!, {e}")
            return {'value': None, 'unit': 'kJ/mol', 'symbol': 'GiEnFo_IG'}

    def _calc_standard_enthalpy_of_fusion(
            self,
            sigma: Dict[str, float],
    ):
        """
        Calculates the standard enthalpy of fusion using Joback method.

        Parameters
        ----------
        sigma : Dict[str, float]
            Dictionary of sigma values.

        Returns
        -------
        EnFus : dict
            Standard enthalpy of fusion (kJ/mol).
        """
        try:
            # calc
            EnFus = -0.88 + sigma['EnFus']
            return {
                'value': EnFus,
                'unit': 'kJ/mol',
                'symbol': 'EnFus'
            }
        except Exception as e:
            logger.error(
                f"Calculating standard enthalpy of fusion failed!, {e}")
            return {'value': None, 'unit': 'kJ/mol', 'symbol': 'EnFus'}

    def _calc_standard_enthalpy_of_vaporization(
            self,
            sigma: Dict[str, float],
    ):
        """
        Calculates the standard enthalpy of vaporization using Joback method.

        Parameters
        ----------
        sigma : Dict[str, float]
            Dictionary of sigma values.

        Returns
        -------
        EnVap : dict
            Standard enthalpy of vaporization (kJ/mol).
        """
        try:
            # calc
            EnVap = 15.30 + sigma['EnVap']
            return {
                'value': EnVap,
                'unit': 'kJ/mol',
                'symbol': 'EnVap'
            }
        except Exception as e:
            logger.error(
                f"Calculating standard enthalpy of vaporization failed!, {e}")
            return {'value': None, 'unit': 'kJ/mol', 'symbol': 'EnVap'}

    def _calc_heat_capacity(
            self,
            sigma: Dict[str, float],
    ):
        """
        Create a placeholder for heat capacity calculation.

        Parameters
        ----------
        sigma : Dict[str, float]
            Dictionary of sigma values.

        Returns
        -------
        Cp_func : dict
            Heat capacity function Cp(T).
        """
        try:
            # create heat capacity function
            res_ = JobackHeatCapacity(
                a=sigma['a'],
                b=sigma['b'],
                c=sigma['c'],
                d=sigma['d']
            )

            return {
                'value': res_.Cp,
                'unit': 'J/mol·K',
                'symbol': 'Cp_IG'
            }
        except Exception as e:
            logger.error(
                f"Creating heat capacity function failed!, {e}")
            return {'value': None, 'unit': 'J/mol·K', 'symbol': 'Cp_IG'}
