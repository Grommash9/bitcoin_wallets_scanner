import random

import requests

import work_with_files


def check_address_valid(some_address, blockchain='BTC'):
    response = requests.get(f'https://chain.so/api/v2/is_address_valid/{blockchain}/{str(some_address)}')
    if response.status_code == 200:
        content = response.json()
        return content['data']['is_valid'], some_address
    if response.status_code == 404:
        return False, some_address


def get_spent_tx_list_from_api(some_address_list, blockhain='BTC'):
    spent_tx_list = []
    response = requests.get(f'https://chain.so/api/v2/get_tx_spent/{blockhain}/{str(some_address_list)}')
    if response.status_code == 200:
        content = response.json()
        for tx in content['data']['txs']:
            if tx['txid'] not in spent_tx_list:
                spent_tx_list.append(tx['txid'])
    return spent_tx_list


def get_tx_inputs(some_tx_list, blockhain='BTC'):
    tx_inputs = []
    for tx in some_tx_list:
        response = requests.get(f'https://chain.so//api/v2/get_tx_inputs/{blockhain}/{tx}')
        if response.status_code == 200:
            content = response.json()
            for address in content['data']['inputs']:
                if address['address'] not in tx_inputs:
                    tx_inputs.append(address['address'])
    return tx_inputs


temp_associated_addresses_dict = dict()


def deeper_anal(some_target_address, clear=True):

    if clear:
        temp_associated_addresses_dict.clear()

    new_addresses_list = get_tx_inputs(get_spent_tx_list_from_api(some_target_address, blockhain='BTC'), blockhain='BTC')

    if len(new_addresses_list) != 0:
        for address in new_addresses_list:
            if address not in temp_associated_addresses_dict.keys():
                temp_associated_addresses_dict[address] = True
        list_to_check = []
        for address_from_dict, state in temp_associated_addresses_dict.items():
            if state:
                temp_associated_addresses_dict[address_from_dict] = False
                list_to_check.append(address_from_dict)
        for addresses_to_check in list_to_check:
            deeper_anal(addresses_to_check, False)
    else:
        return temp_associated_addresses_dict
    return temp_associated_addresses_dict



