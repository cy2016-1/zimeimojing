#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os,time,re
import sqlite3

root_path = os.path.abspath(os.path.dirname(__file__))

#文件夹授权执行方法  参数一 权限  参数二 位置
def cmd(permission , name):
    cmds = permission + " " + os.path.join(root_path, name)
    print(cmds)
    os.system(cmds)

# 创建新表
def CreateTables( db_arr = [] ):
    if len(db_arr) <= 0 :
        print( "创建失败" )
        return "创建失败"

    filename = time.strftime("%Y%m%d%H%M%S", time.localtime())
    old_data = os.path.join(root_path, 'python/data/config.db')
    mov_data = os.path.join(root_path, 'python/data/config_'+ str(filename) +'.db')
    os.system( 'sudo mv '+ old_data +' '+ mov_data )

    conn = sqlite3.connect(old_data)
    cur = conn.cursor()

    for item in db_arr:
        try:
            cur.execute(item)
        except sqlite3.Error as e:
            print( e )

    conn.commit()
    conn.close()
    os.system("sudo chmod 777 "+ old_data)

print("设置app目录下文件权限" )
#该文件仅执行
cmd("sudo chmod +x", 'app/moJing')

print('设置python目录下文件权限')
#该目录下全部仅执行
cmd('sudo chmod +x' , 'python/bin/*')

#创建所需目录
cmd('sudo mkdir -p','python/data/hecheng')
cmd('sudo mkdir -p','python/data/shijue')
cmd('sudo mkdir -p','python/data/yuyin')
cmd('sudo mkdir -p','python/data/conf')
cmd('sudo mkdir -p','python/data/snowboy')

cmd('sudo mkdir -p','python/runtime/log')

#该目录下全部权限
cmd('sudo chown -R pi.pi','python/data/')
cmd('sudo chmod -R 0777', 'python/data/')

#该目录下全部不可执行，可读可写
cmd('sudo chown -R pi.pi','python/runtime/')
cmd('sudo chmod -R 0777', 'python/runtime/')

#该目录下全部仅执行
cmd('sudo chmod +x' , 'python/api.py')
cmd('sudo chmod +x' , 'python/main.py')
cmd('sudo chmod +x' , 'python/run.py')
cmd('sudo chmod +x' , 'python/plugin.py')

'''
---------------------------------------------------------
* 以下是创建数据库内容，下面注释信息为定界符，不能修改！
---------------------------------------------------------
'''
create_table = []

#=[CreatedatabaseStart]=
create_table=['CREATE TABLE "config" ("key" TEXT(20),"value" TEXT(20),"nona" TEXT(200));', 'CREATE TABLE "nmap_config" ("key" TEXT(20),"value" TEXT(20),"nona" TEXT(200));', 'CREATE TABLE "nmap_mon" ("mac" TEXT(20) NOT NULL PRIMARY KEY,"ip" TEXT(15),"notename" TEXT(30),"up_time" TEXT(11),"is_online" INTEGER);', 'CREATE TABLE "nmap_mon_list" ("id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,"mac" TEXT(20),"up_time" TEXT(20),"jiange" INTEGER);', 'CREATE TABLE "nmap_online" ("mac" TEXT(20) NOT NULL PRIMARY KEY,"ip" TEXT(15),"name" TEXT(50),"notename" TEXT(50),"up_time" TEXT(11),"is_online" INTEGER);', 'CREATE TABLE "user_list" ("uid" integer NOT NULL PRIMARY KEY AUTOINCREMENT,"realname" TEXT,"gender" integer,"birthday" TEXT,"nickname" TEXT,"facepath" TEXT);']
#=[CreatedatabaseEnd]=

if len(create_table) > 0:
    CreateTables(create_table)


#设置新设备注册
cmd('sudo' , 'python/api.py online')

