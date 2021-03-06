# -*- coding: utf-8 -*-
from copy import deepcopy
from ocelot.data_helpers import production_volume
from ocelot.errors import OverlappingMarkets, MissingSupplier
from ocelot.transformations.locations.markets import *


def generate_dataset(location, name='f', rp='b', kind="market activity"):
    return {
        'name': name,
        'reference product': rp,
        'location': location,
        'code': location + name + rp,
        # 'technology level': 'current',
        'exchanges': [{'type': 'reference product'}],
    }

def reformat_suppliers(result):
    result_as_dict = {ds['code']: sorted([exc['code'] for exc in ds.get('suppliers', [])])
                      for ds in result}
    return {k: v for k, v in result_as_dict.items() if v}


###
### apportion_market_suppliers_to_consumers
###

def test_astc_no_suppliers():
    consumers = [
        generate_dataset('UCTE without France'),
    ]
    apportion_market_suppliers_to_consumers(consumers, [])

def test_astc_nonlinked_suppliers():
    consumers = [
        generate_dataset('UCTE without France'),
    ]
    suppliers = [
        generate_dataset('FR'),
    ]
    apportion_market_suppliers_to_consumers(consumers, suppliers)

def test_astc_exclude_supplier():
    consumers = [
        generate_dataset('NAFTA'),
    ]
    suppliers = [
        generate_dataset('CH'),
        generate_dataset('MX'),
    ]
    expected = {
        'NAFTAfb': ['MXfb'],
    }
    apportion_market_suppliers_to_consumers(consumers, suppliers)
    assert reformat_suppliers(consumers) == expected

def test_astc_plain():
    consumers = [
        generate_dataset('UCTE without France'),
        generate_dataset('RU'),
    ]
    suppliers = [
        generate_dataset('FR'),
        generate_dataset('Russia (Asia)'),
        generate_dataset('DE'),
        generate_dataset('MY'),
    ]
    expected = {
        'UCTE without Francefb': ['DEfb'],
        'RUfb': ['Russia (Asia)fb'],
    }
    apportion_market_suppliers_to_consumers(consumers, suppliers)
    assert reformat_suppliers(consumers) == expected

def test_astc_global_consumer():
    consumers = [
        generate_dataset('GLO'),
    ]
    suppliers = [
        generate_dataset('FR'),
        generate_dataset('Russia (Asia)'),
        generate_dataset('DE'),
        generate_dataset('MY'),
    ]
    expected = {
        'GLOfb': ['DEfb', 'FRfb', 'MYfb', 'Russia (Asia)fb'],
    }
    apportion_market_suppliers_to_consumers(consumers, suppliers)
    assert reformat_suppliers(consumers) == expected

def test_astc_global_consumer_row_supplier():
    consumers = [
        generate_dataset('GLO'),
    ]
    suppliers = [
        generate_dataset('FR'),
        generate_dataset('Russia (Asia)'),
        generate_dataset('RoW'),
        generate_dataset('DE'),
        generate_dataset('MY'),
    ]
    expected = {
        'GLOfb': ['DEfb', 'FRfb', 'MYfb', 'RoWfb', 'Russia (Asia)fb'],
    }
    apportion_market_suppliers_to_consumers(consumers, suppliers)
    assert reformat_suppliers(consumers) == expected

def test_astc_global_consumer_row_only_supplier():
    consumers = [
        generate_dataset('GLO'),
    ]
    suppliers = [
        generate_dataset('RoW'),
    ]
    expected = {
        'GLOfb': ['RoWfb'],
    }
    apportion_market_suppliers_to_consumers(consumers, suppliers)
    assert reformat_suppliers(consumers) == expected

def test_astc_row_consumer():
    consumers = [
        generate_dataset('UCTE without France'),
        generate_dataset('RU'),
        generate_dataset('RoW'),
    ]
    suppliers = [
        generate_dataset('FR'),
        generate_dataset('Russia (Asia)'),
        generate_dataset('DE'),
        generate_dataset('MY'),
    ]
    expected = {
        'UCTE without Francefb': ['DEfb'],
        'RUfb': ['Russia (Asia)fb'],
        'RoWfb': ['FRfb', 'MYfb']
    }
    apportion_market_suppliers_to_consumers(consumers, suppliers)
    assert reformat_suppliers(consumers) == expected

