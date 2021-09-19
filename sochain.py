import random
import time
import threading
import requests

import work_with_files

size_of_search = 1000


def check_address_valid(some_address, blockchain='BTC'):
    response = requests.get(f'https://chain.so/api/v2/is_address_valid/{blockchain}/{str(some_address)}')
    if response.status_code == 200:
        content = response.json()
        return content['data']['is_valid'], some_address
    if response.status_code == 404:
        return False, some_address

# функция идет по адресам который удалось найти, смотрит их транзы и ищет там новые адреса, но очень отпимизирована, но это пока мой потолок



def find_all_user_wallets(some_address, blockhain='BTC', already_checked_tx=list(), already_checked_address=list(), should_clean_up = True):
    if should_clean_up:
        already_checked_address = []
        already_checked_tx = []
    already_checked_address.append(some_address)
    spent_tx_list = []
    response = requests.get(f'https://chain.so/api/v2/get_tx_spent/{blockhain}/{str(some_address)}')
    if response.status_code == 200:
        content = response.json()
        for tx in content['data']['txs'][::-1]:
            if tx['txid'] not in spent_tx_list:
                if len(spent_tx_list) > size_of_search:
                    break
                spent_tx_list.append(tx['txid'])
    tx_inputs = []
    for tx in spent_tx_list:
        if tx not in already_checked_tx:
            response = requests.get(f'https://chain.so//api/v2/get_tx_inputs/{blockhain}/{tx}')
            if response.status_code == 200:
                content = response.json()
                for address in content['data']['inputs']:
                    if address['address'] not in tx_inputs:
                        tx_inputs.append(address['address'])
                        if len(tx_inputs) > size_of_search:
                            break
                already_checked_tx.append(tx)
    if len(tx_inputs) > size_of_search:
        already_checked_address += tx_inputs
        return already_checked_address
    for address_to_chek in tx_inputs:
        if address_to_chek not in already_checked_address:
            if len(already_checked_address) < size_of_search:
                find_all_user_wallets(address_to_chek, blockhain='BTC', already_checked_tx=already_checked_tx, already_checked_address=already_checked_address, should_clean_up = False)
    return already_checked_address


def who_send_money_to_user(list_of_user_addresses, blockhain='BTC'):
    received_tx_list = []
    money_senders_list = []
    for address in list_of_user_addresses:
        response = requests.get(f'https://chain.so/api/v2/get_tx_received/{blockhain}/{str(address)}')
        if response.status_code == 200:
            content = response.json()
            for tx in content['data']['txs'][::-1]:
                if tx['txid'] not in received_tx_list:
                    received_tx_list.append(tx['txid'])
                    if len(received_tx_list) > size_of_search:
                        break
    for tx in received_tx_list:
        response = requests.get(f'https://chain.so//api/v2/get_tx_inputs/{blockhain}/{tx}')
        if response.status_code == 200:
            content = response.json()
            for transaction_details in content['data']['inputs']:
                if transaction_details['address'] not in money_senders_list:
                    if len(money_senders_list) <= size_of_search:
                        money_senders_list.append(transaction_details['address'])
                    else:
                        return money_senders_list
    return money_senders_list


def sending_money_by_user(list_of_user_addresses, blockhain='BTC'):
    send_tx_list = []
    money_receiver_list = []
    for address in list_of_user_addresses:
        response = requests.get(f'https://chain.so/api/v2/get_tx_spent/{blockhain}/{str(address)}')
        if response.status_code == 200:
            content = response.json()
            for tx in content['data']['txs'][::-1]:
                if tx['txid'] not in send_tx_list:
                    send_tx_list.append(tx['txid'])
                    if len(send_tx_list) > size_of_search:
                        break
    for tx in send_tx_list:
        response = requests.get(f'https://chain.so//api/v2/get_tx_outputs/{blockhain}/{tx}')
        if response.status_code == 200:
            content = response.json()
            for transaction_details in content['data']['outputs']:
                if transaction_details['address'] not in money_receiver_list:
                    if len(money_receiver_list) < size_of_search:
                        money_receiver_list.append(transaction_details['address'])
                    else:
                        return money_receiver_list
    return money_receiver_list