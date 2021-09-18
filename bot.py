import logging
import logging
import threading
import time
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils import executor
import work_with_files
import sochain

files_path = '/home/wallets_scanner_bot/'
#files_path = 'C:/Users/Гриша/PycharmProjects/bitcoin_wallets_scanner/'

button_collection = {
    'Проверить один адрес': InlineKeyboardButton(text='Проверить биткоин адрес', callback_data='check_solo'),
    'О боте': InlineKeyboardButton(text='О боте', callback_data='about'),
    'Исходники': InlineKeyboardButton(text='Исходники', callback_data='source_files'),
    'Статус проверки': InlineKeyboardButton(text='Статус проверки', callback_data='get_status')
}

all_buttons_from_collection_keyboard = InlineKeyboardMarkup()
for values in button_collection.values():
    all_buttons_from_collection_keyboard.add(values)


class InputUserData(StatesGroup):
    step_1 = State()
    step_2 = State()
    step_3 = State()


logging.basicConfig(level=logging.INFO)
memory_storage = MemoryStorage()
bot = Bot(token='1976564059:AAF8JV2xhV5_eOZUsjR653gu01-L-8KBYwY')
dp = Dispatcher(bot, storage=memory_storage)

order_status_dict = dict()


def main_thread_function(address, target_user_id):

    start_time = time.time()

    try:
        order_status_dict[target_user_id] = {address: '\n\nПоиск кошельков пользователя - *process*'}
        all_user_wallets = ['Список кошельков пользователя найденных по факту участия в одной транзакции '
                            '(точно принадлежат одному человеку): \n\n']
        all_user_wallets += sochain.find_all_user_wallets(address)
        order_status_dict[target_user_id] = {address: '\n\nПоиск кошельков - *ok*\n'
                                                      'Кто отправлял пользователю деньги - *process*'}
        senders_to_user = ['\n\nСписок кошельков которые учавствовали в транзакциях, которые пополниляли счет '
                           'пользователя(за исключением погрешностей - те кто платил пользователю): \n\n']
        senders_to_user += sochain.who_send_money_to_user(all_user_wallets)
        order_status_dict[target_user_id] = {address: '\n\nПоиск кошельков - *ok*\n'
                                                      'Кто отправлял пользователю деньги - *ok*\nКому отправлял пользователь - *process*'}
        recipients_from_user = [
            '\n\nСписок кошельков которые учавствовали в транзакции, когда пользователь отправлял деньги '
            '(за исключением погрешностей - те кому пользовтель платил): \n\n']
        recipients_from_user += sochain.sending_money_by_user(all_user_wallets)
        timing = [f'\n\nПодготовка документа заняла {(time.time() - start_time) / 60} минут']
        deep_shit = all_user_wallets + senders_to_user + recipients_from_user + timing
        order_status_dict[target_user_id][address] = 'Все данные получены идет запись в файл'
        if len(deep_shit) != 1:
            work_with_files.write_up_associated_addresses(deep_shit, address, True)
        else:
            work_with_files.write_up_associated_addresses(deep_shit, address, False)
    except:
        order_status_dict[target_user_id][address] = 'failed'
    else:
        order_status_dict[target_user_id][address] = 'done'


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    work_with_files.add_new_user(message.from_user)
    await bot.send_message(chat_id=message.from_user.id,
                           text='Добро пожаловать, надеюсь я помогу вам добыть какую-то информацию',
                           reply_markup=all_buttons_from_collection_keyboard, parse_mode="Markdown")


@dp.callback_query_handler(lambda c: c.data.startswith('main_page'))
async def handle_a(callback_query: types.CallbackQuery):
    await bot.send_message(chat_id=callback_query.from_user.id,
                           text='Вы в главном меню, выберите желаемый пункт: ',
                           reply_markup=all_buttons_from_collection_keyboard, parse_mode="Markdown")
    await bot.answer_callback_query(callback_query_id=callback_query.id)


