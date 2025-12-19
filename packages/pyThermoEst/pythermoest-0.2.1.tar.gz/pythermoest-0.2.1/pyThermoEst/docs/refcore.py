# import libs
import os
# local
from ..util import ReferenceLoader


class RefCore:
    '''
    Core class.
    '''

    def __init__(self):
        # init
        self.ReferenceLoader_ = ReferenceLoader()

        # load reference
        # self.ref_dict = self.load_ref()

    # def load_ref(self):
    #     '''
    #     Load reference files.
    #     '''
    #     # current file path
    #     current_path = os.path.dirname(os.path.abspath(__file__))
    #     # data folder path
    #     data_folder = os.path.join(
    #         current_path,
    #         '..',
    #         'data',
    #     )

    #     # load reference
    #     ref_dict = self.ReferenceLoader_.load_yml_ref(
    #         reference_name='sheet1.yml',
    #         reference_folder=data_folder,
    #     )
    #     # return reference
    #     return ref_dict
