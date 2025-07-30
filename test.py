import requests
import os
import json
from test4 import *
import telebot

url = 'http://192.168.0.104'
save_dir = r'.\printer_data\gcodes'

headers_json = {"Content-Type": "application/json"}

call_start_menu = False
can_get_file = False
can_get_gcode  = False

API_TOKEN = '8108895059:AAEZ8B85efQFpCzSJXzHdAdYNPBlV8das70'
bot = telebot.TeleBot(API_TOKEN)

def get_name_photo_in_folder(folder_path):
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
    files = os.listdir(folder_path)
    for f in files:
        if f.lower().endswith(image_extensions):
            return f
    return None

def start_menu(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_support = telebot.types.KeyboardButton(text="Получить информацию о принтере",)
    button1 = telebot.types.KeyboardButton(text="Экстреная остановка")
    button2 = telebot.types.KeyboardButton(text="Фото с камеры")
    button3 = telebot.types.KeyboardButton(text="Старт печати")
    button4 = telebot.types.KeyboardButton(text="Доп меню")
    keyboard.add(button_support, button1, button2, button3, button4)
    bot.send_message(message.chat.id,'Добро пожаловать в бота для 3д принтера',reply_markup=keyboard)
    call_start_menu == True

def dop_menu(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_support = telebot.types.KeyboardButton(text="ф1",)
    button1 = telebot.types.KeyboardButton(text="ф2")
    button2 = telebot.types.KeyboardButton(text="ф3")
    button3 = telebot.types.KeyboardButton(text="ф4")
    button4 = telebot.types.KeyboardButton(text="Назад")
    keyboard.add(button_support, button1, button2, button3, button4)
    bot.send_message(message.chat.id,'Доп меню',reply_markup=keyboard)
    call_start_menu == False
#@bot.message_handler()
#def get_printer_info(message):
#    if message.text.lower == 'Получить информацию о принтере':
#       print('нажата кнопка получить информацию о принтере' )
        #printer_info = requests.get(url+'/printer/info').text
        #bot.send_message(message.chat.id, printer_info) #общее состояние
        #heater_bed = json.loads(requests.post(url+'/printer/objects/query',json={"objects": {"heater_bed": None}}, headers = headers_json).text)
        #bot.send_message(message.chat.id, heater_bed['result']['status']['heater_bed']['temperature'])
        #bot.send_message(message.chat.id, heater_bed['result']['status']['heater_bed']['target'])
        #extruder = json.loads(requests.post(url+'/printer/objects/query',json={"objects": {"extruder": None}}, headers = headers_json).text)
        #bot.send_message(extruder['result']['status']['extruder']['temperature'])
        #bot.send_message(extruder['result']['status']['extruder']['target'])

if call_start_menu != True:
    @bot.message_handler(commands=['help', 'start'])
    def welcome(message):
        print('start menu')
        start_menu()

@bot.message_handler()
def get_printer_info(message):
    print('пользователь прислал сообщение:')
    print(message.text.lower())
    if message.text.lower() == 'получить информацию о принтере':
        print('нажата кнопка получить информацию о принтере' )
        printer_info = json.loads(requests.get(url+'/printer/info').text)
        bot.send_message(message.chat.id, printer_info['result']['state']) #общее состояние
        extruder = json.loads(requests.post(url+'/printer/objects/query',json={"objects": {"extruder": None}}, headers = headers_json).text)
        heater_bed = json.loads(requests.post(url+'/printer/objects/query',json={"objects": {"heater_bed": None}}, headers = headers_json).text)
        bot.send_message(message.chat.id, ('bed temp: '+ str(heater_bed['result']['status']['heater_bed']['temperature'])+ '\n'
                                           + 'bed tar: ' + str(heater_bed['result']['status']['heater_bed']['target']) + '\n'
                                           + 'ext temp: ' + str(extruder['result']['status']['extruder']['temperature']) + '\n'
                                           + 'ext temp: ' + str(extruder['result']['status']['extruder']['target'])))
        #idle_timeout print_stats

    elif message.text.lower() == 'экстреная остановка':
        get_statu_emergency_stop  = json.loads(requests.post(url+'/printer/emergency_stop').text)       
        bot.send_message(message.chat.id, get_statu_emergency_stop['result'])

    elif message.text.lower() == 'фото с камеры':
        #try:
        #    main_camera()
        #except Exception as e:
        #    bot.reply_to(message, f"Ошибка при сохранении файла: {e}")
        file_name = get_name_photo_in_folder('./')
        if file_name:
            print("Найден файл:", file_name)
            file_path  = './' + file_name
            try:
                with open(file_path, 'rb') as file:
                    bot.send_photo(message.chat.id, file)
                    time.sleep(3)
                #os.remove(file_path)
            except Exception as e:
                bot.send_message(message.chat.id, f"Ошибка при отправке файла: {e}")
        else:
            print("Фото в папке не найдено")

    elif message.text.lower() == 'доп меню':
        dop_menu(message)

if can_get_gcode == True:
    @bot.message_handler(commands=['home'])
    def gcode_g28(message): #паркует принтер
        requests.post(url+'/printer/gcode/script',json={"script": "G28"})
        bot.send_message(message.chat.id,'Printer go home')

if can_get_file == True:
    @bot.message_handler(content_types=['document'])
    def handle_gcode(message):
        try:
        # Получаем file_id и имя файла
            file_id = message.document.file_id
            filename = message.document.file_name

        # Получаем путь к файлу на серверах Telegram
            file_info = bot.get_file(file_id)
            file_path = file_info.file_path

        # Скачиваем файл
            downloaded_file = bot.download_file(file_path)

        # Путь сохранения (создадим папку, если её нет)
            save_dir = 'files'
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)

            full_path = os.path.join(save_dir, filename)

        # Сохраняем файл в бинарном режиме
            with open(full_path, 'wb') as new_file:
                new_file.write(downloaded_file)

            bot.reply_to(message, f"Файл сохранён: {full_path}")
        except Exception as e:
            bot.reply_to(message, f"Ошибка при сохранении файла: {e}")      

bot.infinity_polling()