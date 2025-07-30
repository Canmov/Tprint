import requests
import json
import pprint
url = 'http://192.168.0.104'
printer_info = json.loads(requests.get(url+'/printer/info').text)
print(printer_info['result']['state'])## состояние принетра


headers_json = {"Content-Type": "application/json"}
heater_bed = json.loads(requests.post(url+'/printer/objects/query',json={"objects": {"idle_timeout": None}}, headers = headers_json).text)
print(heater_bed['result'])#['status']['extruder']['temperature'])
heater_bed1 = json.loads(requests.post(url+'/printer/objects/query',json={"objects": {"print_stats": None}}, headers = headers_json).text)
print(heater_bed1['result'])#['status']['extruder']['temperature'])
#heater_bed2 = json.loads(requests.post(url+'/printer/objects/query',json={"objects": {"gcode_macro": None}}, headers = headers_json).text)
#print(heater_bed2['result'])#['status']['extruder']['temperature'])

#printer_info1 = json.loads(requests.get(url+'/server/files/list').text)
#pprint.pprint(printer_info1) #инфа о моделях

#printer_status = json.loads(requests.post('http://192.168.0.104/printer/gcode/script',json={"script": "M140 S80"}).text)
#print(printer_status)
