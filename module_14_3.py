from imports import *

dp = Dispatcher(storage=MemoryStorage())
button1 = KeyboardButton(text='Рассчитать')
button2 = KeyboardButton(text='Информация')
button3 = KeyboardButton(text='Купить')
kb = ReplyKeyboardMarkup(keyboard=[[button1, button2, button3]], resize_keyboard=True)

ibutton1 = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
ibutton2 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
ikb = InlineKeyboardMarkup(inline_keyboard=[[ibutton1, ibutton2]])

farm = ['', 'ПАПАЗОЛ', 'ВЫПИВОН', 'ЗАГРУСТИН', 'БЫЛЗОЛ']

ib1 = InlineKeyboardButton(text=farm[1], callback_data='product_buying')
ib2 = InlineKeyboardButton(text=farm[2], callback_data='product_buying')
ib3 = InlineKeyboardButton(text=farm[3], callback_data='product_buying')
ib4 = InlineKeyboardButton(text=farm[4], callback_data='product_buying')
ikb_farm = InlineKeyboardMarkup(inline_keyboard=[[ib1, ib2, ib3, ib4]])



class UserState(StatesGroup):
    age = State()
    height = State()
    weight = State()
    sex = State()


@dp.message(CommandStart())
async def command_start_handler(message: Message):
    await message.answer(f"Привет, {html.bold(message.from_user.full_name)}! Я бот, помогающий твоему здоровью.")
    await message.answer('Нажми кнопку "Рассчитать", чтобы узнать свою дневную норму калорий', reply_markup=kb)


@dp.message(F.text.lower().contains('рассчитать'))
async def main_menu(message: Message):
    await message.answer('Выберите опцию:', reply_markup=ikb)


@dp.message(F.text == 'Купить')
async def get_buying_list(message: Message):
    for i in range(1,5):
        await message.answer(f'Название: {farm[i]} | Описание: описание{i} | Цена: {i}00')
        await message.answer_photo(FSInputFile(f'vit{i}.jpg'))
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
