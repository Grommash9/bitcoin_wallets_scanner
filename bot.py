import logging

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils import executor
import work_with_files
import sochain

button_collection = {
    'Проверить один адрес': InlineKeyboardButton(text='Проверить биткоин адрес', callback_data='check_solo'),
    'О боте': InlineKeyboardButton(text='О боте', callback_data='about'),
    'Исходники': InlineKeyboardButton(text='Исходники', callback_data='source_files')
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
bot = Bot(token='ты че думал я его тут оставлю?)')
dp = Dispatcher(bot, storage=memory_storage)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    work_with_files.add_new_user(message.from_user)
    await bot.send_message(chat_id=message.from_user.id,
                           text='Добро пожаловать, надеюсь я помогу вам добыть какую-то информацию =)',
                           reply_markup=all_buttons_from_collection_keyboard, parse_mode="Markdown")


@dp.callback_query_handler(lambda c: c.data.startswith('about'))
async def handle_a(callback_query: types.CallbackQuery):
    await bot.send_message(chat_id=callback_query.from_user.id,
                           text=f'Ботом уже воспользовались *{work_with_files.get_users_count()} человек* и'
                                f' *запросили поиск данных {work_with_files.get_total_search_count()} раз.*\n\n'
                                f'Создатель бота - @vatot5, если вам нужно написать какой либо '
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
                           reply_markup=all_buttons_from_collection_keyboard, parse_mode="Markdown")
    await bot.answer_callback_query(callback_query_id=callback_query.id)


@dp.message_handler()
async def any_message_answer(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id,
                           text='Я не знаю что ответить на это, вот менюшка',
                           reply_markup=all_buttons_from_collection_keyboard, parse_mode="Markdown")


@dp.callback_query_handler(lambda c: c.data.startswith('check_'))
async def handle_address_check(callback_query: types.CallbackQuery):
    await bot.send_message(chat_id=callback_query.from_user.id,
                           text="Введите биткоин адрес, "
                                "что бы получить все адреса на которые отправлялись неизрасходовынные средства,:\n\n'"
                                "_Для отмены отправьте 1 любой символ_", parse_mode="Markdown")
    await InputUserData.step_1.set()
    await bot.answer_callback_query(callback_query.id)


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
                                   text=f'Адрес верный, если есть исходящии транзакции то скоро скину файл с адресами,'
                                        f' ожидайте и не тыкайте ничего =)')

            deep_shit = sochain.deeper_anal(address)

            if len(deep_shit) != 0:

                work_with_files.clean_up_associated_addresses()
                work_with_files.write_up_associated_addresses(deep_shit)

                await bot.send_document(message.from_user.id, open(r'C:/Users/Гриша/PycharmProjects/bitcoin_wallets_scanner/associated_addresses.txt', 'rb'))

                await bot.send_message(chat_id=message.from_user.id,
                                       text=f'Надеюсь вы найдете то, что ищете, хорошего дня =)',
                                       reply_markup=all_buttons_from_collection_keyboard)

            else:
                await bot.send_message(chat_id=message.from_user.id,
                                       text=f'С этого адреса ещё не было отправлено транзакций или они на данный'
                                            f' момент не подтвержены, невозможно найти связанные кошельки =(',
                                       reply_markup=all_buttons_from_collection_keyboard)

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