'''
------------------------------------------------------
* 管理计划任务
------------------------------------------------------
'''
def add_crontab():
    crontab = '/etc/crontab'
    f = open(crontab,"r")
    fstr = f.read()
    f.close()

    run_file = os.path.join(root_path, 'python/run.py')
    run_cmd = '*/1 * * * * pi export DISPLAY=:0 && '+ run_file  + " &" #必须加 & 不然计划任务失效     #每隔5分钟检测一次

    time_file = 'ntpdate ntp.sjtu.edu.cn'
    #每隔1小时检测一次
    times_cmd = "0 */1 * * * root "+ time_file + " &"

    wri_str = ''
    is_write = False
    matc = re.search( run_file, fstr, re.M|re.I )
    if matc==None:
        wri_str = "\n" + run_cmd
        is_write = True

    time_matc = re.search( time_file , fstr, re.M|re.I )
    if time_matc==None:
        wri_str += "\n" + times_cmd
        is_write = True

    if is_write:
        fo = open(crontab, "a+")
        fo.seek(0, 2)
        line = fo.write( "{0}{1}".format(wri_str,'\n') )
        print( line )
        fo.close()

    #===================================
    autostart = '/home/pi/.config/autostart'
    if os.path.exists(autostart) is False:
        #print('目录不存在')
        os.system('mkdir -p '+ autostart )

    start_mojing = os.path.join( autostart,'Start_Mojing.desktop')

    mojing_str  = '[Desktop Entry]\n'
    mojing_str += 'Type="Application"\n'
    mojing_str += 'Exec="'+ run_file +'"'

   # if os.path.isfile(start_mojing) is False:
        #print("无文件")
    with open(start_mojing, 'w') as fso:
        fso.write(mojing_str)


add_crontab()

'''
------------------------------------------------------
# 设置默认声卡
------------------------------------------------------
'''
def set_soundcard():
    alsa_conf = '/usr/share/alsa/alsa.conf'
    f = open(alsa_conf,"r")
    fstr = f.read()
    f.close()

    is_write = False
    restr = r'^defaults.ctl.card\s+0\s*$'
    matc = re.search( restr, fstr, re.M|re.I )
    if matc!=None:
        fstr = re.sub(restr, "defaults.ctl.card 1", fstr, 1, re.M|re.I )
        is_write = True

    restr = r'^defaults.pcm.card\s+0\s*$'
    matc = re.search( restr, fstr, re.M|re.I )
    if matc!=None:
        fstr = re.sub(restr, "defaults.pcm.card 1", fstr, 1, re.M|re.I )
        is_write = True

    if is_write:
        fo = open(alsa_conf, "w")
        line = fo.write( fstr )
        print( line )
        fo.close()

set_soundcard()

'''
------------------------------------------------------
# 设置摄像头
------------------------------------------------------
'''
def set_camera():
    config = '/boot/config.txt'
    f = open(config,"r")
    fstr = f.read()
    f.close()

    is_write = False
    restr = r'^start_x=1$'
    matc = re.search( restr, fstr, re.M|re.I )
    if matc==None:
        fstr += "\nstart_x=1"
        is_write = True

    restr = r'^gpu_mem=128$'
    matc = re.search( restr, fstr, re.M|re.I )
    if matc==None:
        fstr += "\ngpu_mem=128"
        is_write = True

    if is_write:
        fo = open(config, "w")
        line = fo.write( fstr )
        print( line )
        fo.close()


    fstr = ""
    #-----------------------------------
    conf = '/etc/modules-load.d/modules.conf'
    f = open(conf,"r")
    fstr = f.read()
    f.close()

    restr = r'^bcm2835-v4l2$'
    matc = re.search( restr, fstr, re.M|re.I )
    if matc==None:
        fo = open(conf, "a+")
        fo.seek(0, 2)
        line = fo.write('bcm2835-v4l2')
        print( line )
        fo.close()

set_camera()


