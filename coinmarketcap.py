import logging
from thefuzz import fuzz        #подключил модули из библиотеки->
from thefuzz import process     #->fuzzywuzzy для обработки неточных соответствий
import sqlite3                  #импорт библиотеки для работы с БД
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext       #импорт библиотек для машины состояний
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from coinmarketcap import coin_request
#список компаний для функции корректировки некорректного запроса пользователя
#в последующем можно забирать из базы данных или считывать из файла
company_list = ['Газпром', 'Сбербанк', 'Алроса', 'ТГК-1', 'Московская биржа']

#создал функцию запроса в базу данных
def query_db(user_query,info):
    conn = sqlite3.connect('msfo.db3')
    cur = conn.cursor()
    cur.execute(f'SELECT {info} FROM msfo WHERE name="{user_query}";')
    str = cur.fetchall()    # fetchall возвращает список кортежей [(),(),(),()]
    return str[0][0]        # поэтому получаем доступ к данным по индексу в списке и индексу в кортеже

# Объект бота
bot = Bot(token='2008374333:AAE-HcREZx4eCUHCtu5-2TFF77gVdO4f9gQ')
# Диспетчер для бота
#добавил хранилище в диспетчер
dp = Dispatcher(bot, storage = MemoryStorage())

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

class User_choise(StatesGroup):
    selection = State()
    waiting_for_msfo = State()
    waiting_for_crypto = State()
#отслеживание любых состояний для отмены из любого состояния FSM

# Функция на команду /start
@dp.message_handler(state='*', commands='Start')
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer("""Вас приветствует бот-помошник. Вы можете получить последний отчёт компании МСФО/РСБУ.
    \nТак же Вы можете узнать курс любой криптовалюты в текущий момент. Воспользуйтесь кнопками ниже.""")
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ['/Отчёт', "/Криптовалюта", '/start']
    keyboard.add(buttons[0]).add(buttons[1]).add(buttons[2])
    await state.finish()
    await message.answer('Что выбираете?', reply_markup=keyboard)

# Функция на команду /Отчёт
@dp.message_handler(state='*', commands='Отчёт')
async def cmd_msfo(message: types.Message, state: FSMContext):
    await message.answer('Введите название компании: ')
    await User_choise.waiting_for_msfo.set()

@dp.message_handler(state='*', commands='Криптовалюта')
async def cmd_crypt(message: types.Message, state: FSMContext):
    await message.answer('Введите название криптовалюты: ')
    await User_choise.waiting_for_crypto.set()


@dp.message_handler(content_types=['text'], state=User_choise.waiting_for_crypto)
async def cmd_crypt_answer(message: types.Message, state: FSMContext):
    await message.answer(coin_request(message.text))


#декоратор функция ожидающая пользовательский ввод на команду /Отчёт
@dp.message_handler(content_types=['text'], state=User_choise.waiting_for_msfo)
async def query_comp(message: types.Message, state: FSMContext):
# тут начинается корректировка неточного запроса пользователя
    company_name = process.extractOne(message.text, company_list)
#записываю в MemoryStorage переменную чтобы отправить в другой хэндлер
    async with state.proxy() as data:
        data['company_name'] = company_name[0]
# так как process.excractOne возвращает список, то получаем доступ к его значениям по индексам
    if company_name[1] >= 60:  #
        if company_name[1] < 99:
            markup_inline = types.InlineKeyboardMarkup()
            item_yes = types.InlineKeyboardButton(text='Да', callback_data='Yes')
            item_no = types.InlineKeyboardButton(text='Нет', callback_data='No')
            markup_inline.add(item_yes, item_no)
            await message.answer(f'Вы имели ввиду компанию {data["company_name"]}?', reply_markup=markup_inline)
        else:
            await response_data(message.answer)
    else:
        await message.answer('по вашему запросу нет информации')

#функция инлайновой клавиатуры с кнопками краткий отчёт и полный отчёт
async def response_data(user_msg):
    markup_inline = types.InlineKeyboardMarkup()
    item_short = types.InlineKeyboardButton(text='Краткий', callback_data='short')
    item_long = types.InlineKeyboardButton(text='Полный', callback_data='long')
    markup_inline.add(item_short, item_long)
    await user_msg('Какой отчёт нужен краткий или полный?', reply_markup=markup_inline)

# функция обработчик callback данных пользовательского выбора
@dp.callback_query_handler(text=['Yes','No','short','long'], state=User_choise.waiting_for_msfo)
async def callback_inline_menu(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'Yes':
        # если выбор "Да" то запускается функция с кнопками "краткий" и "полный"
        await bot.delete_message(call.from_user.id, call.message.message_id)  # удаляем кнопки после использования
        await response_data(call.message.answer)
    elif call.data == 'No':
        await bot.delete_message(call.from_user.id, call.message.message_id)
        await call.message.answer('Попробуйте ещё раз')
    elif call.data == 'short':
        result = await state.get_data()     #получаю переменную из state memory storage
        await call.message.answer(query_db(result['company_name'], 'short_info'))  # выдается краткий отчёт
    elif call.data == 'long':
        result = await state.get_data()     #получаю переменную из state memory storage
        await call.message.answer(query_db(result['company_name'], 'long_info'))  # выдается полный отчёт



""""#сохранение фото на компьютер
@dp.message_handler(content_types=['photo'])
async def download_photo(message: types.Message):
    await message.photo[-1].download(destination_dir='Photo')"""
dp.register_message_handler(cmd_start, commands='Start', state='*')



# Запуск бота
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
