#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os,re,time
#旋转屏幕函数
#无论有没有发现display_rotate都返回没有改关键语句的原句回来  "data"就是参数
def p360():
    try:
        with open("/boot/config.txt","r") as x:
            #定义列表容器
            new_data=[]
            #获取原始内容
            data = x.read()
            #把原始内容添加到容器
            new_data.append(data)
            #把容器内容转字符串
            data_x = "".join(new_data)
            #定义检测语句'^display_rotate=(\d)'
            txt  = 'display_rotate='
            #data_x内查找字符位置
            data_y = re.search(txt, data_x).span()[0]
            #因为找到了所以去掉之前的display_rotate记录
            data_have = data_x[:data_y]
            #在记录display_rotate后面行数内容
            data_next = data_x[data_y+len(txt)+1:]
            #返回的就是"txt"剥离display_rotate 的原句,"data"就是参数
            return {"txt":data_have + data_next ,"data":data_x[data_y+len(txt):][0]}
    except:
        #检测不到关键词就会报错  直接返回原句
        return {"txt": data_x ,"data": "0"}

def main(have = p360()):
    if have:
        data = int(have["data"])
        if data == 3:data = 0
        else :data += 1

        txt = have["txt"]
        if have["txt"][-2:] == "\n\n":
            #发现原文的最后有2个空格以后就依次删除空格,因为我们的语句是写在最后的
            txt = have["txt"][:-1]

        with open("/boot/config.txt","w") as y:
            y.write(txt+"\ndisplay_rotate="+str(data))
            y.close()

        os.system("sudo reboot")


if __name__ == '__main__':
    main()


'''
display_rotate=0                   不旋转
Normal display_rotate=1            转90
degrees display_rotate=2           转180
degrees display_rotate=3           转270

dtparam=i2c_arm=on
dtoverlay=i2s-mmap
start_x=1
gpu_mem=128
display_rotate=1

'''
