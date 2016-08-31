# -*- coding: utf-8 -*-
from ...errors import InvalidMultioutputDataset
# from ..validation import check_single_output_activity
from .combined import combined_production, combined_production_with_byproducts
from .economic import economic_allocation
from .validation import valid_no_allocation_dataset
from .wastes import waste_treatment_allocation, recycling_allocation
import itertools


@valid_no_allocation_dataset
def no_allocation(dataset):
    return [dataset]


def choose_allocation_method(dataset):
    """Choose from among the following allocation methods:

    * combined production with byproducts
    * combined production without byproducts
    * constrained market
    * economic (including true value allocation)
    * recycling
    * waste treatment

    TODO: It feels strange to get reference product classification from the byproduct classification... this should at least be described a bit.

    The chosen allocation function is returned. For functions which don't need allocation, a dummy function (which does nothing) is returned. Note that all functions returned by this function must return a list of datasets.

    """
    reference_product_classifications = [exc['byproduct classification']
                                         for exc in dataset['exchanges']
                                         if exc['type'] == 'reference product'
                                         and exc['amount'] != 0]
    number_reference_products = len(reference_product_classifications)
    negative_reference_production = any(1 for exc in dataset['exchanges']
                                        if exc['type'] == 'reference product'
                                        and exc['amount'] < 0)
    allocatable_byproducts = any(1 for exc in dataset['exchanges']
                                 if exc['type'] == 'byproduct'
                                 and exc['byproduct classification'] == 'allocatable product'
                                 and exc['amount'] != 0)
    has_conditional_exchange = any(1 for exc in dataset['exchanges']
                                   if exc['type'] == 'byproduct'
                                   and exc['amount'] != 0
                                   and exc.get('conditional exchange'))

    if number_reference_products == 1 and not allocatable_byproducts:
        return no_allocation
    elif dataset['type'] == 'market group':
        return no_allocation
    elif dataset['type'] == 'market activity':
        if has_conditional_exchange:
            return no_allocation  # constrained market
        else:
            return no_allocation
    elif number_reference_products > 1:
        if allocatable_byproducts:
            return combined_production_with_byproducts
        else:
            return combined_production
    elif negative_reference_production:
        # TODO: Should be part of a validation function
        assert len(set(reference_product_classifications)) == 1
        if reference_product_classifications[0] == 'waste':
            return waste_treatment_allocation
        else:
            return recycling_allocation
    else:
        return economic_allocation


def cutoff_allocation(data):
    """Do cutoff system model allocation."""
    return [result  # check_single_output_activity(result)
            for ds in data
            for result in choose_allocation_method(ds)(ds)]