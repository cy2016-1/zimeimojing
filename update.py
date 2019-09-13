#!/usr/bin/env python3
import os,time,re
import subprocess

if int(os.popen("id -u").read()) !=0:
    print("请用root权限执行：sudo ./update.py")
    exit()

#当前运行系统目录
THIS_DIR = os.getcwd()

#系统根目录
SYSTEM_ROOT = os.path.abspath(os.path.dirname(THIS_DIR))

#升级目录
UPDATE_DIR = os.path.join( SYSTEM_ROOT, 'update')

#升级库URL
GITEE_URL = 'https://gitee.com/kxdev/zimeimojing.git'

'''
富文本提示
    tistr   --  提示字符串
    status  --  状态码
        w --  警告（红底白字）
        n --  正常（黑底白字）
        p --  提示（绿底白字）
    ln      -- 是否换行（不为空则不换行，默认空，换行）
'''
def print_str( tistr = '', status = 'n', ln = ''):
    ti_str = tistr
    if status=='w':
        ti_str = '\033[41m{0}\033[0m'.format(ti_str)
    elif status=='p':
        ti_str = '\033[42m{0}\033[0m'.format(ti_str)
    if len(ln)>0:
        print(ti_str, end='')
    else:
        print(ti_str)

def menu():
    tishi  = "┏━━━━━━☆ ★ ☆ 欢迎使用自美系统在线升级工具 ☆ ★ ☆ ━━━━━━┓\n"
    tishi += "┃1、查看官方最新版本号                                ┃\n"
    tishi += "┃2、查看本地版本号                                    ┃\n"
    tishi += "┃3、一键检测并升级系统                                ┃\n"
    tishi += "┃4、退出                                              ┃\n"
    tishi += "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
    tishi += "直接输入操作命令前面的数字序号（回车）:"

    os.system('clear')
    a = input(tishi)
    if a == "1":
        menu_ckver('git')
        return menu()
    elif a == "2":
        menu_ckver('local')
        return menu()
    elif a == "3":
        menu_startup()
        return menu()
    elif a == "4":
        exit()
    else:
        return menu()

#比较版本号
def versionCompare(v1="1.1.1", v2="1.2"):
    v1 = re.sub(r'^\D', "", v1)
    v2 = re.sub(r'^\D', "", v2)
    v1_check = re.match("\d+(\.\d+){0,2}", v1)
    v2_check = re.match("\d+(\.\d+){0,2}", v2)
    if v1_check is None or v2_check is None or v1_check.group() != v1 or v2_check.group() != v2:
        return -2   #"版本号格式不对，正确的应该是x.x.x,只能有3段"
    v1_list = v1.split(".")
    v2_list = v2.split(".")
    v1_len = len(v1_list)
    v2_len = len(v2_list)
    if v1_len > v2_len:
        for i in range(v1_len - v2_len):
            v2_list.append("0")
    elif v2_len > v1_len:
        for i in range(v2_len - v1_len):
            v1_list.append("0")
    else:
        pass
    for i in range(len(v1_list)):
        if int(v1_list[i]) > int(v2_list[i]):
            return -1
        if int(v1_list[i]) < int(v2_list[i]):
            return 1
    return 0

#运行git命令
def run_gitcmd( cmd, osrun='popen' ):
    cmd = 'cd '+ UPDATE_DIR +'\n'+cmd
    if osrun == 'system':
        cmd += ' > /dev/null 2>&1'
        os.system( cmd )
    else:
        out = os.popen(cmd).read()
        return out

#获取Git最新的版本
def get_new_ver():
    git_tag = 'git tag -l'      #显示标签
    git_ver_line = run_gitcmd( git_tag )
    git_newver = git_ver_line.splitlines()[-1]
    return git_newver

#获取本地版本号
def get_local_ver():
    this_verfile = os.path.join(THIS_DIR, 'python/data/ver.txt')
    file_ver = ""
    if os.path.exists(this_verfile):
        fo = open(this_verfile, "r+")
        file_ver = fo.read(-1)
        fo.close()

    return file_ver

#下载新的文件
def down_newfile():
    print_str('正在获取远程系统文件……','n','n')
    git_cmd = ''
    if os.path.exists( os.path.join( UPDATE_DIR, '.git') ):
        git_cmd = 'git pull'        #拉取
    else:
        git_cmd = 'git clone '+ GITEE_URL +' '+ UPDATE_DIR

    if git_cmd:
        run_gitcmd( git_cmd, 'system' )
        time.sleep(1)

    git_newver = get_new_ver()      #获取最新的发行版本

    #切换到最新发行版本
    git_cmd = 'git checkout '+ str(git_newver)
    run_gitcmd( git_cmd, 'system' )

    #将最新的版本号写入ver.txt文件中
    up_verfile = os.path.join(UPDATE_DIR, 'python/data/ver.txt')
    fo = open(up_verfile, "w+")
    fo.write(git_newver)
    fo.close()

    print_str('[完成]','p')


#迁移目录
def move_dir():
    if os.path.exists(UPDATE_DIR):
        datetime = time.strftime("%Y%m%d%H%M%S", time.localtime())
        back_path = THIS_DIR +'_'+str(datetime)

        print_str('备份原系统至'+back_path,'n','n')

        cmd = 'sudo mv '+ THIS_DIR +' '+ back_path
        os.system( cmd )

        print_str('[完成]','p')

        print_str('开始部署新系统，请稍候……（这里可能需要几分钟时间）','n','n')
        cmd = 'sudo cp -rf '+ UPDATE_DIR +' '+ THIS_DIR
        os.system( cmd )

        print_str('[完成]','p')

        return True
    else:
        return False

'''
 比较版本
 返回：
    True    --    需要更新
    False   --    不需要
'''
def diff_ver():
    git_newver = get_new_ver()      #获取最新的发行版本

    file_ver = get_local_ver()      #获取本地版本号

    if file_ver:
        print_str('当前系统版本号-->'+ file_ver)
        print_str('官方最新版本号-->'+ git_newver)

        diffver = versionCompare( file_ver, git_newver )
        if diffver > 0:
            print_str('官方最新版本高于当前版本，需要升级！','w')
            return True
        else:
            print_str('当前系统版本已经是最新版本，无需升级！','p')
            return False
    else:
        print_str('当前系统版本文件丢失，需更新升级！','w')
        #没有版本文件，默认即将更新的版本大于当前版本
        return True

#查看版本号
def menu_ckver( ty = 'git' ):
    down_newfile()

    if ty=='git':
        git_newver = get_new_ver()      #获取最新的发行版本
        print_str('官方最新版本号-->'+ git_newver,'w')
    if ty=='local':
        file_ver = get_local_ver()      #获取本地版本号
        print_str('当前系统版本号-->'+ file_ver,'p')
    time.sleep(5)


#开始升级
def menu_startup():
    down_newfile()
    is_up = diff_ver()
    if is_up is True:
        opis = move_dir()
        if opis:
            print_str('新版本文件环境部署完成！','p')
            print_str('开始准备安装！')

            os.system('sudo python3 '+ THIS_DIR +'/install.py update')

            print_str('新系统安装成功，即将重启设备！','p')

    time.sleep(5)

menu()