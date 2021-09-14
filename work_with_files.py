import ast
from copy import deepcopy

import bot
import os
files_path = '/home/wallets_scanner_bot/'
#files_path = 'C:/Users/Гриша/PycharmProjects/bitcoin_wallets_scanner/'


def add_new_user(user_info):

    with open(files_path + 'result_buttons/' + str(user_info.id) + '.txt', 'w') as profile_to_save:
        profile_to_save.write('')
    is_user_new = True
    with open(files_path + 'users_list.txt', 'r') as users_list_file_to_read:
        current_user = str(user_info) + '\n'
        for line in users_list_file_to_read:
            if line == current_user:
                is_user_new = False
    if is_user_new:
        with open(files_path + 'users_list.txt', 'a') as users_list_file_add_line:
            users_list_file_add_line.write(str(user_info) + '\n')
        with open(files_path + 'total_users_count.txt', 'r') as user_count_to_read:
            x = user_count_to_read.readline()
        with open(files_path + 'total_users_count.txt', 'w') as user_count_to_write:
            new_q = int(x) + 1
            user_count_to_write.write(str(new_q))



def add_search_attempt():
    with open(files_path + 'total_search_count.txt', 'r') as total_attempts_file:
        x = total_attempts_file.readline()
    new_q = int(x) + 1
    with open(files_path + 'total_search_count.txt', 'w') as total_attempts_file_to_write:
        total_attempts_file_to_write.write(str(new_q))


def get_users_count():
    with open(files_path + 'total_users_count.txt', 'r') as users_count_file:
        x = users_count_file.readline()
    return str(x)


def get_total_search_count():
    with open(files_path + 'total_search_count.txt', 'r') as search_count_file:
        x = search_count_file.readline()
    return str(x)


def write_up_associated_addresses(some_dict, address, isdone):
    if isdone:
        with open(files_path + f'results/{address}.txt', 'w') as file_to_write_addresses:
            for tx in some_dict:
                file_to_write_addresses.write(str(tx) + '\n')
    else:
        with open(files_path + f'results/{address}.txt', 'w') as file_to_write_addresses:
            file_to_write_addresses.write('У этого адреса недостаточно совершенных транзакций,'
                                          ' как для того что бы получить какую-то информацию =(')


def remove_gived_file(address):
    try:
        os.remove(files_path + f'results/{address}.txt')
    except:
        pass


def get_dict_from_file(user_id):
    try:
        with open(files_path + 'result_buttons/' + str(user_id) + '.txt', 'r') as file_to_read:
            all_data = ''
            for line in file_to_read:
                all_data += line
            if len(all_data) > 1:
                my_opened_dict = ast.literal_eval(all_data)
            else:
                my_opened_dict = dict()
        return my_opened_dict
    except:
        return dict()



def get_user_buttons(user_id, for_button='buttons'):

    temp_dict = deepcopy(get_dict_from_file(user_id))

    if for_button in temp_dict.keys():
        for buttons in temp_dict[for_button]:
            yield {
                'text': buttons['text'],
                'callback_data': buttons['callback_data']
            }


def remove_button(user_id, some_button_name, parent_button='buttons'):

    flag = False

    buttons_to_remove = []
    button_number_counter = -1

    temp_dict = deepcopy(get_dict_from_file(user_id))

    if parent_button in temp_dict.keys():
        for buttons in temp_dict[parent_button]:
            for keys, values in buttons.items():
                if keys == 'text':
                    button_number_counter += 1
                    if values == some_button_name:
                        buttons_to_remove.append(button_number_counter)


    if len(buttons_to_remove) > 0:
        for buttons_number in buttons_to_remove[::-1]:
            del temp_dict[parent_button][buttons_number]
            flag = True

    with open((files_path + 'result_buttons/' + str(user_id) + '.txt'), 'w') as file_to_save:
        file_to_save.write(str(temp_dict))

    return flag


def add_main_button(user_id, some_button):

    temp_dict = deepcopy(get_dict_from_file(user_id))

    if 'buttons' in temp_dict.keys():
        temp_dict['buttons'].append(some_button.values)
    if 'buttons' not in temp_dict.keys():
        temp_dict['buttons'] = [some_button.values]

    with open(str(files_path + 'result_buttons/' + str(user_id) + '.txt'), 'w') as file_to_save:
        file_to_save.write(str(temp_dict))


def remove_results_file(file_name):
    try:
        os.chdir(str(files_path + 'results/'))
        os.remove(str(file_name) + '.txt')
    except:
        pass