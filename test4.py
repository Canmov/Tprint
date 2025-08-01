import subprocess
import time

print_action = True

def run_adb_command(command):
    if command[0] == 'adb':
        adb_path = r"/usr/lib/android-sdk/platform-tools/adb"  # укажите путь к adb
        full_command = [adb_path] + command[1:]
    else:
        full_command = command
    result = subprocess.run(full_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,)
    return result.stdout, result.stderr, result.returncode

def check_devices():
      stdout = run_adb_command(['adb', 'devices'])
      time.sleep(1)
      return stdout 

def on_or_off_disply():
      stdout, stderr, code = run_adb_command(['adb', 'shell','input','keyevent', '26'])
      time.sleep(3)
      if code == 0 and print_action:
            print('Disply switch')
      else:print("Error:", stderr)

def use_camera_key():
      stdout, stderr, code = run_adb_command(['adb', 'shell','input','keyevent', 'camera_key'])
      time.sleep(3)
      if code == 0 and print_action:
            print('App camera stared')
      else:print("Error:", stderr)

def take_photo():
      stdout, stderr, code = run_adb_command(['adb', 'shell','input','keyevent', '27'])
      time.sleep(3)
      if code == 0 and print_action:
            print('Photo saved')
      else:print("Error:", stderr)

def pull_photo():
      stdout, stderr, code = run_adb_command(['adb','pull', '/sdcard/DCIM/Camera'])
      time.sleep(3)
      if code == 0 and print_action:
            print('Pull successfully')
      else:print("Error:", stderr)

def cleansing_folder_camera():
      stdout, stderr, code = run_adb_command(['adb', 'shell','rm','-r','/sdcard/DCIM/Camera/*'])
      time.sleep(3)
      if code == 0 and print_action:
            print('Clean successfully')
      else:print("Error:", stderr)

def main_camera():
      on_or_off_disply()
      use_camera_key()
      take_photo()
      pull_photo()
      cleansing_folder_camera()
      on_or_off_disply()