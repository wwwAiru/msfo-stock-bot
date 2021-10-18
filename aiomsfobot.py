
import logging
from thefuzz import fuzz        #подключил модули из библиотеки->
from thefuzz import process     #->fuzzywuzzy для обработки неточных соответствий
import sqlite3                  #импорт библиотеки для работы с БД
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext       #импорт библиотек для машины состояний
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup

#список компаний для функции корректировки некорректного запроса пользователя
#в последующем можно забирать из базы данных или считывать из файла
company_list = ['Газпром', 'Сбербанк', 'Алроса', 'ТГК-1', 'Московская биржа']


# Объект бота
bot = Bot(token="")
# Диспетчер для бота
#добавил хранилище в диспетчер
dp = Dispatcher(bot, storage = MemoryStorage())
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

#создал функцию запроса в базу данных
def query_db(user_query,info):
    conn = sqlite3.connect('msfo.db3')
    cur = conn.cursor()
    cur.execute(f'SELECT {info} FROM msfo WHERE name="{user_query}"')
    str = cur.fetchall()    # fetchall возвращает список кортежей [(),(),(),()]
    return str[0][0]        # поэтому получаем доступ к данным по индексу в списке и индексу в кортеже

# Хэндлер на команду /start
@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    await message.answer("Вас приветствует бот-помошник. Вы пожете получить последний отчёт компании МСФО/РСБУ.\nВведите название компании :")

#функция инлайновой клавиатуры с кнопками краткий отчёт и полный отчёт
async def response_data(param):
    markup_inline = types.InlineKeyboardMarkup()
    item_short = types.InlineKeyboardButton(text='Краткий', callback_data='short')
    item_long = types.InlineKeyboardButton(text='Полный', callback_data='long')
    markup_inline.add(item_short, item_long)
    await param('Какой отчёт нужен краткий или полный?', reply_markup=markup_inline)
#декоратор функция ожидающая пользовательский ввод
@dp.message_handler(content_types=["text"])
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
        await message.answer("по вашему запросу нет информации")
# функция обработчик callback данных пользовательского выбора
@dp.callback_query_handler(text= ["Yes","No","short","long"])
async def callback_inline_menu(call: types.CallbackQuery, state: FSMContext):
    if call.data == "Yes":  # если выбор "Да" то запускается функция со второй клавиатурой
        await bot.delete_message(call.from_user.id, call.message.message_id)  # удаляем кнопки после использования
        await response_data(call.message.answer)
    elif call.data == "No":
        await bot.delete_message(call.from_user.id, call.message.message_id)
        await call.message.answer("Попробуйте ещё раз")
    elif call.data == "short":
        result = await state.get_data()     #получаю переменную из state memory storage
        await call.message.answer(query_db(result['company_name'], "short_info"))  # выдается краткий отчёт
    elif call.data == "long":
        result = await state.get_data()     #получаю переменную из state memory storage
        await call.message.answer(query_db(result['company_name'], "long_info"))  # выдается полный отчёт


#сохранение фото на компьютер
@dp.message_handler(content_types=["photo"])
async def download_photo(message: types.Message):
    await message.photo[-1].download(destination_dir='Photo')

# Запуск бота
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
