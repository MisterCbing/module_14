from imports import *
from crud_functions import *
from crud_functions1 import *

connection = sqlite3.connect("products.db")
cursor = connection.cursor()

dp = Dispatcher(storage=MemoryStorage())
button1 = KeyboardButton(text='Рассчитать')
button2 = KeyboardButton(text='Информация')
button3 = KeyboardButton(text='Купить')
button4 = KeyboardButton(text ='Регистрация')
kb = ReplyKeyboardMarkup(keyboard=[[button1, button2, button3, button4]], resize_keyboard=True)

ibutton1 = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
ibutton2 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
ikb = InlineKeyboardMarkup(inline_keyboard=[[ibutton1, ibutton2]])

product_list = get_all_products()
ib = []

for product in product_list:
    ib.append(InlineKeyboardButton(text=product[1], callback_data='product_buying'))

ikb_farm = InlineKeyboardMarkup(inline_keyboard=[ib])


class UserState(StatesGroup):
    age = State()
    height = State()
    weight = State()
    sex = State()


class RegistrationState(StatesGroup):
    username = State()
    age = State()
    email = State()


@dp.message(CommandStart())
async def command_start_handler(message: Message):
    await message.answer(f"Привет! Я бот, помогающий твоему здоровью.")
    await message.answer('Нажми кнопку "Рассчитать", чтобы узнать свою дневную норму калорий', reply_markup=kb)


@dp.message(F.text == 'Регистрация')
async def sign_up(message: Message, state: FSMContext):
    await message.answer("Введите имя пользователя (только латинский алфавит):",
                                  reply_markup=ReplyKeyboardRemove())
    await state.set_state(RegistrationState.username)


@dp.message(F.text, RegistrationState.username)
async def set_username(message: Message, state: FSMContext):
    temp = message.text
    if is_included(temp):
        await message.answer('Пользователь существует, введите другое имя.')
        await state.set_state(RegistrationState.username)
    else:
        await state.update_data(username=temp)
        await message.answer("Введите свой email:")
        await state.set_state(RegistrationState.email)


@dp.message(F.text, RegistrationState.email)
async def set_email(message: Message, state: FSMContext):
    await state.update_data(email=message.text)
    await message.answer("Введите свой возраст:")
    await state.set_state(RegistrationState.age)


@dp.message(F.text, RegistrationState.age)
async def set_age(message: Message, state: FSMContext):
    await state.update_data(age=int(message.text))
    data = await state.get_data()
    add_user(data['username'], data['email'], data['age'])
    await message.answer("Регистрация прошла успешно!")
    await state.clear()


@dp.message(F.text.lower().contains('рассчитать'))
async def main_menu(message: Message):
    await message.answer('Выберите опцию:', reply_markup=ikb)


@dp.message(F.text == 'Купить')
async def get_buying_list(message: Message):
    for product in product_list:
        await message.answer(f'Название: {product[1]} | Описание: {product[2]} | Цена: {product[3]}')
        await message.answer_photo(FSInputFile(f'vit{product[0]}.jpg'))
    await message.answer('Выберите продукт для покупки:', reply_markup=ikb_farm)


@dp.callback_query(F.data == 'product_buying')
async def formula(callback: CallbackQuery):
    await callback.message.answer('Вы успешно приобрели продукт!')


@dp.callback_query(F.data.lower() == 'formulas')
async def formula(callback: CallbackQuery):
    await callback.message.answer('для мужчин: 10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5;\n'
                                  'для женщин: 10 x вес (кг) + 6,25 x рост (см) – 5 x возраст (г) – 161.')


@dp.callback_query(F.data.lower() == 'calories')
async def set_age(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Поехали!", reply_markup=ReplyKeyboardRemove())
    await callback.message.answer("Введите свой возраст:")
    await state.set_state(UserState.age)


@dp.message(F.text, UserState.age)
async def set_height(message: Message, state: FSMContext):
    await state.update_data(age=int(message.text))
    await message.answer("Введите свой рост:")
    await state.set_state(UserState.height)


@dp.message(F.text, UserState.height)
async def set_weight(message: Message, state: FSMContext):
    await state.update_data(height=int(message.text))
    await message.answer("Введите свой вес:")
    await state.set_state(UserState.weight)


@dp.message(F.text, UserState.weight)
async def set_sex(message: Message, state: FSMContext):
    await state.update_data(weight=int(message.text))
    await message.answer("Введите свой пол (0 - женщина, 1 - мужчина):")
    await state.set_state(UserState.sex)


@dp.message(F.text, UserState.sex)
async def send_calories(message: Message, state: FSMContext):
    await state.update_data(sex=int(message.text))
    data = await state.get_data()
    norm = data['weight'] * 10 + data['height'] * 6.25 - data['age'] * 5 + [-161, 5][data['sex']]
    await message.answer(f"Ваша норма калорий: {norm}")
    await state.clear()


@dp.message(F.text.lower() == 'информация')
async def info(message: Message):
    await message.answer('Это бот, который умеет рассчитывать дневную норму калорий в зависимости от возраста, '
                         'роста, веса и пола человека')


@dp.message(or_f(F.text.lower() == 'стоп', F.text.lower() == 'stop'))
async def stop(message: Message):
    await dp.stop_polling()


@dp.message()
async def default_answer(message: Message):
    await message.answer('Введите команду /start, чтобы начать общение.')


async def main():
    bot = Bot(token=TOKEN,
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
