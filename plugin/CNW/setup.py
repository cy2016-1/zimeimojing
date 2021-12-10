import os
import sys
import json

rootpath = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(rootpath)
os.chdir(rootpath)
from package.mylib import mylib

# 更新配置文件
config = mylib.getConfig()
config['LastDefaultPlugin'] = 'CNW'
config['ADMIN']['config'] = 'plugin/CNW/adminconfig.json'
config['LoadModular']['Screen'] = False
config['MQTT']['warp'] = 'plugin/CNW/mqtt'
config['MQTT']['server'] = '127.0.0.1'
config['MQTT']['clientid'] = 'Mojing'
config['MQTT']['mqttname'] = 'user'
config['MQTT']['mqttpass'] = '12345'

mylib.saveConfig(config)
print('设置系统配置成功！')

cmd = 'sudo cp -f /usr/share/rpd-wallpaper/fjord.jpg /usr/share/rpd-wallpaper/road.jpg'
os.system(cmd)
cmd = 'sudo cp -f /usr/share/rpd-wallpaper/raspberry-pi-logo.png /usr/share/plymouth/themes/pix/splash.png'
os.system(cmd)
print('设置系统桌面图片成功！')

admin_file = './webroot/admin/index.html'
admin_text = ''
with open(admin_file) as f:
    admin_text = f.read()

admin_text.replace(r'自美系统', '系统配置')

with open(admin_file, 'w') as fso:
    fso.write(admin_text)

chat_config_file = './plugin/Chat/config.json'
with open(chat_config_file) as f:
    chat_config = json.load(f)

chat_config['triggerwords'] = ["播放","天气"]

fw = open(chat_config_file,'w',encoding='utf-8')
json.dump(chat_config, fw, ensure_ascii=False, indent=4)
fw.close()
print('设置相关插件配置成功！')

