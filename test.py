import requests
import os
import json
from test4 import *
import telebot

url = 'http://192.168.0.104'
save_dir = r'.\printer_data\gcodes'

headers_json = {"Content-Type": "application/json"}

def change_page_num_now(x):
    global page_number_now
    page_number_now = x

change_page_num_now(2)

printing_now = False
can_get_file = False
can_get_gcode  = False

MY_ID = 1626917666
API_TOKEN = '8108895059:AAEZ8B85efQFpCzSJXzHdAdYNPBlV8das70'
bot = telebot.TeleBot(API_TOKEN)

def login(func):
    def wrapper(message):
        if message.chat.id == MY_ID:
            func(message)
        else:
            bot.send_message(message.chat.id,'Не твой бот')
            bot.send_message(message.chat.id, 'Твой id если что: ' + str(message.chat.id))
    return wrapper

def get_name_photo_in_folder(folder_path):
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
    files = os.listdir(folder_path)
    for f in files:
        if f.lower().endswith(image_extensions):
            return f
    return None

def main_menu(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = telebot.types.KeyboardButton(text="Получить информацию о принтере")
    button2 = telebot.types.KeyboardButton(text="Экстреная остановка")
    button3 = telebot.types.KeyboardButton(text="Фото с камеры")
    button4 = telebot.types.KeyboardButton(text="Старт печати")
    button5 = telebot.types.KeyboardButton(text="Доп меню")
    keyboard.add(button1, button2, button3, button4, button5)
    bot.send_message(message.chat.id,'Добро пожаловать в бота для 3д принтера',reply_markup=keyboard)
    change_page_num_now(1)

def dop_menu(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_support = telebot.types.KeyboardButton(text="ф1")
    button1 = telebot.types.KeyboardButton(text="ф2")
    button2 = telebot.types.KeyboardButton(text="ф3")
    button3 = telebot.types.KeyboardButton(text="ф4")
    button4 = telebot.types.KeyboardButton(text="Назад")
    keyboard.add(button_support, button1, button2, button3, button4)
    bot.send_message(message.chat.id,'Доп меню',reply_markup=keyboard)
    change_page_num_now(2)

def start_print_menu(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = telebot.types.KeyboardButton(text="Загрузить файл")
    button2 = telebot.types.KeyboardButton(text="Выбрать файл")
    button3 = telebot.types.KeyboardButton(text="Назад")
    keyboard.add(button1, button2, button3)
    bot.send_message(message.chat.id,'Выберите опцию',reply_markup=keyboard)
    change_page_num_now(3)

def load_file_menu(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = telebot.types.KeyboardButton(text="Назад")
    keyboard.add(button1)
    bot.send_message(message.chat.id,'Отправте Gcode',reply_markup=keyboard)
    can_get_file = True
    change_page_num_now(4)

def choose_file_menu(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = telebot.types.KeyboardButton(text="Назад")
    keyboard.add(button1)
    gcode_list = json.loads(requests.get(url+'/server/files/list').text)['result']
    unsort_list = []
    result_str = ''
    for i in range(len(gcode_list)-1):
        unsort_list.append((gcode_list[i]['path'][:-6],gcode_list[i]['modified'],time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(gcode_list[i]['modified']))))
    global sort_list
    sort_list = sorted(unsort_list, key=lambda second: second[1])
    for iter in sort_list:
        result_str = result_str + str(iter[0]) + " " + str(iter[2]) +'\n'
    bot.send_message(message.chat.id,result_str)
    bot.send_message(message.chat.id,"Выберите модель и отправте её название",reply_markup=keyboard)
    change_page_num_now(5)
    
def printing_start(message):
    if checking_availability(message):
        #if 'ok' == json.loads(requests.post(url+f"/printer/print/start?filename={str(message.text)+'.gcode'}", headers = headers_json).text)['result']:
        bot.send_message(message.chat.id,'Печать была запущен')
        #else: bot.send_message(message.chat.id,'Ошибка')

def checking_availability(message):
    for i in range(len(sort_list)):
        if str(message.text) == sort_list[i][0]:
            return 1
    else:bot.send_message(message.chat.id,'Файл не был найден')

if page_number_now != 1:
    @bot.message_handler(commands=['help', 'start'])
    @login
    def welcome(message):
        print('start menu')
        change_page_num_now(1)
        main_menu(message)
        

@bot.message_handler()
@login
def get_printer_info(message):
    #print('пользователь прислал сообщение:')
    #print(message.text.lower())
    if message.text.lower() == 'получить информацию о принтере':
        #print('нажата кнопка получить информацию о принтере' )
        printer_info = json.loads(requests.get(url+'/printer/info').text)
        extruder = json.loads(requests.post(url+'/printer/objects/query',json={"objects": {"extruder": None}}, headers = headers_json).text)
        heater_bed = json.loads(requests.post(url+'/printer/objects/query',json={"objects": {"heater_bed": None}}, headers = headers_json).text)
        bot.send_message(message.chat.id, ('printer status: ' + str(printer_info['result']['state']) + '\n'
                                           + 'bed temp: '+ str(heater_bed['result']['status']['heater_bed']['temperature'])+ '\n'
                                           + 'bed tar: ' + str(heater_bed['result']['status']['heater_bed']['target']) + '\n'
                                           + 'ext temp: ' + str(extruder['result']['status']['extruder']['temperature']) + '\n'
                                           + 'ext temp: ' + str(extruder['result']['status']['extruder']['target'])))
        #idle_timeout print_stats
        if str(printer_info['result']['state']) == 'ready':
            printing_now = False
        elif str(printer_info['result']['state']) == 'ready':
            printing_now = True 
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

    elif message.text.lower() == 'старт печати': start_print_menu(message)
    elif message.text.lower() == 'доп меню': dop_menu(message)
    elif message.text.lower() == 'загрузить файл': load_file_menu(message)
    elif message.text.lower() == 'выбрать файл': choose_file_menu(message)
    elif message.text.lower() == 'назад':
        if page_number_now == 2: main_menu(message)
        elif page_number_now == 3: main_menu(message)
        elif page_number_now == 4: start_print_menu(message)
        elif page_number_now == 5: start_print_menu(message)
    elif page_number_now == 5 and message.text.lower() != 'назад':
        printing_start(message) 

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