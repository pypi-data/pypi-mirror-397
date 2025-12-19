# import libs
import logging
import os
import yaml
import pandas as pd

# NOTE: logger
logger = logging.getLogger(__name__)


class ReferenceLoader:
    '''
    Used to load reference files.
    '''

    def __init__(self):
        pass

    def load_yml_ref(
        self,
        reference_name,
        reference_folder,
    ):
        '''
        Loads YAML reference file.

        Parameters
        ----------
        reference_name : str
            Name of the reference file.
        reference_folder : str
            Folder of the reference file.

        Returns
        -------
        ref_dict : dict
            Dictionary of the reference file.
        '''
        try:
            # reference path
            reference_path = os.path.join(
                reference_folder,
                reference_name
            )
            # load reference file
            with open(reference_path, 'r') as f:
                ref_dict = yaml.safe_load(f)

            # return reference dictionary
            return ref_dict
        except Exception as e:
            raise Exception("Loading reference failed!, ", e)

    def load_csv_ref(
        self,
        reference_name: str,
        reference_folder: str,
    ) -> pd.DataFrame:
        '''
        Loads CSV reference file.

        Parameters
        ----------
        reference_name : str
            Name of the reference file.
        reference_folder : str
            Folder of the reference file.

        Returns
        -------
        ref_df : pd.DataFrame
            DataFrame of the reference file.
        '''
        try:
            # reference path
            reference_path = os.path.join(
                reference_folder,
                reference_name
            )
            # load reference file
            ref_df = pd.read_csv(reference_path)

            # return reference DataFrame
            return ref_df
        except Exception as e:
            raise Exception("Loading reference failed!, ", e)
