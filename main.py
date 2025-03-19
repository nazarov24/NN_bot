import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove

TOKEN = '8189225431:AAG9nJf_uZGwuWH5GwQCj0LZgwzKuYHP6qc'
MAIN_CHANNEL_ID = '-1002333885798'
DUSHANBE_CHANNEL_ID = '-1002606426389'
bot = telebot.TeleBot(TOKEN)

users = {}

def get_start_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Оставить заявку"))
    keyboard.add(KeyboardButton("📞 Контакты"))  # Добавляем кнопку Контакты
    return keyboard

def get_inline_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Опубликовать", callback_data="publish_order"))
    return keyboard

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Добро пожаловать! Нажмите кнопку ниже, чтобы оставить заявку.", reply_markup=get_start_keyboard())

@bot.message_handler(func=lambda message: message.text == "📞 Контакты")
def send_contacts(message):
    contact_text = "📞 Служба поддержки\n+992006774000\n\n📸 Instagram: @speed_de1ivery"
    instagram_link = "https://www.instagram.com/speed_de1ivery"
    bot.send_message(message.chat.id, contact_text)
    bot.send_message(message.chat.id, f"🔗 {instagram_link}")

@bot.message_handler(func=lambda message: message.text == "Оставить заявку")
def start_application(message):
    users[message.chat.id] = {}
    bot.send_message(message.chat.id, 'Введите ваш номер телефона:')
    bot.register_next_step_handler(message, get_phone)

def get_phone(message):
    users[message.chat.id]['phone'] = message.text
    cities = ['Душанбе', 'Худжанд', 'Гафуров', 'Бустон (Чкаловск)']
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    
    if 'city' in users[message.chat.id]:
        keyboard.add(KeyboardButton(users[message.chat.id]['city']))
    else:
        for city in cities:
            keyboard.add(KeyboardButton(city))
    
    bot.send_message(message.chat.id, 'Выберите ваш город:', reply_markup=keyboard)
    bot.register_next_step_handler(message, get_city)

def get_city(message):
    selected_city = message.text.strip()
    
    if selected_city not in ['Душанбе', 'Худжанд', 'Гафуров', 'Бустон (Чкаловск)']:
        bot.send_message(message.chat.id, 'Пожалуйста, выберите корректный город из предложенных.')
        bot.register_next_step_handler(message, get_city)
        return
    
    users[message.chat.id]['city'] = selected_city
    bot.send_message(message.chat.id, f'Вы выбрали город: {selected_city}', reply_markup=ReplyKeyboardRemove())  
    bot.send_message(message.chat.id, 'Введите ваш магазин:', reply_markup=ReplyKeyboardMarkup(resize_keyboard=True)) 
    bot.register_next_step_handler(message, get_shop_name)

def get_shop_name(message):
    users[message.chat.id]['shop'] = message.text
    bot.send_message(message.chat.id, 'Введите ваш адрес для получения товара:')
    bot.register_next_step_handler(message, get_address)

def get_address(message):
    users[message.chat.id]['address'] = message.text
    bot.send_message(message.chat.id, 'Если у вас есть комментарии к заявке, напишите их сейчас.')
    bot.register_next_step_handler(message, get_comment)

def get_comment(message):
    comment = message.text.strip()
    users[message.chat.id]['comment'] = comment  
    user_data = users.get(message.chat.id, {})
    request_text = (f"📌 Ваша заявка!\n\n"
                    f"📞 Номер: {user_data.get('phone')}\n"
                    f"📍 Город: {user_data.get('city')}\n"
                    f"🏪 Магазин: {user_data.get('shop')}\n"
                    f"📦 Адрес: {user_data.get('address')}\n"
                    f"📝 Комментарий: {user_data.get('comment', 'Нет комментариев')}")
    
    bot.send_message(message.chat.id, request_text, reply_markup=get_inline_keyboard())

@bot.callback_query_handler(func=lambda call: call.data == "publish_order")
def publish_order(call):
    user_data = users.get(call.message.chat.id, {})
    request_text = (f"📌 Новая заявка!\n\n"
                    f"📞 Номер: {user_data.get('phone')}\n"
                    f"📍 Город: {user_data.get('city')}\n"
                    f"🏪 Магазин: {user_data.get('shop')}\n"
                    f"📦 Адрес: {user_data.get('address')}\n"
                    f"📝 Комментарий: {user_data.get('comment', 'Нет комментариев')}")
    
    target_channel = DUSHANBE_CHANNEL_ID if user_data.get('city') == 'Душанбе' else MAIN_CHANNEL_ID
    
    bot.send_message(target_channel, request_text)  
    bot.send_message(
        call.message.chat.id, 
        "Ваша заявка принята! ✅\nОжидайте, курьер скоро заберёт вашу посылку.", 
        reply_markup=get_start_keyboard()
    )

bot.polling(none_stop=True)
