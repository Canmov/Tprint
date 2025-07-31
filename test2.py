import requests
import json
import pprint
import time
url = 'http://192.168.0.104'
#printer_info = json.loads(requests.get(url+'/printer/info').text)
#print(printer_info['result']['state'])## состояние принетра


headers_json = {"Content-Type": "application/json"}

#heater_bed1 = json.loads(requests.post(url+'/printer/objects/query',json={"objects": {"print_stats": None}}, headers = headers_json).text)
#print(heater_bed1['result'])#['status']['extruder']['temperature'])
#heater_bed2 = json.loads(requests.post(url+'/printer/objects/query',json={"objects": {"gcode_macro": None}}, headers = headers_json).text)
#print(heater_bed2['result'])#['status']['extruder']['temperature'])

#printer_status = json.loads(requests.post('http://192.168.0.104/printer/gcode/script',json={"script": "M140 S80"}).text)
#print(printer_status)
#time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(res[i]['modified']))

#heater_bed = json.loads(requests.post(url+'/printer/objects/query',json={"objects": {"idle_timeout": None}}, headers = headers_json).text)
#print(heater_bed['result']['status']['idle_timeout']['state'])
#print(heater_bed['result']['status']['idle_timeout']['printing_time'] / 60)

#heater_bed = json.loads(requests.post(url+'/printer/objects/query',json={"objects": {"virtual_sdcard": None}}, headers = headers_json).text)
#print(heater_bed['result']['status']['virtual_sdcard']['file_path'][31:])
#print(heater_bed['result']['status']['virtual_sdcard']['progress']*100)
#print(heater_bed['result']['status']['virtual_sdcard']['is_active'])

#print_stats = json.loads(requests.post(url+'/printer/objects/query',json={"objects": {"print_stats": None}}, headers = headers_json).text)
#print(print_stats['result']['status']['print_stats']['filename'])
#print(print_stats['result']['status']['print_stats']['total_duration']/60)
#print(print_stats['result']['status']['print_stats']['state'])
#print(time.strftime("%H:%M:%S", time.gmtime(print_stats['result']['status']['print_stats']['total_duration'])))
