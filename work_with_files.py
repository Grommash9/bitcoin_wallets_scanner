import bot


def add_new_user(user_info):

    is_user_new = True
    with open('users_list.txt', 'r') as users_list_file_to_read:
        current_user = str(user_info) + '\n'
        for line in users_list_file_to_read:
            if line == current_user:
                is_user_new = False
    if is_user_new:
        with open('users_list.txt', 'a') as users_list_file_add_line:
            users_list_file_add_line.write(str(user_info) + '\n')
        with open('total_users_count.txt', 'r') as user_count_to_read:
            x = user_count_to_read.readline()
        with open('total_users_count.txt', 'w') as user_count_to_write:
            new_q = int(x) + 1
            user_count_to_write.write(str(new_q))


def add_search_attempt():
    with open('total_search_count.txt', 'r') as total_attempts_file:
        x = total_attempts_file.readline()
    new_q = int(x) + 1
    with open('total_search_count.txt', 'w') as total_attempts_file_to_write:
        total_attempts_file_to_write.write(str(new_q))


def get_users_count():
    with open('total_users_count.txt', 'r') as users_count_file:
        x = users_count_file.readline()
    return str(x)


def get_total_search_count():
    with open('total_search_count.txt', 'r') as search_count_file:
        x = search_count_file.readline()
    return str(x)


def clean_up_associated_addresses():
    with open('associated_addresses.txt', 'w') as file_to_clean:
        file_to_clean.write('')


def write_up_associated_addresses(some_dict):
    with open('associated_addresses.txt', 'a') as file_to_write_addresses:
        for keys in some_dict.keys():
            file_to_write_addresses.write(str(keys) + '\n')

