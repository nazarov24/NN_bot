import telebot
from telebot import types
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from database import get_user_data, save_user, get_saved_addresses, save_address

TOKEN = '8189225431:AAG9nJf_uZGwuWH5GwQCj0LZgwzKuYHP6qc'
MAIN_CHANNEL_ID = '-1002333885798'
DUSHANBE_CHANNEL_ID = '-1002606426389'
bot = telebot.TeleBot(TOKEN)

users = {}

commands = [
    types.BotCommand("start", "Запустить бота"),
]

def get_city_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    cities = ['Душанбе', 'Худжанд', 'Гафуров', 'Бустон (Чкаловск)']
    for city in cities:
        keyboard.add(KeyboardButton(city))
    return keyboard

def get_address_keyboard(chat_id):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    addresses = get_saved_addresses(chat_id)
    for address in addresses:
        keyboard.add(KeyboardButton(address))
    keyboard.add(KeyboardButton("🆕 Ввести новый адрес"))
    return keyboard

def get_start_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Оформить заказ", callback_data="start_order"))
    keyboard.add(InlineKeyboardButton("📞 Контакты", callback_data="contact_info"))
    return keyboard

def get_inline_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Опубликовать", callback_data="publish_order"))
    return keyboard

@bot.message_handler(commands=['start'])
def start(message):
    phone, _ = get_user_data(message.chat.id)

    if phone:
        bot.send_message(message.chat.id, "Вы уже зарегистрированы! Можете сразу оформить заявку.", reply_markup=get_start_keyboard())
    else:
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(KeyboardButton("📱 Отправить номер телефона", request_contact=True))
        bot.send_message(message.chat.id, "Отправьте ваш номер телефона для регистрации:", reply_markup=keyboard)

@bot.message_handler(content_types=['contact'])
def register_user(message):
    if message.contact is not None:
        save_user(message.chat.id, message.contact.phone_number)
        users[message.chat.id] = {}
        bot.send_message(message.chat.id, "Спасибо за регистрацию! Теперь выберите ваш город.", reply_markup=get_city_keyboard())

@bot.callback_query_handler(func=lambda call: call.data == "start_order")
def start_order(call):
    phone, _ = get_user_data(call.message.chat.id)
    
    if not phone:
        bot.send_message(call.message.chat.id, "Сначала зарегистрируйтесь, отправив номер телефона.", reply_markup=get_start_keyboard())
        return
    
    users[call.message.chat.id] = {}  # Сбрасываем информацию о пользователе перед новым заказом
    
    bot.send_message(call.message.chat.id, "Выберите ваш город:", reply_markup=get_city_keyboard())
    bot.register_next_step_handler(call.message, set_city)

@bot.message_handler(func=lambda message: message.text in ['Душанбе', 'Худжанд', 'Гафуров', 'Бустон (Чкаловск)'])
def set_city(message):
    users[message.chat.id] = {'city': message.text}
    bot.send_message(message.chat.id, 'Введите ваш магазин:')
    bot.register_next_step_handler(message, get_shop_name)

def get_shop_name(message):
    users[message.chat.id]['shop'] = message.text
    bot.send_message(message.chat.id, 'Выберите ваш адрес или введите новый:', reply_markup=get_address_keyboard(message.chat.id))
    bot.register_next_step_handler(message, get_address)

def get_address(message):
    if message.text == "🆕 Ввести новый адрес":
        bot.send_message(message.chat.id, 'Введите новый адрес:')
        bot.register_next_step_handler(message, save_new_address)
    else:
        finalize_order(message.chat.id, message.text)

def save_new_address(message):
    save_address(message.chat.id, message.text)
    finalize_order(message.chat.id, message.text)

def finalize_order(chat_id, address):
    user_data = users.get(chat_id, {})
    phone, _ = get_user_data(chat_id)
    
    request_text = (f"\U0001F4CC Новая заявка!\n\n"
                    f"\U0001F4DE Номер: {phone}\n"
                    f"\U0001F3D9 Город: {user_data['city']}\n"
                    f"\U0001F3EC Магазин: {user_data['shop']}\n"
                    f"\U0001F4E6 Адрес: {address}")
    
    users[chat_id]['address'] = address
    bot.send_message(chat_id, request_text, reply_markup=get_inline_keyboard())

@bot.callback_query_handler(func=lambda call: call.data == "publish_order")
def publish_order(call):
    user_data = users.get(call.message.chat.id, {})
    phone, _ = get_user_data(call.message.chat.id)
    
    request_text = (f"\U0001F4CC Новая заявка!\n\n"
                    f"\U0001F4DE Номер: {phone}\n"
                    f"\U0001F3D9 Город: {user_data.get('city')}\n"
                    f"\U0001F3EC Магазин: {user_data.get('shop')}\n"
                    f"\U0001F4E6 Адрес: {user_data.get('address')}")
    
    target_channel = DUSHANBE_CHANNEL_ID if user_data.get('city') == "Душанбе" else MAIN_CHANNEL_ID
    bot.send_message(target_channel, request_text)
    
    # ✅ Оповещение пользователя
    bot.send_message(call.message.chat.id, 
                     "Ваша заявка принята! ✅\n"
                     "Ожидайте, курьер скоро заберёт вашу посылку.\n\n"
                     "📞 Если есть дополнительные вопросы, звоните или напишите нашему оператору:\n"
                     "+992006774000", 
                     reply_markup=get_start_keyboard())

@bot.callback_query_handler(func=lambda call: call.data == "contact_info")
def send_contact_info(call):
    contact_text = "📞 Служба поддержки\n+992006774000\n\n📸 Instagram: @speed_de1ivery"
    instagram_link = "https://www.instagram.com/speed_de1ivery"
    bot.send_message(call.message.chat.id, contact_text)
    bot.send_message(call.message.chat.id, f"🔗 {instagram_link}")

bot.polling(none_stop=True)
