import random
import time

import requests

import work_with_files


def check_address_valid(some_address, blockchain='BTC'):
    response = requests.get(f'https://chain.so/api/v2/is_address_valid/{blockchain}/{str(some_address)}')
    if response.status_code == 200:
        content = response.json()
        return content['data']['is_valid'], some_address
    if response.status_code == 404:
        return False, some_address

# функция идет по адресам который удалось найти, смотрит их транзы и ищет там новые адреса, но очень отпимизирована, но это пока мой потолок


def find_all_user_wallets(some_address, blockhain='BTC', already_checked_tx=[], already_checked_address=[], addresses_to_check=[]):
    already_checked_address.append(some_address)
    spent_tx_list = []
    time.sleep(1)
    response = requests.get(f'https://chain.so/api/v2/get_tx_spent/{blockhain}/{str(some_address)}')
    if response.status_code == 200:
        content = response.json()
        for tx in content['data']['txs']:
            if tx['txid'] not in spent_tx_list:
                spent_tx_list.append(tx['txid'])
    tx_inputs = []
    for tx in spent_tx_list:
        if tx not in already_checked_tx:
            time.sleep(1)
            response = requests.get(f'https://chain.so//api/v2/get_tx_inputs/{blockhain}/{tx}')
            if response.status_code == 200:
                content = response.json()
                for address in content['data']['inputs']:
                    if address['address'] not in tx_inputs:
                        tx_inputs.append(address['address'])
                        already_checked_tx.append(tx)
    for address_to_chek in tx_inputs:
        if address_to_chek not in already_checked_address:
            find_all_user_wallets(address_to_chek, blockhain='BTC', already_checked_tx=already_checked_tx, already_checked_address=already_checked_address, addresses_to_check=addresses_to_check)
    return already_checked_address


def who_send_money_to_user(list_of_user_addresses, blockhain='BTC'):
    send_tx_list = []
    money_senders_list = []
    for address in list_of_user_addresses:
        time.sleep(1)
        response = requests.get(f'https://chain.so/api/v2/get_tx_received/{blockhain}/{str(address)}')
        if response.status_code == 200:
            content = response.json()
            for tx in content['data']['txs']:
                if tx['txid'] not in send_tx_list:
                    send_tx_list.append(tx['txid'])
    for tx in send_tx_list:
        time.sleep(1)
        response = requests.get(f'https://chain.so//api/v2/get_tx_inputs/{blockhain}/{tx}')
        if response.status_code == 200:
            content = response.json()
            for transaction_details in content['data']['inputs']:
                if transaction_details['address'] not in money_senders_list:
                    money_senders_list.append(transaction_details['address'])
    return money_senders_list


def sending_money_by_user(list_of_user_addresses, blockhain='BTC'):
    send_tx_list = []
    money_receiver_list = []
    for address in list_of_user_addresses:
        time.sleep(1)
        response = requests.get(f'https://chain.so/api/v2/get_tx_spent/{blockhain}/{str(address)}')
        if response.status_code == 200:
            content = response.json()
            for tx in content['data']['txs']:
                if tx['txid'] not in send_tx_list:
                    send_tx_list.append(tx['txid'])
    for tx in send_tx_list:
        time.sleep(1)
        response = requests.get(f'https://chain.so//api/v2/get_tx_outputs/{blockhain}/{tx}')
        if response.status_code == 200:
            content = response.json()
            for transaction_details in content['data']['outputs']:
                if transaction_details['address'] not in money_receiver_list:
                    money_receiver_list.append(transaction_details['address'])
    return money_receiver_list