'''
----------------清空处理-------------------
 new字典格式要求
 key=该文件绝对路径
 vealue=[文件名和后缀]列表内可以是多个文件名
-------------------------------------------
'''
def vacuuming():
    new = { os.path.join(root_path, "python/data/yuyin"):[
    "baidu_token.txt","baidu_renlian_shibie_token.txt",
    ]}

    for x in  new:
        for y in new[x]:
            A = x + "/" + y
            print("正在删除--->",A)
            try:
                os.remove(A)
            except:print("不存在")
            else:
                print("删除完成--->ok")

vacuuming()

'''
----------------关闭电脑屏保-------------------
#禁止屏保方法
-------------------------------------------
'''
def ban_screen_savers():
    with open("/etc/profile.d/Screen.sh","w") as x :
        x.write("xset dpms 0 0 0\nxset s off")
        print("关闭屏保完成")

ban_screen_savers()
'''
----------------校准时间-------------------
#校准时间的方法
-------------------------------------------
'''
def calibration_time():
    #需要安装包sudo apt-get install ntpdate

    # 时区判断
    if os.popen("date -R").read().count("0800") == 1:
        pass
    else:
        #修改时区到中国上海
        with open("/etc/timezone","w") as x:
            x.write('Asia/Shanghai')
     #在继续修改时间
    os.system("sudo ntpdate ntp.sjtu.edu.cn")
    print("核对时间完成")

calibration_time()
'''
----------------链接前后端-------------------
#链接前后端的方法
-------------------------------------------
'''
def set_js():
    conf_path = os.path.join( root_path,"app/resources/app/config.js")

    f = open(conf_path,"r")
    fstr = f.read()
    f.close()

    restr = r'const\s+rootpath\s*=\s*\'.+\';'
    matc = re.search( restr, fstr, re.M|re.I )
    if matc!=None:
        root_path2 = root_path
        if root_path2[-1:] != "/": root_path2 = root_path2 + "/"
        new_api = "const rootpath = '" +root_path2+ "';"
        fstr = re.sub(restr, new_api, fstr, 1, re.M|re.I )
        fo = open(conf_path, "w")
        line = fo.write( fstr )
        fo.close()
        print(fstr)

    print("链接前后端完成")
set_js()

print("全部完成*_^")

'''
----------------系统扩容-------------------

-------------------------------------------
'''

guandao ='''import os
print("d")
print("2")
print("n")
print("p")
print("2")
print(os.popen("sudo cat /sys/block/mmcblk0/mmcblk0p2/start").read()[:-1])
print("\\n",end='')
print("\\n",end='')
print("w")'''


kuorong = '''#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os

#检测文件是否存在
if os.path.exists("/kuorong.txt") == False:
    #设置分区
    os.system("sudo python3 /guandao.py | sudo fdisk /dev/mmcblk0")
    #创建文件，第二次开机就不会执行if语句
    os.system("sudo touch /kuorong.txt")
    #重启后设置生效
    os.system("sudo reboot")

#扩容指令
os.system("sudo resize2fs /dev/mmcblk0p2")
#删除执行脚本
os.system('sudo rm -r /kuorong.py')
#删除执行脚本
os.system('sudo rm -r /guandao.py')
#删除开机启动文件
os.system('sudo rm -r /home/pi/.config/autostart/kuorong.desktop')
#删除多余文件
os.system('sudo rm -r /kuorong.txt')'''

desktop= '''[Desktop Entry]
Type="Application"
Exec="/kuorong.py"'''

if input("是否执行系统空间最大化？(y/n)") =="y":
    #创建执行脚本
    with open ("/guandao.py","w") as x:
        x.write(guandao)
    #创建执行脚本
    with open ("/kuorong.py","w") as x:
        x.write(kuorong)
    #创建执行文件
    with open ("/home/pi/.config/autostart/kuorong.desktop","w") as x:
        x.write(desktop)
    #赋予执行权限
    os.system("sudo chmod +x /kuorong.py")
    print("系统空间最大化执行完成，重启生效")