@dp.callback_query_handler(lambda c: c.data.startswith('about'))
async def handle_a(callback_query: types.CallbackQuery):
    await bot.send_message(chat_id=callback_query.from_user.id,
                           text=f'Ботом уже воспользовались *{work_with_files.get_users_count()} человек* и'
                                f' *запросили поиск данных {work_with_files.get_total_search_count()} раз.*\n\n'
                                f'Создатель бота - @grommash9, если вам нужно написать какой либо '
                                f'телеграм бот или услуги программиста в целом, пишите, буду рад поработать с вами \n\n'
                                f'Бот стоит на сервере который необходимо ежемесячно оплачивать,'
                                f' поэтому я с радостью приму добровольные пожертвования\n\n'
                                f'*bitcoin*: _bc1qld7c86vpcssxashzu5hfguegkegae393p4w8fj_\n'
                                f'*ETH*: _0xa6217937E58Ff3828e377d8BFAe5585D930DD445_\n'
                                f'*bnb*: _bnb1hl8dhj7ty0qg3ls72uknj27hnwe877phdzluxy_\n',
                           reply_markup=all_buttons_from_collection_keyboard, parse_mode="Markdown")
    await bot.answer_callback_query(callback_query_id=callback_query.id)


@dp.callback_query_handler(lambda c: c.data.startswith('source_files'))
async def handle_a(callback_query: types.CallbackQuery):
    await bot.send_message(chat_id=callback_query.from_user.id,
                           text=f'Вот ссылка на исходники этого бота, если вы программист,'
                                f' то не судите очень строго, это моя третья разработка =)\n\n'
                                f'https://github.com/Grommash9/bitcoin_wallets_scanner',
                           reply_markup=all_buttons_from_collection_keyboard)
    await bot.answer_callback_query(callback_query_id=callback_query.id)


@dp.callback_query_handler(lambda c: c.data.startswith('get_status'))
async def handle_a(callback_query: types.CallbackQuery):
    addresses_to_remove_from_order_dict_list = []
    temp_keyboard_collection = InlineKeyboardMarkup()
    if callback_query.from_user.id in order_status_dict.keys():
        message_to_send = ''
        for users_id in order_status_dict.keys():
            if users_id == callback_query.from_user.id:
                for addresses, status in order_status_dict[users_id].items():
                    if status == 'done':
                        new_button = InlineKeyboardButton(text=addresses, callback_data=f'give_{addresses}')
                        work_with_files.add_main_button(callback_query.from_user.id, new_button)
                        addresses_to_remove_from_order_dict_list.append(addresses)
                        order_status_dict[users_id][addresses] = 'Забирайте'
                        message_to_send += f'Проверка адреса *{addresses}* успешно завершена,' \
                                           f' вы можете забрать результаты нажав на кнопку ниже'
                    elif status == 'failed':
                        message_to_send += f'Проверка адреса *{addresses}* завершилась с ошибкой,' \
                                           f' пожалуйста попробуйте снова, если ошибка повториться - свяжитесь' \
                                           f' с разработчиком'
                    else:
                        message_to_send += f'Текущий статус проверки адреса *{addresses}* - {status}'

        if message_to_send == '':
            message_to_send = 'У вас нет результатов для скачивания, пожалуйста инициализируйте новый поиск'
        for custom_buttons in work_with_files.get_user_buttons(user_id=callback_query.from_user.id):
            temp_keyboard_collection.add(custom_buttons)
        temp_keyboard_collection.add(InlineKeyboardButton(text='Главная', callback_data='main_page'))
        await bot.send_message(chat_id=callback_query.from_user.id,
                               text=message_to_send,
                               reply_markup=temp_keyboard_collection, parse_mode="Markdown")
        await bot.answer_callback_query(callback_query_id=callback_query.id)
    else:
        temp_keyboard_collection.add(InlineKeyboardButton(text='Главная', callback_data='main_page'))
        await bot.send_message(chat_id=callback_query.from_user.id,
                               text=f'У вас нет результатов для скачивания, пожалуйста инициализируйте новый поиск',
                               reply_markup=all_buttons_from_collection_keyboard)
        await bot.answer_callback_query(callback_query_id=callback_query.id)