def test_astc_row_supplier():
    consumers = [
        generate_dataset('UCTE without France'),
        generate_dataset('RoW'),
    ]
    suppliers = [
        generate_dataset('RER'),
        generate_dataset('RoW'),
    ]
    # If we change here to make RoW always a backup
    # If geomatched it is exlcuded
    # expected = {
    #     'UCTE without Francefb': ['RoWfb'],
    #     'RoWfb': ['RoWfb']
    # }
    expected = {
        'RoWfb': ['RoWfb']
    }
    apportion_market_suppliers_to_consumers(consumers, suppliers)
    assert reformat_suppliers(consumers) == expected

def test_astc_row_not_in_smaller_consuming_region():
    consumers = [
        generate_dataset('NAFTA'),
    ]
    suppliers = [
        generate_dataset('RoW'),
        generate_dataset('MX'),
    ]
    expected = {
        'NAFTAfb': ['MXfb'],
    }
    apportion_market_suppliers_to_consumers(consumers, suppliers)
    assert reformat_suppliers(consumers) == expected

def test_astc_row_supplier_and_consumer_supplier_within_consumer():
    consumers = [
        generate_dataset('UCTE'),
        generate_dataset('RoW'),
    ]
    suppliers = [
        generate_dataset('CH'),
        generate_dataset('Europe without Switzerland'),
        generate_dataset('RoW'),
    ]
    expected = {
        'UCTEfb': ['CHfb'],
        'RoWfb': ['RoWfb']
    }
    apportion_market_suppliers_to_consumers(consumers, suppliers)
    assert reformat_suppliers(consumers) == expected

def test_astc_row_supplier_and_consumer_consumer_within_supplier():
    consumers = [
        generate_dataset('RER'),
        generate_dataset('NAFTA'),
        generate_dataset('RoW'),
    ]
    suppliers = [
        generate_dataset('CH'),
        generate_dataset('Europe without Switzerland'),
        generate_dataset('RoW'),
    ]
    # If we change here to make RoW always a backup
    # RoW excluded from supplier because it covers NAFTA as well
    # expected = {
    #     'NAFTAfb': ['RoWfb'], # Fallback
    #     'RoWfb': ['RoWfb'],
    #     'RERfb': ['CHfb', 'Europe without Switzerlandfb']
    # }
    expected = {
        'RERfb': ['CHfb', 'Europe without Switzerlandfb']
    }
    apportion_market_suppliers_to_consumers(consumers, suppliers)
    assert reformat_suppliers(consumers) == expected

def test_astc_row_supplier_and_consumer_overlap_but_not_contained():
    consumers = [
        generate_dataset('NAFTA'),
        generate_dataset('WEU'),
        generate_dataset('RoW'),
    ]
    suppliers = [
        generate_dataset('RER'),
        generate_dataset('RoW'),
    ]
    # If we change here to make RoW always a backup
    # and not compare georesolved RoW to georesolved RoW
    # expected = {
    #     'NAFTAfb': ['RoWfb'], # Fallback
    #     'WEUfb': ['RoWfb'],   # Contained by
    #     'RoWfb': ['RoWfb'],   # Fallback
    # }
    expected = {}
    apportion_market_suppliers_to_consumers(consumers, suppliers)
    assert reformat_suppliers(consumers) == expected

def test_astc_row_consumer_glo_supplier():
    consumers = [
        generate_dataset('WEU'),
        generate_dataset('RoW'),
    ]
    suppliers = [
        generate_dataset('GLO'),
    ]
    # If we change here to make GLO/RoW always a backup
    # expected = {
    #     'WEUfb': ['GLOfb'],
    #     'RoWfb': ['GLOfb'],
    # }
    expected = {}
    apportion_market_suppliers_to_consumers(consumers, suppliers)
    assert reformat_suppliers(consumers) == expected

def test_astc_larger_regional_supplier():
    consumers = [
        generate_dataset('WEU'),
    ]
    suppliers = [
        generate_dataset('RoW'),
        generate_dataset('RER'),
    ]
    # If we change here to make GLO/RoW always a backup
    # expected = {
    #     'WEUfb': ['RoWfb'],
    # }
    expected = {}
    apportion_market_suppliers_to_consumers(consumers, suppliers)
    assert reformat_suppliers(consumers) == expected

def test_astc_single_global_supplier():
    consumers = [
        generate_dataset('WEU'),
    ]
    suppliers = [
        generate_dataset('GLO'),
    ]
    # If we change here to make GLO/RoW always a backup
    # expected = {
    #     'WEUfb': ['GLOfb'],
    # }
    expected = {}
    apportion_market_suppliers_to_consumers(consumers, suppliers)
    assert reformat_suppliers(consumers) == expected


###
### add_suppliers_to_markets
###

