# -*- coding: utf-8 -*-
import ocelot
from copy import copy
import numpy as np
import scipy as sp
import pandas as pd
import os

if 0:
    folder = r'C:\python\DB_versions\3.2\undefined\datasets'
    datasets = ocelot.io.extract_ecospold2.extract_directory(folder, False)
    filename = 'ecoinvent_3.2_internal'
    folder = r'C:\ocelot_DB'
    logger = ''
    datasets = ocelot.transformations.find_allocation_method_cutoff.allocation_method(datasets, logger)
    datasets = ocelot.transformations.fix_known_issues_ecoinvent_32.fix_known_issues(
        datasets, '')
    support_excel_folder = r'C:\ocelot_DB'
    support_pkl_folder = r'C:\ocelot_DB'
    data_format = ocelot.utils.read_format_definition()
    if 0:
        ocelot.transformations.activity_overview.build_activity_overview(datasets, 
            support_excel_folder, support_pkl_folder, data_format)
    ocelot.utils.save_file(datasets, folder, filename)
    datasets = datasets[:100]
    filename = 'ecoinvent_3.2_internal_small'
    ocelot.utils.save_file(datasets, folder, filename)
else:
    folder = r'C:\ocelot_DB'
    #filename = 'ecoinvent_3.2_internal_small'
    filename = 'after_economic_allocation'
    #filename = 'ecoinvent_3.2_internal'
    datasets = ocelot.utils.open_file(folder, filename)
    filename = 'activity_overview'
    activity_overview = ocelot.utils.open_file(folder, filename)
    data_format = ocelot.utils.read_format_definition()
    criteria = {
        'allocation method': ['economic allocation'], 
        #'name': [''], 
        #'location': ['CH'], 
                }
    datasets = ocelot.utils.filter_datasets(datasets, activity_overview, criteria)
    datasets = ocelot.transformations.find_allocation_method_cutoff.allocation_method(datasets, '')
    if 0:
        datasets = ocelot.transformations.allocate_cutoff.allocate_datasets_cutoff(
            datasets, data_format, '')
        folder = 'C:\ocelot_DB'
        filename = 'after_economic_allocation'
        ocelot.utils.save_file(datasets, folder, filename)
    system_model_folder = r'C:\python\DB_versions\3.2\cut-off'
    result_folder = r'C:\ocelot_DB'
    ocelot.utils.validate_against_linking(datasets, system_model_folder, data_format, result_folder)
    
        
        #ocelot.utils.print_dataset_to_excel(dataset, folder, data_format, activity_overview)