@dp.callback_query_handler(lambda c: c.data.startswith('give_'))
async def handle_a(callback_query: types.CallbackQuery):
    target_file = callback_query.data[5:]
    try:
        await bot.send_document(callback_query.from_user.id, open(files_path + f'results/{target_file}.txt', 'rb'))
        del order_status_dict[callback_query.from_user.id]
        work_with_files.remove_button(callback_query.from_user.id, some_button_name=target_file)
        work_with_files.remove_results_file(target_file)
        await bot.answer_callback_query(callback_query.id)
    except:
        await bot.send_message(callback_query.from_user.id, text='Файл утерян, запросите поиск снова')


@dp.message_handler()
async def any_message_answer(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id,
                           text='Я не знаю что ответить на это, вот менюшка',
                           reply_markup=all_buttons_from_collection_keyboard, parse_mode="Markdown")


@dp.callback_query_handler(lambda c: c.data.startswith('check_'))
async def handle_address_check(callback_query: types.CallbackQuery):
    if not callback_query.from_user.id in order_status_dict.keys():
        isundone = False
        for users_id, orders in order_status_dict.items():
            for address, status in order_status_dict[users_id].items():
                if status != 'done':
                    isundone = True

        if isundone:
            new_markup = InlineKeyboardMarkup()
            new_markup.add(button_collection['Статус проверки'])
            await bot.send_message(chat_id=callback_query.from_user.id,
                                   text="Кто-то сейчас проверяет адрес, к сожаланию пока что бот "
                                        "может обрабатывать только один заказ за раз, пожалуйста ожидайте,"
                                        "извините за неудобства",
                                   reply_markup=all_buttons_from_collection_keyboard,
                                   parse_mode="Markdown")
            await bot.answer_callback_query(callback_query.id)
        else:
            await bot.send_message(chat_id=callback_query.from_user.id,
                                   text="Введите биткоин адрес, "
                                        "что бы получить все адреса на которые отправлялись "
                                        "неизрасходовынные средства:\n\n"
                                        "_Для отмены отправьте 1 любой символ_", parse_mode="Markdown")
            await InputUserData.step_1.set()
            await bot.answer_callback_query(callback_query.id)
    else:
        new_markup = InlineKeyboardMarkup()
        new_markup.add(button_collection['Статус проверки'])
        await bot.send_message(chat_id=callback_query.from_user.id,
                               text="На данный момент вы уже заказали проверку адреса,"
                                    " пожалуйста заберите результат в меню Проверки статуса,"
                                    " на данный момент бот позволяет проверять только"
                                    " по одному адресу за раз, извините за неудобства",
                               reply_markup=all_buttons_from_collection_keyboard,
                               parse_mode="Markdown")


@dp.message_handler(state=InputUserData.step_1, content_types=types.ContentTypes.TEXT)
async def questionnaire_state_1_message(message: types.Message, state: FSMContext):
    async with state.proxy() as user_data:
        user_data['input_user'] = message.text.replace('\n',
                                                       ' ')
        await state.finish()

    if len(user_data['input_user']) != 1:
        if user_data['input_user'].endswith(' '):
            target_wallet = str(user_data['input_user'])[:-1]
        else:
            target_wallet = user_data['input_user']
        address_valid, address = sochain.check_address_valid(target_wallet)
        if address_valid:

            work_with_files.add_search_attempt()

            await bot.send_message(chat_id=message.from_user.id,
                                   text=f"Адрес валидный и был принят в обработку,"
                                        f"проверить статус можно нажав на соответствующую кнопку",
                                   reply_markup=all_buttons_from_collection_keyboard,
                                   parse_mode="Markdown")
            x = threading.Thread(target=main_thread_function, args=[target_wallet, message.from_user.id])
            x.start()

        else:
            await bot.send_message(chat_id=message.from_user.id, text='В отправленном вами сообщении не найдено'
                                                                      ' действительных биткоин '
                                                                      'адресов или api sochain.com не отвечает,'
                                                                      ' попробуйте снова',
                                   reply_markup=all_buttons_from_collection_keyboard)
    else:
        await bot.send_message(chat_id=message.from_user.id,
                               text='Вы отменили ввод кошелька, можете выбрать другое действие: ',
                               parse_mode="Markdown", reply_markup=all_buttons_from_collection_keyboard)


if __name__ == '__main__':
    executor.start_polling(dp)