def test_add_suppliers_to_markets():
    given = [{
        'type': 'skip me',
        'code': 'foo',
    }, {
        'code': 'cCA',
        'type': 'transforming activity',
        'reference product': 'foo',
        'name': '',
        'location': 'CA',
        'exchanges': [{'type': 'reference product'}],
    }, {
        'code': 'cMX',
        'type': 'transforming activity',
        'reference product': 'foo',
        'name': '',
        'location': 'MX',
        'exchanges': [{'type': 'reference product'}],
    }, {
        'code': 'cFR',
        'type': 'transforming activity',
        'reference product': 'foo',
        'name': '',
        'location': 'FR',
        'exchanges': [{'type': 'reference product'}],
    }, {
        'code': 'cNAFTA',
        'type': 'market activity',
        'reference product': 'foo',
        'name': '',
        'location': 'NAFTA',
    }, {
        'code': 'cRER',
        'type': 'market activity',
        'reference product': 'foo',
        'name': '',
        'location': 'RER',
    }, {
        'code': 'cDE',
        'type': 'transforming activity',
        'reference product': 'bar',
        'name': '',
        'location': 'DE',
        'exchanges': [{'type': 'reference product'}],
    }, {
        'code': 'cZA',
        'type': 'transforming activity',
        'reference product': 'bar',
        'name': '',
        'location': 'ZA',
        'exchanges': [{'type': 'reference product'}],
    }, {
        'code': 'cRoW',
        'type': 'market activity',
        'reference product': 'bar',
        'name': '',
        'location': 'RoW',
    }]
    expected = {
        'cRoW': ['cDE', 'cZA'],
        'cRER': ['cFR'],
        'cNAFTA': ['cCA', 'cMX'],
    }
    assert reformat_suppliers(add_suppliers_to_markets(given)) == expected

def test_add_suppliers_to_markets_no_consumers():
    given = [{
        'code': 'cCA',
        'type': 'transforming activity',
        'reference product': 'foo',
        'name': '',
        'location': 'CA',
        'exchanges': [{'type': 'reference product'}],
    }, {
        'code': 'cMX',
        'type': 'transforming activity',
        'reference product': 'foo',
        'name': '',
        'location': 'MX',
        'exchanges': [{'type': 'reference product'}],
    }, {
        'code': 'cFR',
        'type': 'transforming activity',
        'reference product': 'foo',
        'name': '',
        'location': 'FR',
        'exchanges': [{'type': 'reference product'}],
    }, {
        'code': 'cNAFTA',
        'type': 'market activity',
        'reference product': 'bar',
        'name': '',
        'location': 'NAFTA',
    }, {
        'code': 'cRER',
        'type': 'market activity',
        'reference product': 'bar',
        'name': '',
        'location': 'RER',
    }]
    assert reformat_suppliers(add_suppliers_to_markets(given)) == {}


###
### allocate_all_market_suppliers
###

def test_allocate_all_market_suppliers():
    given = [{
        'location': 'dining room',
        'name': 'dinner',
        'type': 'market activity',
        'exchanges': [{
            'amount': 24,
            'name': 'salad',
            'type': 'reference product',
            'unit': '',
        }],
        'suppliers': [{
            'code': 'up',
            'location': 'upstairs',
            'name': '',
            'production volume': {'amount': 2},
            'unit': '',
        }, {
            'code': 'do',
            'location': 'downstairs',
            'name': '',
            'production volume': {'amount': 10},
            'unit': '',
        }]
    }]
    expected = [{
        'amount': 24,
        'name': 'salad',
        'type': 'reference product',
        'unit': '',
    }, {
        'amount': 2 / 12 * 24,
        'code': 'up',
        'name': '',
        'tag': 'intermediateExchange',
        'type': 'from technosphere',
        'unit': '',
    }, {
        'amount': 10 / 12 * 24,
        'code': 'do',
        'name': '',
        'tag': 'intermediateExchange',
        'type': 'from technosphere',
        'unit': '',
    }]
    assert allocate_all_market_suppliers(given)[0]['exchanges'] == expected

def test_allocate_all_market_suppliers_single_supplier():
    given = [{
        'location': 'dining room',
        'name': 'dinner',
        'type': 'market activity',
        'exchanges': [{
            'amount': 24,
            'name': 'salad',
            'type': 'reference product',
        }],
        'suppliers': [{
            'code': 'up',
            'location': 'upstairs',
            'name': '',
            'production volume': {'amount': 20},
            'unit': '',
        }]
    }]
    expected = [{
        'amount': 24,
        'name': 'salad',
        'type': 'reference product',
    }, {
        'amount': 24,
        'code': 'up',
        'name': '',
        'tag': 'intermediateExchange',
        'type': 'from technosphere',
        'unit': '',
    }]
    assert allocate_all_market_suppliers(deepcopy(given))[0]['exchanges'] == expected


