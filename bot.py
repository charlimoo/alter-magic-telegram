import telebot
import requests
from telebot import types # import types for inline buttons
from config import TELEGRAM_BOT_TOKEN, workflows
from image_processor import get_prompt, save_image


import time
import json

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

user_data = {}

messages = json.loads(open("messages.json", encoding="utf-8").read())
m_start = str(messages['start'])
m_workflow = str(messages['workflow'])
m_category = str(messages['category'])
m_style = str(messages['style'])
m_wait = str(messages['wait'])
m_lost = str(messages['lost'])
m_help = str(messages['help'])
m_about = str(messages['about'])
m_community = str(messages['community'])
m_channel = str(messages['channel'])

def check_server():
  try:
    from config import srvadd
    response = requests.get("http://" + srvadd)
    if response.status_code == 200:
      return "Server is up!"
    else:
      return "Server returned status code %s" % response.status_code
  except:
    return "Server is down!"

def show_server_status(message):
  status = check_server()
  bot.send_message(message.chat.id, status)

@bot.message_handler(content_types=['text'])
def handle_text(message):
  if message.text == '💻 Server Status':
    show_server_status(message)
  elif message.text.startswith('http://') or message.text.startswith('https://'):
    new_address = message.text
    new_address = new_address.replace('http://', '')
    new_address = new_address.replace('https://', '')
    new_address = new_address.replace('/', '')
    import config
    config.modify_server(new_address)
    bot.send_message(message.chat.id, "Server address updated!")
  elif message.text == "serverurl":
    from config import srvadd
    bot.send_message(message.chat.id, srvadd)
  else:
    bot.send_message(message.chat.id, m_lost)



@bot.message_handler(func=lambda message: message.text == '🆘 Help')
def handle_button_1(message):
    # Do something
    bot.send_message(message.chat.id, m_help)

# Handle button 2 press  
@bot.message_handler(func=lambda message: message.text == '🙂 About')
def handle_button_2(message):
    # Do something else
    bot.send_message(message.chat.id, m_about)

@bot.message_handler(func=lambda message: message.text == '🤟 Join Community')
def handle_button_2(message):
    # Do something else
    bot.send_message(message.chat.id, m_community)

@bot.message_handler(func=lambda message: message.text == '💡 Telegram channel For Updates')
def handle_button_2(message):
    # Do something else
    bot.send_message(message.chat.id, m_channel)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(telebot.types.KeyboardButton('🆘 Help'), telebot.types.KeyboardButton('🙂 About'))
    keyboard.row(telebot.types.KeyboardButton('💻 Server Status'), telebot.types.KeyboardButton('🤟 Join Community'))
    keyboard.row(telebot.types.KeyboardButton('💡 Telegram channel For Updates'))

    bot.reply_to(message, m_start, reply_markup=keyboard)
    user_data[message.chat.id] = {}

@bot.message_handler(content_types=['photo']) 
def handle_photo(message):
    try:
        user_data[message.chat.id] = {}
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        img_name = f"{message.chat.id}_{time.time()}.jpg"
        img_path = save_image(downloaded_file, img_name)
        user_data[message.chat.id]['img_name'] = img_name
        user_data[message.chat.id]['img_path'] = img_path
        keyboard = types.InlineKeyboardMarkup()
        for workflow in workflows['workflows']:
            callback_data = workflow['name'] 
            keyboard.add(types.InlineKeyboardButton(text=workflow['name'], callback_data=callback_data))
        bot.send_message(message.chat.id, m_workflow, reply_markup=keyboard)
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, "couldn't get image, would you send it again? or another time i guess..")
    # create inline keyboard with workflow buttons

@bot.callback_query_handler(func=lambda call: call.data in [workflow['name'] for workflow in workflows['workflows']])
def workflow_chosen(call):
    user_data[call.message.chat.id]['workflow'] = call.data
    # create inline keyboard with category buttons
    keyboard = types.InlineKeyboardMarkup()
    workflow = next(w for w in workflows['workflows'] if w['name'] == call.data)
    for category in workflow['categories']:
        callback_data = category['name']
        keyboard.add(types.InlineKeyboardButton(text=category['name'], callback_data=callback_data))

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=m_category, reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data in [category['name'] for workflow in workflows['workflows'] for category in workflow['categories']])
def category_chosen(call):
    user_data[call.message.chat.id]['category'] = call.data
    
    keyboard = types.InlineKeyboardMarkup()
    workflow = next(w for w in workflows['workflows'] if w['name'] == user_data[call.message.chat.id]['workflow'])
    category = next(c for c in workflow['categories'] if c['name'] == call.data)

    for style in category['styles']:
        callback_data = style['name']
        keyboard.add(types.InlineKeyboardButton(text=style['name'], callback_data=callback_data))
    
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=m_style, reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data in [style['name'] for workflow in workflows['workflows'] for category in workflow['categories'] for style in category['styles']])
def style_chosen(call):
    user_data[call.message.chat.id]['style'] = call.data
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=m_wait)
    userprompt = get_prompt(user_data[call.message.chat.id]['workflow'], user_data[call.message.chat.id]['category'], user_data[call.message.chat.id]['style'])
    try:
        from engine import engine
        from config import srvadd
        img = engine(
            user_data[call.message.chat.id]['workflow'],
            user_data[call.message.chat.id]['img_path'],
            user_data[call.message.chat.id]['img_name'],
            userprompt,srvadd)
        bot.send_photo(call.message.chat.id, img)
    except:
        bot.send_message(call.message.chat.id, "Looks like the server is down?")
    user_data[call.message.chat.id] = {}



bot.polling()