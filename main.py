import requests
import os
import json
from adb_Tprint import *
import telebot
from cfg import * 
 
url = 'http://192.168.0.104'

save_dir_gcode = r'.\printer_data\gcodes'
save_dir_camera = r'./Camera'

headers_json = {"Content-Type": "application/json"}

def change_page_num_now(x):
    global page_number_now
    page_number_now = x

change_page_num_now('dop_menu')

printing_now = False
can_get_file = False
can_send_gcode  = False

MY_ID = my_id()
API_TOKEN = api_token()
bot = telebot.TeleBot(API_TOKEN)

def login(func):
    def wrapper(message):
        if message.chat.id == MY_ID:
            func(message)
        else:
            bot.send_message(message.chat.id,'Не твой бот')
            bot.send_message(message.chat.id, 'Твой id если что: ' + str(message.chat.id))
    return wrapper

#menu:
def main_menu(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = telebot.types.KeyboardButton(text="Получить информацию о принтере")
    button2 = telebot.types.KeyboardButton(text="Экстреная остановка")
    button3 = telebot.types.KeyboardButton(text="Фото с камеры")
    button4 = telebot.types.KeyboardButton(text="Старт печати")
    button5 = telebot.types.KeyboardButton(text="Доп меню")
    keyboard.add(button1, button2, button3, button4, button5)
    bot.send_message(message.chat.id,'Добро пожаловать в бота для 3д принтера',reply_markup=keyboard)
    change_page_num_now('main_menu')

def dop_menu(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = telebot.types.KeyboardButton(text="Проверить ADB")
    button2 = telebot.types.KeyboardButton(text="ф2")
    button3 = telebot.types.KeyboardButton(text="ф3")
    button4 = telebot.types.KeyboardButton(text="ф4")
    button5 = telebot.types.KeyboardButton(text="Назад")
    keyboard.add(button1, button2, button3, button4, button5)
    bot.send_message(message.chat.id,'Доп меню',reply_markup=keyboard)
    change_page_num_now('dop_menu')

def start_print_menu(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = telebot.types.KeyboardButton(text="Загрузить файл")
    button2 = telebot.types.KeyboardButton(text="Выбрать файл")
    button3 = telebot.types.KeyboardButton(text="Назад")
    keyboard.add(button1, button2, button3)
    bot.send_message(message.chat.id,'Выберите опцию',reply_markup=keyboard)
    change_page_num_now('start_print_menu')

def load_file_menu(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = telebot.types.KeyboardButton(text="Назад")
    keyboard.add(button1)
    bot.send_message(message.chat.id,'Отправте Gcode',reply_markup=keyboard)
    can_get_file = True
    change_page_num_now('load_file_menu')

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
    change_page_num_now('choose_file_menu')

#функции:    
def printing_start(message):
    if checking_availability(message):
        if 'ok' == json.loads(requests.post(url+f"/printer/print/start?filename={str(message.text)+'.gcode'}", headers = headers_json).text)['result']:
            bot.send_message(message.chat.id,'Печать была запущена')
            main_menu(message)
        else: bot.send_message(message.chat.id,'Ошибка')

def checking_availability(message):
    for i in range(len(sort_list)):
        if str(message.text) == sort_list[i][0]:
            return 1
    else:bot.send_message(message.chat.id,'Файл не был найден')
 
def emergency_stop(message):
    get_statu_emergency_stop  = json.loads(requests.post(url+'/printer/emergency_stop').text)       
    bot.send_message(message.chat.id, get_statu_emergency_stop['result'])

def get_name_photo_in_folder(folder_path):
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
    files = os.listdir(folder_path)
    for f in files:
        if f.lower().endswith(image_extensions):
            return f
    return None

def send_photo_by_printer(message):
    try:
        main_camera()
    except Exception as e:
        bot.reply_to(message, f"Ошибка при сохранении файла: {e}")
    file_name = get_name_photo_in_folder(save_dir_camera)
    if file_name:
        print("Найден файл:", file_name)
        file_path_img  = save_dir_camera + f'/{file_name}'
        try:
            with open(file_path_img, 'rb') as file:
                bot.send_photo(message.chat.id, file)
                time.sleep(3)
            os.remove(file_path_img)
        except Exception as e:
            bot.send_message(message.chat.id, f"Ошибка при отправке файла: {e}")
    else:
        print("Фото в папке не найдено")

#Обработка сообщений от пользлвателя
if page_number_now != 'main_menu':
    @bot.message_handler(commands=['help', 'start'])
    @login
    def welcome(message):
        change_page_num_now('main_menu')
        main_menu(message)
        

@bot.message_handler()
@login
def take_message(message):
    if message.text.lower() == 'получить информацию о принтере':
        
        kiliper_state = json.loads(requests.get(url+'/printer/info').text)
        extruder = json.loads(requests.post(url+'/printer/objects/query',json={"objects": {"extruder": None}}, headers = headers_json).text)
        heater_bed = json.loads(requests.post(url+'/printer/objects/query',json={"objects": {"heater_bed": None}}, headers = headers_json).text)
        print_stats = json.loads(requests.post(url+'/printer/objects/query',json={"objects": {"print_stats": None}}, headers = headers_json).text)
        virtual_sdcard = json.loads(requests.post(url+'/printer/objects/query',json={"objects": {"virtual_sdcard": None}}, headers = headers_json).text)

        printer_state = print_stats['result']['status']['print_stats']['state'] 

        printing_model = None
        printing_percent = None
        time_for_complete = None #8 минуты нагрев добавить, ограничить если отрицательно 
        total_time_printing_unix = print_stats['result']['status']['print_stats']['total_duration']
        total_time_printing = time.strftime("%H:%M:%S", time.gmtime(total_time_printing_unix))

        str_message_for_user = ''

        if printer_state == 'complete':
            printing_now = False
            printer_state_message = 'Принтер закончил печать \nПечать составила: ' + str(total_time_printing)
            printing_model = print_stats['result']['status']['print_stats']['filename'] + '\n'
            str_message_for_user = str_message_for_user + printing_model

        elif printer_state == 'standby':
            printing_now = False
            printer_state_message = 'Принтер ожидает начала печати'

        elif printer_state == 'printing':
            printing_now = True
            printer_state_message = 'Принтер в процессе печати \nПечать идёт: ' + str(total_time_printing)
            printing_model = print_stats['result']['status']['print_stats']['filename'] + '\n'
            printing_percent = str(virtual_sdcard['result']['status']['virtual_sdcard']['progress']*1000//10) + '%' + '\n'
            metadata_gcode_unix = json.loads(requests.get(url+'/server/files/metadata?filename='+ printing_model).text)['result']['estimated_time']
            time_for_complete = str(time.strftime("%H:%M:%S", time.gmtime(metadata_gcode_unix - total_time_printing_unix))) + '\n'
            str_message_for_user = str_message_for_user + printing_model + 'Процентов напечатано: ' + printing_percent + 'Время до завершения: ' + time_for_complete

        elif printer_state == 'paused':
            printing_now = True
            printer_state_message = 'Печать поставлена на паузу \nПечать шла: ' + str(total_time_printing)
            printing_model = print_stats['result']['status']['print_stats']['filename'] + '\n'
            printing_percent = str(virtual_sdcard['result']['status']['virtual_sdcard']['progress']*1000//10) + '%' + '\n'
            metadata_gcode_unix = json.loads(requests.get(url+'/server/files/metadata?filename='+ printing_model).text)['result']['estimated_time']
            time_for_complete = str(time.strftime("%H:%M:%S", time.gmtime(metadata_gcode_unix - total_time_printing_unix))) + '\n'
            str_message_for_user = str_message_for_user + printing_model + 'Процентов напечатано: ' + printing_percent + 'Время до завершения: ' + time_for_complete

        elif printer_state == 'error':
            printing_now = True
            printer_state_message = 'Ошибка печати модели'
            printing_model = print_stats['result']['status']['print_stats']['filename'] + '\n'
            str_message_for_user = str_message_for_user + printing_model
        
        bot.send_message(message.chat.id, (printer_state_message + '\n'
                                           + str_message_for_user
                                           + 'Температура стола: '+ str(heater_bed['result']['status']['heater_bed']['temperature'])+ 'C ==> '
                                           + str(heater_bed['result']['status']['heater_bed']['target']) + 'C' + '\n'
                                           + 'Температура экструдера: ' + str(extruder['result']['status']['extruder']['temperature']) + 'C ==>'
                                           + str(extruder['result']['status']['extruder']['target']) + 'C' ))

    elif message.text.lower() == 'экстреная остановка':emergency_stop(message)
    elif message.text.lower() == 'фото с камеры':send_photo_by_printer(message)
    elif message.text.lower() == 'старт печати': start_print_menu(message)
    elif message.text.lower() == 'доп меню': dop_menu(message)
    elif message.text.lower() == 'загрузить файл': load_file_menu(message)
    elif message.text.lower() == 'выбрать файл': choose_file_menu(message)
    elif message.text.lower() == 'назад':
        if page_number_now == 'dop_,menu': main_menu(message)
        elif page_number_now == 'start_print_menu': main_menu(message)
        elif page_number_now == 'load_menu': 
            start_print_menu(message)
            can_get_file = False
        elif page_number_now == 'choose_file_menu': start_print_menu(message)
    elif page_number_now == 'choose_file_menu' and message.text.lower() != 'назад': printing_start(message) 
    elif page_number_now == 'dop_menu' and message.text.lower() == 'проверить ADB': bot.send_message(message.chat.id, check_devices()) 

if can_send_gcode == True:
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
            file_path_gcode = file_info.file_path

        # Скачиваем файл
            downloaded_file = bot.download_file(file_path_gcode)

        # Путь сохранения (создадим папку, если её нет)
            if not os.path.exists(save_dir_gcode):
                os.makedirs(save_dir_gcode)

            full_path = os.path.join(save_dir_gcode, filename)

        # Сохраняем файл в бинарном режиме
            with open(full_path, 'wb') as new_file:
                new_file.write(downloaded_file)

            bot.reply_to(message, f"Файл сохранён: {full_path}")
            start_print_menu(message)
        except Exception as e:
            bot.reply_to(message, f"Ошибка при сохранении файла: {e}")      

bot.infinity_polling()