###
### allocate_suppliers
###

def test_allocate_suppliers_no_production_volume_single_supplier():
    given = {
        'name': '',
        'location': '',
        'reference product': '',
        'exchanges': [{
            'type': 'reference product',
            'name': '',
            'amount': 1,
        }],
        'suppliers': [{
            'production volume': {'amount': 0},
            'name': 'a',
            'unit': 'b',
            'code': 'foo',
            'location': '',
        }]
    }
    expected = {
        'name': '',
        'location': '',
        'reference product': '',
        'exchanges': [{
            'type': 'reference product',
            'name': '',
            'amount': 1,
        }, {
            'amount': 1,
            'name': 'a',
            'unit': 'b',
            'code': 'foo',
            'type': 'from technosphere',
            'tag': 'intermediateExchange',
        }],
        'suppliers': [{
            'production volume': {'amount': 4321},
            'name': 'a',
            'unit': 'b',
            'code': 'foo',
            'location': '',
        }]
    }
    assert allocate_suppliers(given) == expected

def test_allocate_suppliers_no_production_volume():
    given = {
        'name': '',
        'location': '',
        'exchanges': [{
            'type': 'reference product',
            'name': '',
            'amount': 1,
        }],
        'suppliers': [{
            'production volume': {'amount': 0}
        }, {
            'production volume': {'amount': 0}
        }]
    }
    assert allocate_suppliers(given) is None

def test_allocate_suppliers_skip_zero_amount():
    given = {
        'exchanges': [{
            'type': 'reference product',
            'name': '',
            'amount': 1,
        }],
        'suppliers': [{
            'name': 'skip me',
            'amount': 1,
            'production volume': {'amount': 0},
        }, {
            'name': 'keep me',
            'unit': '',
            'location': '',
            'code': '',
            'amount': 1,
            'production volume': {'amount': 1},

        }]
    }
    expected = {
        'exchanges': [{
            'type': 'reference product',
            'name': '',
            'amount': 1,
        }, {
            'amount': 1,
            'code': '',
            'name': 'keep me',
            'tag': 'intermediateExchange',
            'type': 'from technosphere',
            'unit': '',
        }],
        'suppliers': [{
            'name': 'skip me',
            'amount': 1,
            'production volume': {'amount': 0},
        }, {
            'name': 'keep me',
            'unit': '',
            'location': '',
            'code': '',
            'amount': 1,
            'production volume': {'amount': 1},

        }]
    }
    assert allocate_suppliers(given) == expected


###
### add_recycled_content_suppliers_to_markets
###

def test_add_recycled_content_suppliers_to_markets():
    given = [{
        'code': 'cCA',
        'type': 'transforming activity',
        'reference product': 'foo, Recycled Content cut-off',
        'name': '',
        'location': 'CA',
        'exchanges': [{'type': 'reference product'}],
    }, {
        'code': 'cMX',
        'type': 'transforming activity',
        'reference product': 'foo, Recycled Content cut-off',
        'name': '',
        'location': 'MX',
        'exchanges': [{'type': 'reference product'}],
    }, {
        'code': 'cFR',
        'type': 'transforming activity',
        'reference product': 'foo, Recycled Content cut-off',
        'name': '',
        'location': 'FR',
        'exchanges': [{'type': 'reference product'}],
    }, {
        'code': 'cNAFTA',
        'type': 'market activity',
        'reference product': 'foo',
        'name': '',
        'location': 'NAFTA',
    }, {
        'code': 'cRER',
        'type': 'market activity',
        'reference product': 'foo',
        'name': '',
        'location': 'RER',
    }, {
        'code': 'cDE',
        'type': 'transforming activity',
        'reference product': 'bar',
        'name': '',
        'location': 'DE',
        'exchanges': [{'type': 'reference product'}],
    }, {
        'code': 'cZA',
        'type': 'transforming activity',
        'reference product': 'bar',
        'name': '',
        'location': 'ZA',
        'exchanges': [{'type': 'reference product'}],
    }, {
        'code': 'cRoW',
        'type': 'market activity',
        'reference product': 'bar',
        'name': '',
        'location': 'RoW',
    }]
    expected = {
        'cNAFTA': ['cCA', 'cMX'],
        'cRER': ['cFR'],
    }
    assert reformat_suppliers(add_recycled_content_suppliers_to_markets(given)) == expected

###
### production volumes
###

