# -*- coding: utf-8 -*-
from .collection import Collection
from .transformations import (
    copy_original_exchange_id,
    ensure_ids_are_unique,
    ensure_mandatory_properties,
    fix_ecoinvent_parameters,
    manage_activity_links,
    normalize_reference_production_amount,
    pv_cleanup,
    update_activity_link_parent_child,
    validate_markets,
    variable_names_are_unique,
)
from .transformations.consequential import (
    delete_activity_links_to_constrained_markets,
    ensure_byproducts_have_alternative_production,
    handle_constrained_markets,
    link_markets_by_technology_level,
    split_combined_production,
)
from .transformations.cutoff import (
    adjust_market_signs_for_allocatable_products,
    cleanup_activity_links,
    cutoff_allocation,
    flip_non_allocatable_byproducts,
    handle_waste_outputs,
    rename_recycled_content_products_after_linking,
)
from .transformations.cutoff.cleanup import (
    drop_rp_activity_links,
    drop_zero_amount_activity_links,
    remove_consequential_exchanges,
)
from .transformations.parameterization import (recalculate_all_parameterized_datasets,
)
from .transformations.locations import (
    link_markets_by_pv,
    link_markets_by_pv_ecoinvent_row,
)
from .wrapper import TransformationWrapper


# Default config for now is cutoff
cutoff_config = Collection(
    'Ecoinvent 3 cutoff by classification system model',
    ensure_ids_are_unique,
    copy_original_exchange_id,
    variable_names_are_unique,
    # There are a *lot* of missing mandatory properties
    # No point adding them to this report
    # ensure_mandatory_properties,
    validate_markets,
    fix_ecoinvent_parameters,
    pv_cleanup,
    remove_consequential_exchanges,
    cleanup_activity_links,
    update_activity_link_parent_child,
    manage_activity_links,
    handle_waste_outputs,
    cutoff_allocation,
    drop_rp_activity_links,
    link_markets_by_pv,
    rename_recycled_content_products_after_linking,
    # extrapolate to database reference year
    flip_non_allocatable_byproducts,
    TransformationWrapper(normalize_reference_production_amount),
    adjust_market_signs_for_allocatable_products,
    # Need to fix many formula errors before this can work
    # recalculate_all_parameterized_datasets,
    # final output processing
)

cutoff_config_ecoinvent_row = Collection(
    'Ecoinvent 3 cutoff by classification system model, with ecoinvent-specific RoW handling',
    ensure_ids_are_unique,
    copy_original_exchange_id,
    variable_names_are_unique,
    # There are a *lot* of missing mandatory properties
    # No point adding them to this report
    # ensure_mandatory_properties,
    validate_markets,
    fix_ecoinvent_parameters,
    pv_cleanup,
    remove_consequential_exchanges,
    cleanup_activity_links,
    update_activity_link_parent_child,
    manage_activity_links,
    handle_waste_outputs,
    cutoff_allocation,
    drop_rp_activity_links,
    link_markets_by_pv_ecoinvent_row,
    rename_recycled_content_products_after_linking,
    # extrapolate to database reference year
    flip_non_allocatable_byproducts,
    TransformationWrapper(normalize_reference_production_amount),
    adjust_market_signs_for_allocatable_products,
    # Need to fix many formula errors before this can work
    # recalculate_all_parameterized_datasets,
    # final output processing
)

consequential_config = Collection(
    'Ecoinvent 3 consequential long-term system model',
    ensure_ids_are_unique,
    copy_original_exchange_id,
    variable_names_are_unique,
    validate_markets,
    fix_ecoinvent_parameters,
    pv_cleanup,
    drop_zero_amount_activity_links,
    split_combined_production,
    delete_activity_links_to_constrained_markets,
    handle_constrained_markets,
    # manage_activity_links,
    ensure_byproducts_have_alternative_production,
    link_markets_by_technology_level,
    # extrapolate to database reference year
    TransformationWrapper(normalize_reference_production_amount),
    # final output processing
)