def test_update_market_production_volumes():
    given = [{
        'name': '',
        'type': 'foo',
        'location': '',
        'exchanges': [{
            'name': '',
            'type': 'reference product',
            'production volume': {}
        }],
        'suppliers': [
            {'production volume': {'amount': 10}},
            {'production volume': {'amount': 20}},
        ]
    }]
    ds = update_market_production_volumes(given, 'foo')[0]
    assert ds['exchanges'][0]['production volume']['amount'] == 30

def test_update_market_production_volumes_activity_link():
    given = [{
        'name': '',
        'type': 'foo',
        'location': '',
        'exchanges': [{
            'name': '',
            'type': 'reference product',
            'production volume': {'subtracted activity link volume': 15}
        }],
        'suppliers': [
            {'production volume': {
                'original amount': 10,
                'amount': 2,
                'subtracted activity link volume': 8
            }},
            {'production volume': {'amount': 20}},
        ]
    }]
    ds = update_market_production_volumes(given, 'foo')[0]
    assert ds['exchanges'][0]['production volume']['amount'] == 7

def test_update_market_production_volumes_negative_sum():
    given = [{
        'name': '',
        'type': 'foo',
        'location': '',
        'exchanges': [{
            'name': '',
            'type': 'reference product',
            'production volume': {'subtracted activity link volume': 40}
        }],
        'suppliers': [
            {'production volume': {'amount': 10}},
            {'production volume': {'amount': 20}},
        ]
    }]
    ds = update_market_production_volumes(given, 'foo')[0]
    assert ds['exchanges'][0]['production volume']['amount'] == 0

def test_update_market_production_volumes_recursive():
    given = [{
        'name': '',
        'code': 'a',
        'type': 'market group',
        'location': 'GLO',
        'exchanges': [{
            'name': '',
            'type': 'reference product',
            'production volume': {},
        }],
        'suppliers': [
            {'code': 'b'},
            {'code': 'd'},
        ]
    }, {
        'name': '',
        'code': 'b',
        'type': 'market group',
        'location': 'NAFTA',
        'exchanges': [{
            'name': '',
            'type': 'reference product',
            'production volume': {},
        }],
        'suppliers': [
            {'code': 'c'},
            {'production volume': {'amount': 10}, 'code': 'e'}
        ]
    }, {
        'name': '',
        'code': 'c',
        'type': 'market group',
        'location': 'US',
        'exchanges': [{
            'name': '',
            'type': 'reference product',
            'production volume': {},
        }],
        'suppliers': [
            {'production volume': {'amount': 20}, 'code': 'f'}
        ]
    }, {
        'name': '',
        'code': 'd',
        'type': 'market group',
        'location': 'CN',
        'exchanges': [{
            'name': '',
            'type': 'reference product',
            'production volume': {},
        }],
        'suppliers': [
            {'production volume': {'amount': 30}, 'code': 'g'}
        ]
    }]
    update_market_production_volumes(given, 'market group')
    assert production_volume(given[0]) == 60
    assert production_volume(given[1]) == 30
    assert production_volume(given[2]) == 20
    assert production_volume(given[3]) == 30


###
### Utilities
###

def test_delete_suppliers_list():
    given = [{'suppliers': 1}]
    assert delete_suppliers_list(given) == [{}]

def test_assign_fake_pv_to_confidential_datasets():
    given = [{
        'name': "latex production",
        'type': 'transforming activity',
        'location': 'GLO',
        'exchanges': [{
            'type': 'reference product',
            'name': '',
            'production volume': {}
        }]
    }]
    expected = [{
        'name': "latex production",
        'type': 'transforming activity',
        'location': 'GLO',
        'exchanges': [{
            'type': 'reference product',
            'name': '',
            'production volume': {'amount': 1}
        }]
    }]
    assert assign_fake_pv_to_confidential_datasets(given) == expected
    del given[0]['exchanges'][0]['production volume']['amount']
    assert given != expected
    given[0]['type'] = 'market activity'
    assert assign_fake_pv_to_confidential_datasets(given) != expected
    given[0]['type'] = 'transforming activity'
    assert assign_fake_pv_to_confidential_datasets(given) == expected

def test_delete_whitelisted_zero_pv_market_datsets():
    given = [{
        'type': 'market activity',
        'name': 'not market for refinery gas',
        'location': 'GLO',
        'reference product': '',
    }, {
        'type': 'market activity',
        'name': 'market for refinery gas',
        'location': 'GLO',
        'reference product': '',
    }]
    expected = [{
        'type': 'market activity',
        'name': 'not market for refinery gas',
        'location': 'GLO',
        'reference product': '',
    }]
    assert delete_whitelisted_zero_pv_market_datsets(given) == expected
